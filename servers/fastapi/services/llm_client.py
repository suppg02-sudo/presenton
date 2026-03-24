import asyncio
import dirtyjson
import json
import logging
import time
from typing import AsyncGenerator, List, Optional
from fastapi import HTTPException
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk as OpenAIChatCompletionChunk,
)
from google import genai
from google.genai.types import Content as GoogleContent, Part as GoogleContentPart
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    ToolConfig as GoogleToolConfig,
    FunctionCallingConfig as GoogleFunctionCallingConfig,
    FunctionCallingConfigMode as GoogleFunctionCallingConfigMode,
)
from google.genai.types import Tool as GoogleTool
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage
from anthropic import MessageStreamEvent as AnthropicMessageStreamEvent
from enums.llm_provider import LLMProvider
from models.llm_message import (
    AnthropicAssistantMessage,
    AnthropicUserMessage,
    GoogleAssistantMessage,
    GoogleToolCallMessage,
    OpenAIAssistantMessage,
    LLMMessage,
    LLMSystemMessage,
    LLMUserMessage,
)
from models.llm_tool_call import (
    AnthropicToolCall,
    GoogleToolCall,
    LLMToolCall,
    OpenAIToolCall,
    OpenAIToolCallFunction,
)
from models.llm_tools import LLMDynamicTool, LLMTool
from services.llm_tool_calls_handler import LLMToolCallsHandler
# Metrics service - disabled for now due to import issues
# from services.metrics_service import store_metric_async, initialize_metrics_table


# Stub functions to prevent import errors
async def store_metric_async(**kwargs):
    """Stub function - metrics collection disabled"""
    pass


async def initialize_metrics_table():
    """Stub function - metrics initialization disabled"""
    pass


from utils.async_iterator import iterator_to_async
from utils.dummy_functions import do_nothing_async
from utils.get_env import (
    get_anthropic_api_key_env,
    get_custom_llm_api_key_env,
    get_custom_llm_url_env,
    get_disable_thinking_env,
    get_google_api_key_env,
    get_ollama_url_env,
    get_openai_api_key_env,
    get_tool_calls_env,
    get_web_grounding_env,
)
from utils.llm_provider import get_llm_provider, get_model
from utils.parsers import parse_bool_or_none
from utils.schema_utils import (
    ensure_strict_json_schema,
    flatten_json_schema,
    remove_titles_from_schema,
)

