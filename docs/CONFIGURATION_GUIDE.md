# Presenton Configuration Guide

**Version**: 1.0.0  
**Last Updated**: February 18, 2026  
**Audience**: Users who want to customize Presenton

---

## Environment Variables

Environment variables control how Presenton runs. Set them when starting the Docker container.

### API Key Management

#### CAN_CHANGE_KEYS
**Purpose**: Allow users to change API keys in the UI  
**Values**: `true` or `false`  
**Default**: `true`  
**Example**:
```bash
docker run -e CAN_CHANGE_KEYS="false" ...
```

**When to Use**:
- Set to `false` if you want to lock API keys
- Set to `true` if you want users to change keys

---

## LLM (Text Generation) Configuration

### LLM Provider Selection

#### LLM
**Purpose**: Choose which AI provider to use for text generation  
**Values**: `openai`, `google`, `anthropic`, `ollama`, `custom`  
**Default**: `custom` (OpenRouter free tier)  
**Example**:
```bash
docker run -e LLM="openai" ...
```

---

### OpenAI Configuration

#### OPENAI_API_KEY
**Purpose**: Your OpenAI API key  
**Required**: Yes, if `LLM="openai"`  
**Example**:
```bash
docker run -e LLM="openai" -e OPENAI_API_KEY="sk-..." ...
```

#### OPENAI_MODEL
**Purpose**: Which OpenAI model to use  
**Default**: `gpt-4.1`  
**Popular Options**:
- `gpt-4-turbo` — Fast, high quality
- `gpt-4` — Slower, best quality
- `gpt-3.5-turbo` — Fastest, good quality
**Example**:
```bash
docker run -e LLM="openai" -e OPENAI_MODEL="gpt-4-turbo" ...
```

---

### Google Configuration

#### GOOGLE_API_KEY
**Purpose**: Your Google API key  
**Required**: Yes, if `LLM="google"`  
**Example**:
```bash
docker run -e LLM="google" -e GOOGLE_API_KEY="..." ...
```

#### GOOGLE_MODEL
**Purpose**: Which Google model to use  
**Default**: `models/gemini-2.0-flash`  
**Popular Options**:
- `models/gemini-2.0-flash` — Fast, good quality
- `models/gemini-pro` — Balanced
- `models/gemini-pro-vision` — With image understanding
**Example**:
```bash
docker run -e LLM="google" -e GOOGLE_MODEL="models/gemini-2.0-flash" ...
```

---

### Anthropic Configuration

#### ANTHROPIC_API_KEY
**Purpose**: Your Anthropic API key  
**Required**: Yes, if `LLM="anthropic"`  
**Example**:
```bash
docker run -e LLM="anthropic" -e ANTHROPIC_API_KEY="..." ...
```

#### ANTHROPIC_MODEL
**Purpose**: Which Anthropic model to use  
**Default**: `claude-3-5-sonnet-20241022`  
**Popular Options**:
- `claude-3-5-sonnet` — Fast, high quality
- `claude-3-opus` — Slowest, best quality
- `claude-3-haiku` — Fastest, good quality
**Example**:
```bash
docker run -e LLM="anthropic" -e ANTHROPIC_MODEL="claude-3-5-sonnet-20241022" ...
```

---

### Ollama Configuration (Local Models)

#### OLLAMA_URL
**Purpose**: URL to your Ollama server  
**Default**: `http://localhost:11434`  
**Example**:
```bash
docker run -e LLM="ollama" -e OLLAMA_URL="http://ollama:11434" ...
```

#### OLLAMA_MODEL
**Purpose**: Which Ollama model to use  
**Required**: Yes, if `LLM="ollama"`  
**Popular Options**:
- `llama3.2:3b` — Fast, good quality
- `llama2:7b` — Balanced
- `mistral:7b` — Fast, good quality
**Example**:
```bash
docker run -e LLM="ollama" -e OLLAMA_MODEL="llama3.2:3b" ...
```

---

### Custom OpenAI-Compatible API

#### CUSTOM_LLM_URL
**Purpose**: URL to your custom OpenAI-compatible API  
**Required**: Yes, if `LLM="custom"`  
**Example**:
```bash
docker run -e LLM="custom" -e CUSTOM_LLM_URL="https://api.example.com/v1" ...
```

#### CUSTOM_LLM_API_KEY
**Purpose**: API key for your custom endpoint  
**Required**: Yes, if `LLM="custom"`  
**Example**:
```bash
docker run -e LLM="custom" -e CUSTOM_LLM_API_KEY="..." ...
```

#### CUSTOM_MODEL
**Purpose**: Model name at your custom endpoint  
**Required**: Yes, if `LLM="custom"`  
**Example**:
```bash
docker run -e LLM="custom" -e CUSTOM_MODEL="llama3.2:3b" ...
```

#### TOOL_CALLS
**Purpose**: Use tool calls instead of JSON schema for structured output  
**Values**: `true` or `false`  
**Default**: `false`  
**Example**:
```bash
docker run -e TOOL_CALLS="true" ...
```

#### DISABLE_THINKING
**Purpose**: Disable thinking/reasoning in custom models  
**Values**: `true` or `false`  
**Default**: `false`  
**Example**:
```bash
docker run -e DISABLE_THINKING="true" ...
```

---

### Web Search

#### WEB_SEARCH
**Purpose**: Enable web search for better results  
**Values**: `true` or `false`  
**Default**: `false`  
**Supported**: OpenAI, Google, Anthropic  
**Example**:
```bash
docker run -e WEB_SEARCH="true" ...
```

---

## Image Generation Configuration

### Image Provider Selection

#### DISABLE_IMAGE_GENERATION
**Purpose**: Disable image generation entirely  
**Values**: `true` or `false`  
**Default**: `false`  
**Example**:
```bash
docker run -e DISABLE_IMAGE_GENERATION="true" ...
```

#### IMAGE_PROVIDER
**Purpose**: Choose which service generates images  
**Values**: `dall-e-3`, `gpt-image-1.5`, `gemini_flash`, `nanobanana_pro`, `pexels`, `pixabay`, `comfyui`  
**Required**: Yes, unless `DISABLE_IMAGE_GENERATION="true"`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="dall-e-3" ...
```

---

### OpenAI Image Generation

#### DALL_E_3_QUALITY
**Purpose**: Quality level for DALL-E 3 images  
**Values**: `standard` or `hd`  
**Default**: `standard`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="dall-e-3" -e DALL_E_3_QUALITY="hd" ...
```

#### GPT_IMAGE_1_5_QUALITY
**Purpose**: Quality level for GPT Image 1.5  
**Values**: `low`, `medium`, or `high`  
**Default**: `medium`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="gpt-image-1.5" -e GPT_IMAGE_1_5_QUALITY="high" ...
```

---

### Google Image Generation

**Requires**: `GOOGLE_API_KEY`

**Providers**:
- `gemini_flash` — Fast, good quality
- `nanobanana_pro` — High quality

**Example**:
```bash
docker run -e IMAGE_PROVIDER="gemini_flash" -e GOOGLE_API_KEY="..." ...
```

---

### Stock Photo Services

#### PEXELS_API_KEY
**Purpose**: API key for Pexels stock photos  
**Required**: Yes, if `IMAGE_PROVIDER="pexels"`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="pexels" -e PEXELS_API_KEY="..." ...
```

#### PIXABAY_API_KEY
**Purpose**: API key for Pixabay stock photos  
**Required**: Yes, if `IMAGE_PROVIDER="pixabay"`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="pixabay" -e PIXABAY_API_KEY="..." ...
```

---

### ComfyUI (Self-Hosted)

#### COMFYUI_URL
**Purpose**: URL to your ComfyUI server  
**Required**: Yes, if `IMAGE_PROVIDER="comfyui"`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="comfyui" -e COMFYUI_URL="http://comfyui:8188" ...
```

#### COMFYUI_WORKFLOW
**Purpose**: ComfyUI workflow JSON  
**Required**: Yes, if `IMAGE_PROVIDER="comfyui"`  
**Example**:
```bash
docker run -e IMAGE_PROVIDER="comfyui" -e COMFYUI_WORKFLOW='{"nodes":{...}}' ...
```

---

## Telemetry Configuration

#### DISABLE_ANONYMOUS_TELEMETRY
**Purpose**: Disable anonymous usage telemetry  
**Values**: `true` or `false`  
**Default**: `false`  
**Example**:
```bash
docker run -e DISABLE_ANONYMOUS_TELEMETRY="true" ...
```

---

## Complete Configuration Examples

### Example 1: Free Tier (No Costs)

```bash
docker run -it --name presenton \
  -p 5000:80 \
  -e LLM="custom" \
  -e CUSTOM_LLM_URL="https://openrouter.ai/api/v1" \
  -e CUSTOM_LLM_API_KEY="sk-or-..." \
  -e CUSTOM_MODEL="openrouter/free" \
  -e IMAGE_PROVIDER="pexels" \
  -e PEXELS_API_KEY="..." \
  -e CAN_CHANGE_KEYS="false" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

### Example 2: OpenAI + DALL-E

```bash
docker run -it --name presenton \
  -p 5000:80 \
  -e LLM="openai" \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_MODEL="gpt-4-turbo" \
  -e IMAGE_PROVIDER="dall-e-3" \
  -e DALL_E_3_QUALITY="hd" \
  -e CAN_CHANGE_KEYS="false" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