# Monitoring and rate limiting
from utils.rate_limiter import (
    wait_if_rate_limited,
    handle_rate_limit_error,
    is_rate_limited,
)
from utils.request_queue import enqueue_request
from utils.quota_monitor import record_request, record_rate_limit, record_error
from utils.model_monitor import (
    record_model_success,
    record_model_failure,
    should_rotate_model,
)

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.llm_provider = get_llm_provider()
        self._client = self._get_client()
        self.tool_calls_handler = LLMToolCallsHandler(self)
        # Initialize metrics table on first import
        try:
            asyncio.create_task(initialize_metrics_table())
        except Exception as e:
            logger.warning(f"Failed to initialize metrics table: {str(e)}")

    # ? Use tool calls
    def use_tool_calls_for_structured_output(self) -> bool:
        if self.llm_provider != LLMProvider.CUSTOM:
            return False
        return parse_bool_or_none(get_tool_calls_env()) or False

    # ? Web Grounding
    def enable_web_grounding(self) -> bool:
        if (
            self.llm_provider == LLMProvider.OLLAMA
            or self.llm_provider == LLMProvider.CUSTOM
        ):
            return False
        return parse_bool_or_none(get_web_grounding_env()) or False

    # ? Disable thinking
    def disable_thinking(self) -> bool:
        return parse_bool_or_none(get_disable_thinking_env()) or False

    # ? Clients
    def _get_client(self):
        match self.llm_provider:
            case LLMProvider.OPENAI:
                return self._get_openai_client()
            case LLMProvider.GOOGLE:
                return self._get_google_client()
            case LLMProvider.ANTHROPIC:
                return self._get_anthropic_client()
            case LLMProvider.OLLAMA:
                return self._get_ollama_client()
            case LLMProvider.CUSTOM:
                return self._get_custom_client()
            case _:
                raise HTTPException(
                    status_code=400,
                    detail="LLM Provider must be either openai, google, anthropic, ollama, or custom",
                )

    def _get_openai_client(self):
        if not get_openai_api_key_env():
            raise HTTPException(
                status_code=400,
                detail="OpenAI API Key is not set",
            )
        return AsyncOpenAI()

    def _get_google_client(self):
        if not get_google_api_key_env():
            raise HTTPException(
                status_code=400,
                detail="Google API Key is not set",
            )
        return genai.Client()

    def _get_anthropic_client(self):
        if not get_anthropic_api_key_env():
            raise HTTPException(
                status_code=400,
                detail="Anthropic API Key is not set",
            )
        return AsyncAnthropic()

    def _get_ollama_client(self):
        return AsyncOpenAI(
            base_url=(get_ollama_url_env() or "http://localhost:11434") + "/v1",
            api_key="ollama",
        )

    def _get_custom_client(self):
        if not get_custom_llm_url_env():
            raise HTTPException(
                status_code=400,
                detail="Custom LLM URL is not set",
            )
        return AsyncOpenAI(
            base_url=get_custom_llm_url_env(),
            api_key=get_custom_llm_api_key_env() or "null",
        )

    # ? Prompts
    def _get_system_prompt(self, messages: List[LLMMessage]) -> str:
        for message in messages:
            if isinstance(message, LLMSystemMessage):
                return message.content
        return ""

    def _get_google_messages(self, messages: List[LLMMessage]) -> List[GoogleContent]:
        contents = []
        for message in messages:
            if isinstance(message, LLMUserMessage):
                contents.append(
                    GoogleContent(
                        role=message.role,
                        parts=[GoogleContentPart(text=message.content)],
                    )
                )
            elif isinstance(message, GoogleAssistantMessage):
                contents.append(message.content)
            elif isinstance(message, GoogleToolCallMessage):
                contents.append(
                    GoogleContent(
                        role="user",
                        parts=[
                            GoogleContentPart.from_function_response(
                                name=message.name,
                                response=message.response,
                            )
                        ],
                    )
                )

        return contents

    def _get_anthropic_messages(self, messages: List[LLMMessage]) -> List[LLMMessage]:
        return [
            message for message in messages if not isinstance(message, LLMSystemMessage)
        ]

    # ? Generate Unstructured Content
    async def _generate_openai(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        extra_body: Optional[dict] = None,
        depth: int = 0,
    ) -> str | None:
        client: AsyncOpenAI = self._client
        start_time = time.time()

        # Check and handle rate limiting (only at depth 0)
        if depth == 0:
            was_rate_limited = await wait_if_rate_limited()
            if was_rate_limited:
                logger.info(
                    f"Rate limit detected. Exponential backoff applied before retrying."
                )
                record_rate_limit()

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[message.model_dump() for message in messages],
                max_completion_tokens=max_tokens,
                tools=tools,
                extra_body=extra_body,
            )

            # Log which model was actually used (important for OpenRouter fallback tracking)
            model_used = response.model
            print(
                f"[MODEL_USAGE] LLM Request: Requested {model}, Used {model_used}",
                flush=True,
            )
            logger.info(
                f"LLM Request completed. Requested model: {model}, Actual model used: {model_used}"
            )

            # Capture metrics (only at depth 0 to avoid duplicate metrics from recursive calls)
            if depth == 0:
                response_time_ms = (time.time() - start_time) * 1000
                tokens_input = response.usage.prompt_tokens if response.usage else 0
                tokens_output = (
                    response.usage.completion_tokens if response.usage else 0
                )

                logger.info(
                    f"LLM Metrics - Model: {model_used}, Input tokens: {tokens_input}, "
                    f"Output tokens: {tokens_output}, Response time: {response_time_ms:.2f}ms"
                )

                # Record model success and quota
                total_tokens = tokens_input + tokens_output
                try:
                    record_model_success(model_used, response_time_ms, total_tokens)
                    record_request(model_used, total_tokens)
                except Exception as e:
                    logger.warning(f"Failed to record model metrics: {str(e)}")

                # Store metrics asynchronously (non-blocking)
                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model_used,
                            tokens_input=tokens_input,
                            tokens_output=tokens_output,
                            response_time_ms=response_time_ms,
                            status="success",
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to store metrics: {str(e)}")
        except Exception as e:
            # Capture error metrics
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"LLM Request failed: {str(e)}")

            if depth == 0:
                # Record model failure and general error
                try:
                    record_model_failure(model)
                    record_error()

                    # Check if it's a rate limit error (429)
                    error_str = str(e).lower()
                    if (
                        "429" in error_str
                        or "rate" in error_str
                        or "too many requests" in error_str
                    ):
                        logger.warning(
                            f"Rate limit error detected. Triggering exponential backoff."
                        )
                        handle_rate_limit_error()
                        record_rate_limit()
                except Exception as monitor_error:
                    logger.warning(
                        f"Failed to record error monitoring: {str(monitor_error)}"
                    )

                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model,
                            tokens_input=0,
                            tokens_output=0,
                            response_time_ms=response_time_ms,
                            status="error",
                            error_message=str(e),
                        )
                    )
                except Exception as metric_error:
                    logger.warning(
                        f"Failed to store error metrics: {str(metric_error)}"
                    )
            raise

        if len(response.choices) == 0:
            return None

        content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls

        if tool_calls:
            parsed_tool_calls = [
                OpenAIToolCall(
                    id=tool_call.id,
                    type=tool_call.type,
                    function=OpenAIToolCallFunction(
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    ),
                )
                for tool_call in tool_calls
            ]
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_openai(
                parsed_tool_calls
            )
            assistant_message = OpenAIAssistantMessage(
                role="assistant",
                content=content or "",  # Handle None content
                tool_calls=[tool_call.model_dump() for tool_call in parsed_tool_calls],
            )
            new_messages = [
                *messages,
                assistant_message,
                *tool_call_messages,
            ]
            return await self._generate_openai(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                tools=tools,
                extra_body=extra_body,
                depth=depth + 1,
            )

        # Return content, or empty string if None to prevent "no content" error
        if content is None or (isinstance(content, str) and not content.strip()):
            logger.warning(
                f"LLM returned empty or None content for model: {model}. "
                "This may happen with some free tier models. Returning empty response."
            )
            return ""
        return content

    async def _generate_google(
        self,
        model: str,
        messages: List[LLMMessage],
        tools: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ) -> str | None:
        client: genai.Client = self._client

        google_tools = None
        if tools:
            google_tools = [GoogleTool(function_declarations=[tool]) for tool in tools]

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=self._get_google_messages(messages),
            config=GenerateContentConfig(
                tools=google_tools,
                system_instruction=self._get_system_prompt(messages),
                response_mime_type="text/plain",
                max_output_tokens=max_tokens,
            ),
        )

        content = response.candidates[0].content
        response_parts = content.parts

        if not response_parts:
            return None

        text_content = None
        tool_calls = []
        for each_part in response_parts:
            if each_part.function_call:
                tool_calls.append(
                    GoogleToolCall(
                        id=each_part.function_call.id,
                        name=each_part.function_call.name,
                        arguments=each_part.function_call.args,
                    )
                )
            if each_part.text:
                text_content = each_part.text

        if tool_calls:
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_google(
                tool_calls
            )
            new_messages = [
                *messages,
                GoogleAssistantMessage(
                    role="assistant",
                    content=content,
                ),
                *tool_call_messages,
            ]
            return await self._generate_google(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                tools=tools,
                depth=depth + 1,
            )

        return text_content

    async def _generate_anthropic(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        depth: int = 0,
    ) -> str | None:
        client: AsyncAnthropic = self._client

        response: AnthropicMessage = await client.messages.create(
            model=model,
            system=self._get_system_prompt(messages),
            messages=[
                message.model_dump()
                for message in self._get_anthropic_messages(messages)
            ],
            tools=tools,
            max_tokens=max_tokens or 4000,
        )
        text_content = None
        tool_calls: List[AnthropicToolCall] = []
        for content in response.content:
            if content.type == "text" and isinstance(content.text, str):
                text_content = content.text

            if content.type == "tool_use":
                tool_calls.append(
                    AnthropicToolCall(
                        id=content.id,
                        type=content.type,
                        name=content.name,
                        input=content.input,
                    )
                )

        if tool_calls:
            tool_call_messages = (
                await self.tool_calls_handler.handle_tool_calls_anthropic(tool_calls)
            )
            new_messages = [
                *messages,
                AnthropicAssistantMessage(
                    role="assistant",
                    content=[each.model_dump() for each in tool_calls],
                ),
                AnthropicUserMessage(
                    role="user",
                    content=[each.model_dump() for each in tool_call_messages],
                ),
            ]
            return await self._generate_anthropic(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                tools=tools,
                depth=depth + 1,
            )

        return text_content

    async def _generate_ollama(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        return await self._generate_openai(
            model=model, messages=messages, max_tokens=max_tokens, depth=depth
        )

    async def _generate_ollama_cloud(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        import httpx

        custom_url = get_custom_llm_url_env()
        api_key = get_custom_llm_api_key_env() or "null"

        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            if isinstance(msg, LLMSystemMessage):
                ollama_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, LLMUserMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, OpenAIAssistantMessage):
                ollama_messages.append({"role": "assistant", "content": msg.content})

        payload = {"model": model, "messages": ollama_messages, "stream": False}

        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{custom_url.rstrip('/')}/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama Cloud error: {response.text}",
                )

            result = response.json()
            content = result.get("message", {}).get("content", "")

            if not content or not content.strip():
                if depth < 2:
                    return await self._generate_ollama_cloud(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        depth=depth + 1,
                    )
                logger.warning(f"Empty response from Ollama Cloud for model: {model}")
                return ""

            return content

    async def _generate_custom(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        # Special handling for Ollama Cloud
        custom_url = get_custom_llm_url_env()
        if custom_url and "ollama.com" in custom_url:
            return await self._generate_ollama_cloud(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                depth=depth,
            )

        extra_body = {"enable_thinking": False} if self.disable_thinking() else None
        return await self._generate_openai(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            extra_body=extra_body,
            depth=depth,
        )

    async def generate(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[type[LLMTool] | LLMDynamicTool]] = None,
    ):
        parsed_tools = self.tool_calls_handler.parse_tools(tools)

        content = None
        match self.llm_provider:
            case LLMProvider.OPENAI:
                content = await self._generate_openai(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.GOOGLE:
                content = await self._generate_google(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.ANTHROPIC:
                content = await self._generate_anthropic(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.OLLAMA:
                content = await self._generate_ollama(
                    model=model, messages=messages, max_tokens=max_tokens
                )
            case LLMProvider.CUSTOM:
                content = await self._generate_custom(
                    model=model, messages=messages, max_tokens=max_tokens
                )
        if content is None or (isinstance(content, str) and not content.strip()):
            # Log warning but don't fail - some free models may return empty responses
            logger.warning(
                f"LLM returned empty or None content for model: {model}. "
                "This may happen with some free tier models. Returning empty response."
            )
            return ""
        return content

    # ? Generate Structured Content
    async def _generate_openai_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        extra_body: Optional[dict] = None,
        depth: int = 0,
    ) -> dict | None:
        client: AsyncOpenAI = self._client
        start_time = time.time()

        # Check and handle rate limiting (only at depth 0)
        if depth == 0:
            was_rate_limited = await wait_if_rate_limited()
            if was_rate_limited:
                logger.info(
                    f"Rate limit detected. Exponential backoff applied before retrying."
                )
                record_rate_limit()

        response_schema = response_format
        all_tools = [*tools] if tools else None

        use_tool_calls_for_structured_output = (
            self.use_tool_calls_for_structured_output()
        )
        if strict and depth == 0:
            response_schema = ensure_strict_json_schema(
                response_schema,
                path=(),
                root=response_schema,
            )
        if use_tool_calls_for_structured_output and depth == 0:
            if all_tools is None:
                all_tools = []
            all_tools.append(
                self.tool_calls_handler.parse_tool(
                    LLMDynamicTool(
                        name="ResponseSchema",
                        description="Provide response to the user",
                        parameters=response_schema,
                        handler=do_nothing_async,
                    ),
                    strict=strict,
                )
            )

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[message.model_dump() for message in messages],
                response_format=(
                    {
                        "type": "json_schema",
                        "json_schema": (
                            {
                                "name": "ResponseSchema",
                                "strict": strict,
                                "schema": response_schema,
                            }
                        ),
                    }
                    if not use_tool_calls_for_structured_output
                    else None
                ),
                max_completion_tokens=max_tokens,
                tools=all_tools,
                extra_body=extra_body,
            )

            # Log which model was actually used (important for OpenRouter fallback tracking)
            model_used = response.model
            logger.info(
                f"LLM Structured Request completed. Requested model: {model}, Actual model used: {model_used}"
            )

            # Capture metrics (only at depth 0 to avoid duplicate metrics from recursive calls)
            if depth == 0:
                response_time_ms = (time.time() - start_time) * 1000
                tokens_input = response.usage.prompt_tokens if response.usage else 0
                tokens_output = (
                    response.usage.completion_tokens if response.usage else 0
                )

                logger.info(
                    f"LLM Structured Metrics - Model: {model_used}, Input tokens: {tokens_input}, "
                    f"Output tokens: {tokens_output}, Response time: {response_time_ms:.2f}ms"
                )

                # Record model success and quota
                total_tokens = tokens_input + tokens_output
                try:
                    record_model_success(model_used, response_time_ms, total_tokens)
                    record_request(model_used, total_tokens)
                except Exception as e:
                    logger.warning(f"Failed to record model metrics: {str(e)}")

                # Store metrics asynchronously (non-blocking)
                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model_used,
                            tokens_input=tokens_input,
                            tokens_output=tokens_output,
                            response_time_ms=response_time_ms,
                            status="success",
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to store structured metrics: {str(e)}")
        except Exception as e:
            # Capture error metrics
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"LLM Structured Request failed: {str(e)}")

            if depth == 0:
                # Record model failure and general error
                try:
                    record_model_failure(model)
                    record_error()

                    # Check if it's a rate limit error (429)
                    error_str = str(e).lower()
                    if (
                        "429" in error_str
                        or "rate" in error_str
                        or "too many requests" in error_str
                    ):
                        logger.warning(
                            f"Rate limit error detected. Triggering exponential backoff."
                        )
                        handle_rate_limit_error()
                        record_rate_limit()
                except Exception as monitor_error:
                    logger.warning(
                        f"Failed to record error monitoring: {str(monitor_error)}"
                    )

                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model,
                            tokens_input=0,
                            tokens_output=0,
                            response_time_ms=response_time_ms,
                            status="error",
                            error_message=str(e),
                        )
                    )
                except Exception as metric_error:
                    logger.warning(
                        f"Failed to store structured error metrics: {str(metric_error)}"
                    )
            raise

        if response is None or len(response.choices) == 0:
            return None

        content = response.choices[0].message.content

        tool_calls = response.choices[0].message.tool_calls
        has_response_schema = False

        if tool_calls:
            for tool_call in tool_calls:
                if tool_call.function.name == "ResponseSchema":
                    content = tool_call.function.arguments
                    has_response_schema = True

            if not has_response_schema:
                parsed_tool_calls = [
                    OpenAIToolCall(
                        id=tool_call.id,
                        type=tool_call.type,
                        function=OpenAIToolCallFunction(
                            name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                        ),
                    )
                    for tool_call in tool_calls
                ]
                tool_call_messages = (
                    await self.tool_calls_handler.handle_tool_calls_openai(
                        parsed_tool_calls
                    )
                )
                new_messages = [
                    *messages,
                    OpenAIAssistantMessage(
                        role="assistant",
                        content=content or "",  # Handle None content
                        tool_calls=[each.model_dump() for each in parsed_tool_calls],
                    ),
                    *tool_call_messages,
                ]
                content = await self._generate_openai_structured(
                    model=model,
                    messages=new_messages,
                    response_format=response_schema,
                    strict=strict,
                    max_tokens=max_tokens,
                    tools=all_tools,
                    extra_body=extra_body,
                    depth=depth + 1,
                )
        if content:
            if depth == 0:
                return dict(dirtyjson.loads(content))
            return content
        return None

    async def _generate_google_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        depth: int = 0,
    ) -> dict | None:
        client: genai.Client = self._client

        google_tools = None
        if tools:
            google_tools = [GoogleTool(function_declarations=[tool]) for tool in tools]
            google_tools.append(
                GoogleTool(
                    function_declarations=[
                        {
                            "name": "ResponseSchema",
                            "description": "Provide response to the user",
                            "parameters": remove_titles_from_schema(
                                flatten_json_schema(response_format)
                            ),
                        }
                    ]
                )
            )

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=self._get_google_messages(messages),
            config=GenerateContentConfig(
                tools=google_tools,
                tool_config=(
                    GoogleToolConfig(
                        function_calling_config=GoogleFunctionCallingConfig(
                            mode=GoogleFunctionCallingConfigMode.ANY,
                        ),
                    )
                    if tools
                    else None
                ),
                system_instruction=self._get_system_prompt(messages),
                response_mime_type="application/json" if not tools else None,
                response_json_schema=response_format if not tools else None,
                max_output_tokens=max_tokens,
            ),
        )

        content = response.candidates[0].content
        response_parts = content.parts
        text_content = None

        if not response_parts:
            return None

        tool_calls: List[GoogleToolCall] = []
        for each_part in response_parts:
            if each_part.function_call:
                tool_calls.append(
                    GoogleToolCall(
                        id=each_part.function_call.id,
                        name=each_part.function_call.name,
                        arguments=each_part.function_call.args,
                    )
                )

            if each_part.text:
                text_content = each_part.text

        for each in tool_calls:
            if each.name == "ResponseSchema":
                return each.arguments

        if tool_calls:
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_google(
                tool_calls
            )
            new_messages = [
                *messages,
                GoogleAssistantMessage(
                    role="assistant",
                    content=content,
                ),
                *tool_call_messages,
            ]
            return await self._generate_google_structured(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                response_format=response_format,
                tools=tools,
                depth=depth + 1,
            )

        if text_content:
            return dict(dirtyjson.loads(text_content))
        return None

    async def _generate_anthropic_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        tools: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        client: AsyncAnthropic = self._client
        response: AnthropicMessage = await client.messages.create(
            model=model,
            system=self._get_system_prompt(messages),
            messages=[
                message.model_dump()
                for message in self._get_anthropic_messages(messages)
            ],
            max_tokens=max_tokens or 4000,
            tools=[
                {
                    "name": "ResponseSchema",
                    "description": "A response to the user's message",
                    "input_schema": response_format,
                },
                *(tools or []),
            ],
        )
        tool_calls: List[AnthropicToolCall] = []
        for content in response.content:
            if content.type == "tool_use":
                tool_calls.append(
                    AnthropicToolCall(
                        id=content.id,
                        type=content.type,
                        name=content.name,
                        input=content.input,
                    )
                )

        for each in tool_calls:
            if each.name == "ResponseSchema":
                return each.input

        if tool_calls:
            tool_call_messages = (
                await self.tool_calls_handler.handle_tool_calls_anthropic(tool_calls)
            )
            new_messages = [
                *messages,
                AnthropicAssistantMessage(
                    role="assistant",
                    content=[each.model_dump() for each in tool_calls],
                ),
                AnthropicUserMessage(
                    role="user",
                    content=[each.model_dump() for each in tool_call_messages],
                ),
            ]
            return await self._generate_anthropic_structured(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                response_format=response_format,
                tools=tools,
                depth=depth + 1,
            )

        return None

    async def _generate_ollama_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        return await self._generate_openai_structured(
            model=model,
            messages=messages,
            response_format=response_format,
            strict=strict,
            max_tokens=max_tokens,
            depth=depth,
        )

    async def _generate_ollama_cloud_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        import httpx

        custom_url = get_custom_llm_url_env()
        api_key = get_custom_llm_api_key_env() or "null"

        # Build prompt with schema instruction
        text_content = ""
        for msg in messages:
            if isinstance(msg, LLMSystemMessage):
                text_content += f"System: {msg.content}\n"
            elif isinstance(msg, LLMUserMessage):
                text_content += f"User: {msg.content}\n"
            elif isinstance(msg, OpenAIAssistantMessage):
                text_content += f"Assistant: {msg.content}\n"

        # Add JSON schema instruction
        schema_str = json.dumps(response_format, indent=2)
        text_content += (
            f"\nRespond ONLY with valid JSON matching this schema:\n{schema_str}\n"
        )

        ollama_messages = [{"role": "user", "content": text_content}]

        payload = {"model": model, "messages": ollama_messages, "stream": False}

        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{custom_url.rstrip('/')}/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama Cloud structured error: {response.text}",
                )

            result = response.json()
            content = result.get("message", {}).get("content", "")

            if not content or not content.strip():
                if depth < 2:
                    return await self._generate_ollama_cloud_structured(
                        model=model,
                        messages=messages,
                        response_format=response_format,
                        strict=strict,
                        max_tokens=max_tokens,
                        depth=depth + 1,
                    )
                logger.warning(
                    f"Empty response from Ollama Cloud structured for model: {model}"
                )
                return {}

            # Try to parse as JSON
            try:
                # Extract JSON from response if needed
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON from Ollama Cloud: {e}, content: {content}"
                )
                if depth < 2:
                    return await self._generate_ollama_cloud_structured(
                        model=model,
                        messages=messages,
                        response_format=response_format,
                        strict=strict,
                        max_tokens=max_tokens,
                        depth=depth + 1,
                    )
                return {}

    async def _generate_custom_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        # Special handling for Ollama Cloud - use Ollama Cloud format
        custom_url = get_custom_llm_url_env()
        if custom_url and "ollama.com" in custom_url:
            return await self._generate_ollama_cloud_structured(
                model=model,
                messages=messages,
                response_format=response_format,
                strict=strict,
                max_tokens=max_tokens,
                depth=depth,
            )

        extra_body = {"enable_thinking": False} if self.disable_thinking() else None
        return await self._generate_openai_structured(
            model=model,
            messages=messages,
            response_format=response_format,
            strict=strict,
            max_tokens=max_tokens,
            extra_body=extra_body,
            depth=depth,
        )

    async def generate_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        tools: Optional[List[type[LLMTool] | LLMDynamicTool]] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        parsed_tools = self.tool_calls_handler.parse_tools(tools)

        content = None
        match self.llm_provider:
            case LLMProvider.OPENAI:
                content = await self._generate_openai_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.GOOGLE:
                content = await self._generate_google_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.ANTHROPIC:
                content = await self._generate_anthropic_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.OLLAMA:
                content = await self._generate_ollama_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    max_tokens=max_tokens,
                )
            case LLMProvider.CUSTOM:
                content = await self._generate_custom_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    max_tokens=max_tokens,
                )
        if content is None:
            # Log warning but don't fail - some free models may return empty responses
            logger.warning(
                f"LLM returned empty or None content for structured request with model: {model}. "
                "This may happen with some free tier models. Returning empty dict."
            )
            return {}
        return content

    # ? Stream Unstructured Content
    async def _stream_openai(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        extra_body: Optional[dict] = None,
        depth: int = 0,
    ) -> AsyncGenerator[str, None]:
        client: AsyncOpenAI = self._client
        start_time = time.time()

        tool_calls: List[LLMToolCall] = []
        current_index = 0
        current_id = None
        current_name = None
        current_arguments = None
        model_logged = False
        model_used = None
        tokens_input = 0
        tokens_output = 0

        try:
            async for event in await client.chat.completions.create(
                model=model,
                messages=[message.model_dump() for message in messages],
                max_completion_tokens=max_tokens,
                tools=tools,
                extra_body=extra_body,
                stream=True,
            ):
                event: OpenAIChatCompletionChunk = event

                # Log model from first chunk and capture for metrics
                if not model_logged and hasattr(event, "model") and event.model:
                    model_used = event.model
                    logger.info(
                        f"LLM Stream started. Requested model: {model}, Actual model used: {model_used}"
                    )
                    model_logged = True

                # Capture token usage from the event if available
                if hasattr(event, "usage") and event.usage:
                    tokens_input = event.usage.prompt_tokens or 0
                    tokens_output = event.usage.completion_tokens or 0

                if not event.choices:
                    continue

                content_chunk = event.choices[0].delta.content
                if content_chunk:
                    yield content_chunk

                tool_call_chunk = event.choices[0].delta.tool_calls
                if tool_call_chunk:
                    tool_index = tool_call_chunk[0].index
                    tool_id = tool_call_chunk[0].id
                    tool_name = tool_call_chunk[0].function.name
                    tool_arguments = tool_call_chunk[0].function.arguments

                    if current_index != tool_index:
                        tool_calls.append(
                            OpenAIToolCall(
                                id=current_id,
                                type="function",
                                function=OpenAIToolCallFunction(
                                    name=current_name,
                                    arguments=current_arguments,
                                ),
                            )
                        )
                        current_index = tool_index
                        current_id = tool_id
                        current_name = tool_name
                        current_arguments = tool_arguments
                    else:
                        current_name = tool_name or current_name
                        current_id = tool_id or current_id
                        if current_arguments is None:
                            current_arguments = tool_arguments
                        elif tool_arguments:
                            current_arguments += tool_arguments

            if current_id is not None:
                tool_calls.append(
                    OpenAIToolCall(
                        id=current_id,
                        type="function",
                        function=OpenAIToolCallFunction(
                            name=current_name,
                            arguments=current_arguments,
                        ),
                    )
                )

            # Capture metrics for streaming (only at depth 0)
            if depth == 0:
                response_time_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"LLM Stream Metrics - Model: {model_used or model}, Input tokens: {tokens_input}, "
                    f"Output tokens: {tokens_output}, Response time: {response_time_ms:.2f}ms"
                )

                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model_used or model,
                            tokens_input=tokens_input,
                            tokens_output=tokens_output,
                            response_time_ms=response_time_ms,
                            status="success",
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to store stream metrics: {str(e)}")

            if tool_calls:
                tool_call_messages = (
                    await self.tool_calls_handler.handle_tool_calls_openai(tool_calls)
                )
                new_messages = [
                    *messages,
                    OpenAIAssistantMessage(
                        role="assistant",
                        content=None,
                        tool_calls=[each.model_dump() for each in tool_calls],
                    ),
                    *tool_call_messages,
                ]
                async for event in self._stream_openai(
                    model=model,
                    messages=new_messages,
                    max_tokens=max_tokens,
                    tools=tools,
                    extra_body=extra_body,
                    depth=depth + 1,
                ):
                    yield event
        except Exception as e:
            # Capture error metrics for streaming
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"LLM Stream failed: {str(e)}")

            if depth == 0:
                try:
                    asyncio.create_task(
                        store_metric_async(
                            model_name=model_used or model,
                            tokens_input=0,
                            tokens_output=0,
                            response_time_ms=response_time_ms,
                            status="error",
                            error_message=str(e),
                        )
                    )
                except Exception as metric_error:
                    logger.warning(
                        f"Failed to store stream error metrics: {str(metric_error)}"
                    )
            raise

    async def _stream_google(
        self,
        model: str,
        messages: List[LLMMessage],
        tools: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ) -> AsyncGenerator[str, None]:
        client: genai.Client = self._client

        google_tools = None
        if tools:
            google_tools = [GoogleTool(function_declarations=[tool]) for tool in tools]

        generated_contents = []
        tool_calls: List[GoogleToolCall] = []
        async for event in iterator_to_async(client.models.generate_content_stream)(
            model=model,
            contents=self._get_google_messages(messages),
            config=GenerateContentConfig(
                system_instruction=self._get_system_prompt(messages),
                response_mime_type="text/plain",
                tools=google_tools,
                max_output_tokens=max_tokens,
            ),
        ):
            if not (
                event.candidates
                and event.candidates[0].content
                and event.candidates[0].content.parts
            ):
                continue

            generated_contents.append(event.candidates[0].content)

            for each_part in event.candidates[0].content.parts:
                if each_part.text:
                    yield each_part.text

                if each_part.function_call:
                    tool_calls.append(
                        GoogleToolCall(
                            id=each_part.function_call.id,
                            name=each_part.function_call.name,
                            arguments=each_part.function_call.args,
                        )
                    )

        if tool_calls:
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_google(
                tool_calls
            )
            new_messages = [
                *messages,
                *[
                    GoogleAssistantMessage(
                        role="assistant",
                        content=each,
                    )
                    for each in generated_contents
                ],
                *tool_call_messages,
            ]
            async for event in self._stream_google(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                tools=tools,
                depth=depth + 1,
            ):
                yield event

    async def _stream_anthropic(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        depth: int = 0,
    ):
        client: AsyncAnthropic = self._client

        tool_calls: List[AnthropicToolCall] = []
        async with client.messages.stream(
            model=model,
            system=self._get_system_prompt(messages),
            messages=[
                message.model_dump()
                for message in self._get_anthropic_messages(messages)
            ],
            max_tokens=max_tokens or 4000,
            tools=tools,
        ) as stream:
            async for event in stream:
                event: AnthropicMessageStreamEvent = event

                if event.type == "text":
                    yield event.text

                if (
                    event.type == "content_block_stop"
                    and event.content_block.type == "tool_use"
                ):
                    tool_calls.append(
                        AnthropicToolCall(
                            id=event.content_block.id,
                            type=event.content_block.type,
                            name=event.content_block.name,
                            input=event.content_block.input,
                        )
                    )

        if tool_calls:
            tool_call_messages = (
                await self.tool_calls_handler.handle_tool_calls_anthropic(tool_calls)
            )
            new_messages = [
                *messages,
                AnthropicAssistantMessage(
                    role="assistant",
                    content=[each.model_dump() for each in tool_calls],
                ),
                AnthropicUserMessage(
                    role="user",
                    content=[each.model_dump() for each in tool_call_messages],
                ),
            ]
            async for event in self._stream_anthropic(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                tools=tools,
                depth=depth + 1,
            ):
                yield event

    def _stream_ollama(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        return self._stream_openai(
            model=model, messages=messages, max_tokens=max_tokens, depth=depth
        )

    def _stream_ollama_cloud(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        import httpx

        custom_url = get_custom_llm_url_env()
        api_key = get_custom_llm_api_key_env() or "null"

        ollama_messages = []
        for msg in messages:
            if isinstance(msg, LLMSystemMessage):
                ollama_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, LLMUserMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, OpenAIAssistantMessage):
                ollama_messages.append({"role": "assistant", "content": msg.content})

        payload = {"model": model, "messages": ollama_messages, "stream": True}

        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}

        async def generate():
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{custom_url.rstrip('/')}/chat",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Ollama Cloud streaming error: {response.text}",
                        )

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if data.get("message"):
                                    content = data["message"].get("content", "")
                                    if content:
                                        yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue

        async def async_generator():
            full_content = ""
            async for chunk in generate():
                full_content += json.loads(
                    chunk.replace("data: ", "").replace("\n\n", "")
                )["choices"][0]["delta"].get("content", "")
                yield chunk
            await record_model_success(model)

        return async_generator()

    def _stream_custom(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        # Special handling for Ollama Cloud streaming
        custom_url = get_custom_llm_url_env()
        if custom_url and "ollama.com" in custom_url:
            return self._stream_ollama_cloud(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                depth=depth,
            )

        extra_body = {"enable_thinking": False} if self.disable_thinking() else None
        return self._stream_openai(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            extra_body=extra_body,
            depth=depth,
        )

    def stream(
        self,
        model: str,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        tools: Optional[List[type[LLMTool] | LLMDynamicTool]] = None,
    ):
        parsed_tools = self.tool_calls_handler.parse_tools(tools)

        match self.llm_provider:
            case LLMProvider.OPENAI:
                return self._stream_openai(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.GOOGLE:
                return self._stream_google(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.ANTHROPIC:
                return self._stream_anthropic(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=parsed_tools,
                )
            case LLMProvider.OLLAMA:
                return self._stream_ollama(
                    model=model, messages=messages, max_tokens=max_tokens
                )
            case LLMProvider.CUSTOM:
                return self._stream_custom(
                    model=model, messages=messages, max_tokens=max_tokens
                )

    # ? Stream Structured Content
    async def _stream_openai_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        extra_body: Optional[dict] = None,
        depth: int = 0,
    ) -> AsyncGenerator[str, None]:
        client: AsyncOpenAI = self._client

        response_schema = response_format
        all_tools = [*tools] if tools else None

        use_tool_calls_for_structured_output = (
            self.use_tool_calls_for_structured_output()
        )
        if strict and depth == 0:
            response_schema = ensure_strict_json_schema(
                response_schema,
                path=(),
                root=response_schema,
            )

        if use_tool_calls_for_structured_output and depth == 0:
            if all_tools is None:
                all_tools = []
            all_tools.append(
                self.tool_calls_handler.parse_tool(
                    LLMDynamicTool(
                        name="ResponseSchema",
                        description="Provide response to the user",
                        parameters=response_schema,
                        handler=do_nothing_async,
                    ),
                    strict=strict,
                )
            )

        tool_calls: List[LLMToolCall] = []
        current_index = 0
        current_id = None
        current_name = None
        current_arguments = None

        has_response_schema_tool_call = False
        async for event in await client.chat.completions.create(
            model=model,
            messages=[message.model_dump() for message in messages],
            max_completion_tokens=max_tokens,
            tools=all_tools,
            response_format=(
                {
                    "type": "json_schema",
                    "json_schema": (
                        {
                            "name": "ResponseSchema",
                            "strict": strict,
                            "schema": response_schema,
                        }
                    ),
                }
                if not use_tool_calls_for_structured_output
                else None
            ),
            extra_body=extra_body,
            stream=True,
        ):
            event: OpenAIChatCompletionChunk = event
            if not event.choices:
                continue

            content_chunk = event.choices[0].delta.content
            if content_chunk and not use_tool_calls_for_structured_output:
                yield content_chunk

            tool_call_chunk = event.choices[0].delta.tool_calls
            if tool_call_chunk:
                tool_index = tool_call_chunk[0].index
                tool_id = tool_call_chunk[0].id
                tool_name = tool_call_chunk[0].function.name
                tool_arguments = tool_call_chunk[0].function.arguments

                if current_index != tool_index:
                    tool_calls.append(
                        OpenAIToolCall(
                            id=current_id,
                            type="function",
                            function=OpenAIToolCallFunction(
                                name=current_name,
                                arguments=current_arguments,
                            ),
                        )
                    )
                    current_index = tool_index
                    current_id = tool_id
                    current_name = tool_name
                    current_arguments = tool_arguments
                else:
                    current_name = tool_name or current_name
                    current_id = tool_id or current_id
                    if current_arguments is None:
                        current_arguments = tool_arguments
                    elif tool_arguments:
                        current_arguments += tool_arguments

                if current_name == "ResponseSchema":
                    if tool_arguments:
                        yield tool_arguments
                    has_response_schema_tool_call = True

        if current_id is not None:
            tool_calls.append(
                OpenAIToolCall(
                    id=current_id,
                    type="function",
                    function=OpenAIToolCallFunction(
                        name=current_name,
                        arguments=current_arguments,
                    ),
                )
            )

        if tool_calls and not has_response_schema_tool_call:
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_openai(
                tool_calls
            )
            new_messages = [
                *messages,
                OpenAIAssistantMessage(
                    role="assistant",
                    content=None,
                    tool_calls=[each.model_dump() for each in tool_calls],
                ),
                *tool_call_messages,
            ]
            async for event in self._stream_openai_structured(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                strict=strict,
                tools=all_tools,
                response_format=response_schema,
                extra_body=extra_body,
                depth=depth + 1,
            ):
                yield event

    async def _stream_google_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        depth: int = 0,
    ) -> AsyncGenerator[str, None]:
        client: genai.Client = self._client

        google_tools = None
        if tools:
            google_tools = [GoogleTool(function_declarations=[tool]) for tool in tools]
            google_tools.append(
                GoogleTool(
                    function_declarations=[
                        {
                            "name": "ResponseSchema",
                            "description": "Provide response to the user",
                            "parameters": remove_titles_from_schema(
                                flatten_json_schema(response_format)
                            ),
                        }
                    ]
                )
            )

        parsed_messages = self._get_google_messages(messages)

        generated_contents = []
        tool_calls: List[GoogleToolCall] = []
        has_response_schema_tool_call = False
        async for event in iterator_to_async(client.models.generate_content_stream)(
            model=model,
            contents=parsed_messages,
            config=GenerateContentConfig(
                tools=google_tools,
                tool_config=(
                    GoogleToolConfig(
                        function_calling_config=GoogleFunctionCallingConfig(
                            mode=GoogleFunctionCallingConfigMode.ANY,
                        ),
                    )
                    if tools
                    else None
                ),
                system_instruction=self._get_system_prompt(messages),
                response_mime_type="application/json" if not tools else None,
                response_json_schema=response_format if not tools else None,
                max_output_tokens=max_tokens,
            ),
        ):
            if not (
                event.candidates
                and event.candidates[0].content
                and event.candidates[0].content.parts
            ):
                continue

            generated_contents.append(event.candidates[0].content)

            for each_part in event.candidates[0].content.parts:
                if each_part.text and not google_tools:
                    yield each_part.text

                if each_part.function_call:
                    if each_part.function_call.name == "ResponseSchema":
                        has_response_schema_tool_call = True
                        if each_part.function_call.args:
                            yield json.dumps(each_part.function_call.args)

                    tool_calls.append(
                        GoogleToolCall(
                            id=each_part.function_call.id,
                            name=each_part.function_call.name,
                            arguments=each_part.function_call.args,
                        )
                    )

        if tool_calls and not has_response_schema_tool_call:
            tool_call_messages = await self.tool_calls_handler.handle_tool_calls_google(
                tool_calls
            )
            new_messages = [
                *messages,
                *[
                    GoogleAssistantMessage(
                        role="assistant",
                        content=each,
                    )
                    for each in generated_contents
                ],
                *tool_call_messages,
            ]
            async for event in self._stream_google_structured(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                response_format=response_format,
                tools=tools,
                depth=depth + 1,
            ):
                yield event

    async def _stream_anthropic_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        tools: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ) -> AsyncGenerator[str, None]:
        client: AsyncAnthropic = self._client

        tool_calls: List[AnthropicToolCall] = []
        has_response_schema_tool_call = False
        async with client.messages.stream(
            model=model,
            system=self._get_system_prompt(messages),
            messages=[
                message.model_dump()
                for message in self._get_anthropic_messages(messages)
            ],
            max_tokens=max_tokens or 4000,
            tools=[
                {
                    "name": "ResponseSchema",
                    "description": "A response to the user's message",
                    "input_schema": response_format,
                },
                *(tools or []),
            ],
        ) as stream:
            is_response_schema_tool_call_started = False
            async for event in stream:
                event: AnthropicMessageStreamEvent = event

                if (
                    event.type == "content_block_start"
                    and event.content_block.type == "tool_use"
                ):
                    if event.content_block.name == "ResponseSchema":
                        has_response_schema_tool_call = True
                        is_response_schema_tool_call_started = True

                if (
                    event.type == "content_block_delta"
                    and event.delta.type == "input_json_delta"
                    and is_response_schema_tool_call_started
                ):
                    yield event.delta.partial_json

                if (
                    event.type == "content_block_stop"
                    and event.content_block.type == "tool_use"
                ):
                    tool_calls.append(
                        AnthropicToolCall(
                            id=event.content_block.id,
                            type=event.content_block.type,
                            name=event.content_block.name,
                            input=event.content_block.input,
                        )
                    )

        if tool_calls and not has_response_schema_tool_call:
            tool_call_messages = (
                await self.tool_calls_handler.handle_tool_calls_anthropic(tool_calls)
            )
            new_messages = [
                *messages,
                AnthropicAssistantMessage(
                    role="assistant",
                    content=[each.model_dump() for each in tool_calls],
                ),
                AnthropicUserMessage(
                    role="user",
                    content=[each.model_dump() for each in tool_call_messages],
                ),
            ]
            async for event in self._stream_anthropic_structured(
                model=model,
                messages=new_messages,
                max_tokens=max_tokens,
                response_format=response_format,
                tools=tools,
                depth=depth + 1,
            ):
                yield event

    def _stream_ollama_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        return self._stream_openai_structured(
            model=model,
            messages=messages,
            response_format=response_format,
            strict=strict,
            max_tokens=max_tokens,
            depth=depth,
        )

    def _stream_custom_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        max_tokens: Optional[int] = None,
        depth: int = 0,
    ):
        # Special handling for Ollama Cloud - use non-streaming
        custom_url = get_custom_llm_url_env()
        if custom_url and "ollama.com" in custom_url:
            # For streaming, we still need to call non-streaming and yield chunks
            async def generate():
                result = await self._generate_ollama_cloud_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    max_tokens=max_tokens,
                    depth=depth,
                )
                result_str = json.dumps(result)
                # Yield one chunk with all content
                yield f"data: {json.dumps({'choices': [{'delta': {'content': result_str}}]})}\n\n"
                yield "data: [DONE]\n\n"

            return generate()

        extra_body = {"enable_thinking": False} if self.disable_thinking() else None
        return self._stream_openai_structured(
            model=model,
            messages=messages,
            response_format=response_format,
            strict=strict,
            max_tokens=max_tokens,
            extra_body=extra_body,
            depth=depth,
        )

    def stream_structured(
        self,
        model: str,
        messages: List[LLMMessage],
        response_format: dict,
        strict: bool = False,
        tools: Optional[List[type[LLMTool] | LLMDynamicTool]] = None,
        max_tokens: Optional[int] = None,
    ):
        parsed_tools = self.tool_calls_handler.parse_tools(tools)

        match self.llm_provider:
            case LLMProvider.OPENAI:
                return self._stream_openai_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.GOOGLE:
                return self._stream_google_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.ANTHROPIC:
                return self._stream_anthropic_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    tools=parsed_tools,
                    max_tokens=max_tokens,
                )
            case LLMProvider.OLLAMA:
                return self._stream_ollama_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    max_tokens=max_tokens,
                )
            case LLMProvider.CUSTOM:
                return self._stream_custom_structured(
                    model=model,
                    messages=messages,
                    response_format=response_format,
                    strict=strict,
                    max_tokens=max_tokens,
                )

    # ? Web search
    async def _search_openai(self, query: str) -> str:
        client: AsyncOpenAI = self._client
        response = await client.responses.create(
            model=get_model(),
            tools=[
                {
                    "type": "web_search_preview",
                }
            ],
            input=query,
        )
        return response.output_text

    async def _search_google(self, query: str) -> str:
        client: genai.Client = self._client
        grounding_tool = GoogleTool(google_search=GoogleSearch())
        config = GenerateContentConfig(tools=[grounding_tool])

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=get_model(),
            contents=query,
            config=config,
        )
        return response.text

    async def _search_anthropic(self, query: str) -> str:
        client: AsyncAnthropic = self._client

        response = await client.messages.create(
            model=get_model(),
            max_tokens=4000,
            messages=[{"role": "user", "content": query}],
            tools=[
                {"type": "web_search_20250305", "name": "web_search", "max_uses": 1}
            ],
        )
        result = "\n".join(
            [each.text for each in response.content if each.type == "text"]
        )
        return result