### Example 3: Google + Gemini

```bash
docker run -it --name presenton \
  -p 5000:80 \
  -e LLM="google" \
  -e GOOGLE_API_KEY="..." \
  -e GOOGLE_MODEL="models/gemini-2.0-flash" \
  -e IMAGE_PROVIDER="gemini_flash" \
  -e CAN_CHANGE_KEYS="false" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

### Example 4: Local Ollama

```bash
docker run -it --name presenton \
  -p 5000:80 \
  -e LLM="ollama" \
  -e OLLAMA_URL="http://ollama:11434" \
  -e OLLAMA_MODEL="llama3.2:3b" \
  -e IMAGE_PROVIDER="pexels" \
  -e PEXELS_API_KEY="..." \
  -e CAN_CHANGE_KEYS="false" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

### Example 5: Anthropic Claude

```bash
docker run -it --name presenton \
  -p 5000:80 \
  -e LLM="anthropic" \
  -e ANTHROPIC_API_KEY="..." \
  -e ANTHROPIC_MODEL="claude-3-5-sonnet-20241022" \
  -e IMAGE_PROVIDER="pexels" \
  -e PEXELS_API_KEY="..." \
  -e CAN_CHANGE_KEYS="false" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

---

## Model Selection Strategy

### Free Models (Best for Cost)

**Use when:**
- Budget is limited
- Testing or learning
- Speed isn't critical

**Models:**
- Meta Llama 3.3 70B
- Google Gemma
- Mistral Nemo

**Cost**: $0

---

### Premium Models (Best for Quality)

**Use when:**
- You need high-quality content
- Creating for clients
- Professional presentations

**Models:**
- Claude 3.5 Sonnet
- GPT-4 Turbo
- Gemini 2.0 Flash

**Cost**: $0.01-$0.50 per presentation

---

### Local Models (Best for Privacy)

**Use when:**
- You need complete privacy
- You have GPU available
- You want no API costs

**Models:**
- Llama 3.2
- Mistral 7B
- Phi 3

**Cost**: $0 (hardware only)

---

## Performance Tuning

### Faster Generation

1. **Use fewer slides** — 5-8 instead of 15-20
2. **Use faster models** — Llama instead of Claude
3. **Disable images** — Set `DISABLE_IMAGE_GENERATION="true"`
4. **Simpler topics** — Straightforward topics generate faster

### Better Quality

1. **Use premium models** — Claude, GPT-4, Gemini
2. **More slides** — 12-15 instead of 5-8
3. **Enable images** — Better visual presentations
4. **Specific topics** — Detailed topics = better content

---

## Database Options

Presenton stores data in SQLite by default. Configuration is automatic.

**Data Stored:**
- Presentation metadata
- Generation metrics
- User preferences
- Analytics data

**Location**: `/app_data/fastapi.db`

---

## Logging Configuration

Logs are written to:
- **Console**: Real-time output
- **Files**: In `/app_data/logs/`

**View logs:**
```bash
docker logs presenton
```

---

## API Rate Limiting

Rate limiting is handled by your API provider:

**OpenAI**: 3,500 requests/minute (free tier)  
**Google**: 60 requests/minute (free tier)  
**Anthropic**: 50,000 tokens/minute (free tier)  
**OpenRouter**: Varies by model

---

## Troubleshooting Configuration

### "API Key not working"
- Verify the key is correct
- Check the API provider is set correctly
- Ensure the key has required permissions

### "Model not found"
- Verify model name is correct
- Check the model is available in your region
- Try a different model

### "Images not generating"
- Check `IMAGE_PROVIDER` is set
- Verify image provider API key
- Try disabling and re-enabling

---

## Next Steps

1. **Choose your LLM** — OpenAI, Google, Anthropic, or local
2. **Choose your image provider** — DALL-E, Gemini, Pexels, or Pixabay
3. **Set environment variables** — Use examples above
4. **Start Presenton** — Run the Docker command
5. **Test** — Create a presentation to verify

---

## Need Help?

- **Getting Started**: [Getting Started Guide](PRESENTON_GETTING_STARTED.md)
- **User Guide**: [User Guide](USER_GUIDE.md)
- **Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- **FAQ**: [Frequently Asked Questions](FAQ.md)
