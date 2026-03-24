# Presenton Setup Progress

## Project: Open-Source AI Presentation Generator

### Setup Summary

Presenton has been successfully cloned and configured with Ollama as the primary LLM provider, using remote llama3.1:8b model (faster responses, no thinking overhead).

---

## ✅ Completed Steps

### 1. Repository Cloning
- **Date**: 2026-02-16
- **Location**: `/home/usdaw/presenton`
- **Source**: https://github.com/presenton/presenton
- **Status**: ✅ Complete

### 2. Docker Container Setup
- **Container Name**: `presenton`
- **Image**: `ghcr.io/presenton/presenton:latest`
- **Port Mapping**: `0.0.0.0:5001->80/tcp`
- **Volume Mount**: `$(pwd)/presenton/app_data:/app_data`
- **Status**: ✅ Running
- **Access URL**: http://localhost:5001

### 3. Ollama Remote Integration
- **Ollama URL**: `http://10.2.14.131:11434`
- **Model**: `deepseek-r1:8b`
- **API Test**: ✅ Verified working (2026-02-18)
- **Status**: ✅ Active
- **Test Response**: Successfully connected to remote Ollama server, model verified
- **Model Details**: 8B parameters, reasoning-focused
- **Note**: Multiple models tested (llama3.1, qwen3, gemma3) but reverted to deepseek-r1:8b for stability

### 4. Configuration Applied
```env
LLM=ollama
OLLAMA_URL=http://10.2.14.131:11434
OLLAMA_MODEL=deepseek-r1:8b
DISABLE_IMAGE_GENERATION=true
CAN_CHANGE_KEYS=false
LOG_LEVEL=DEBUG
PYTHONUNBUFFERED=1
OLLAMA_DEBUG=DEBUG
```

---

## 📋 Attempted Configurations

### 1. Ollama Integration (Completed)
- **Attempted**: Connect to remote Ollama server at `http://10.2.14.131:11434`
- **Models Tested**:
  - `glm-4.7-flash:latest` - Not supported by Presenton
  - `llama3.1:8b` - Supported, functional
  - `deepseek-r1:8b` - Supported, reasoning-focused (CURRENT)
- **Status**: ✅ Success - Connected to remote server
- **Reason**: Network issue resolved, container successfully connects
- **Result**: Ollama now active with deepseek-r1:8b (better reasoning for presentations)

### 2. Google Gemini 2.5 Flash (Previous Configuration)
- **Model**: `models/gemini-2.5-flash`
- **Status**: ❌ Replaced - Switched to Ollama for local control
- **Reason**: User preference for local/private model access
- **API Key Still Available**: `AIzaSyDVJcEWPle_J8yQ1ar1Lothfzk79MuP77w` (can be used as fallback)

### 3. Gemini 2.5 Flash Preview (Failed)
- **Attempted Model**: `gemini-2.5-flash-exp`
- **Status**: ❌ Failed - Model not found
- **Resolution**: Switched to `models/gemini-2.5-flash` (standard version)

### 4. GLM-4.7 Flash (Not Supported by Presenton)
- **Attempted Model**: `glm-4.7-flash:latest`
- **Status**: ❌ Not supported - Presenton doesn't recognize this model
- **Reason**: Model not in Presenton's list of supported Ollama models
- **Resolution**: Switched to `llama3.1:8b` (supported alternative)

### 5. Upgrade to DeepSeek R1 (Reasoning Improvement)
- **Previous Model**: `llama3.1:8b`
- **New Model**: `deepseek-r1:8b`
- **Status**: ✅ Upgraded Successfully (later reverted)
- **Reason**: DeepSeek R1 is reasoning-focused, better for organizing presentation content logically
- **Benefits**: Similar size (5.2GB vs 4.9GB), superior reasoning capabilities
- **Issue Found**: DeepSeek R1 shows "thinking" process, which makes it slower than expected

### 6. Switch to Llama 3.1 (Speed Improvement)
- **Previous Model**: `deepseek-r1:8b`
- **New Model**: `llama3.1:8b`
- **Status**: ⚠️ Switched - UnicodeEncodeError found
- **Reason**: DeepSeek R1's reasoning overhead caused slower response times; attempted llama3.1:8b for faster generation
- **Issue Found**: llama3.1:8b generates emojis that cause UTF-8 encoding errors in Presenton
- **Resolution**: Reverted to deepseek-r1:8b

### 7. Attempt qwen3:8b (Alternative Model)
- **Previous Model**: `llama3.1:8b`
- **New Model**: `qwen3:8b`
- **Status**: ⚠️ Pull hung / stuck
- **Reason**: qwen3:8b pull got stuck in a loop, never completed
- **Result**: Abandoned due to stuck download

### 8. Attempt gemma3:4b (Alternative Model)
- **Previous Model**: `qwen3:8b` (stuck)
- **New Model**: `gemma3:4b`
- **Status**: ⚠️ Pull hung / stuck
- **Reason**: gemma3:4b pull also got stuck in a loop
- **Result**: Abandoned due to stuck download

### 9. Revert to DeepSeek R1 (Stable Model)
- **Previous Model**: `gemma3:4b` (stuck)
- **Current Model**: `deepseek-r1:8b`
- **Status**: ✅ Active and Working
- **Reason**: deepseek-r1:8b is the only model consistently working without errors
- **Trade-off**: Accept reasoning overhead for stability
- **Conclusion**: deepseek-r1:8b with thinking process is reliable, albeit slower than ideal

---

## 🔄 Planned Next Steps

### 1. OpenRouter Fallback Provider Setup
**Status**: ⏳ Pending User Approval

**Objective**: Add OpenRouter as secondary LLM provider to use when Ollama is unavailable or slow

**Implementation Plan**:
1. Restart Presenton container with `CAN_CHANGE_KEYS="true"`
2. Configure OpenRouter through UI (no container restarts needed)
3. Switch providers manually when Google credits run out

**OpenRouter Configuration**:
- **Base URL**: `https://openrouter.ai/api/v1`
- **Provider Type**: `custom` (OpenAI-compatible)
- **API Key**: ⏳ Awaiting user input
- **Get API Key**: https://openrouter.ai/keys

**Recommended OpenRouter Models**:
- `anthropic/claude-3.5-sonnet` - High quality, good for complex presentations
- `google/gemini-2.5-flash` - Fast, cost-effective
- `openai/gpt-4o-mini` - Budget-friendly option

**Environment Variables for Switch**:
```bash
-e CAN_CHANGE_KEYS="true"  # Enable UI configuration access
```

---

## 📊 Current System Status

### Container Information
```bash
# View running container
docker ps | grep presenton

# View logs
docker logs presenton

# Check configuration
docker inspect presenton --format='{{range .Config.Env}}{{println .}}{{end}}' | grep -E "GOOGLE|LLM|DISABLE"
```

### Verification Commands
```bash
# Test Presenton HTTP response
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001

# Test Ollama connection
curl -s http://10.2.14.131:11434/api/tags

# Test Ollama model
curl -s http://10.2.14.131:11434/api/generate -d '{"model":"glm-4.7-flash:latest","prompt":"Hello","stream":false}'
```

---

## 🔧 Technical Details

### Supported LLM Providers (From Documentation)
- ✅ **OpenAI** (gpt-4o, gpt-4.1, etc.)
- ✅ **Google** (gemini-2.5-flash, gemini-2.0-flash, etc.)
- ✅ **Anthropic** (claude-3.5-sonnet, claude-3-opus, etc.)
- ✅ **Ollama** (llama3.2, deepseek-r1, qwen3, glm-4.7-flash, etc.) - **ACTIVE**
- ✅ **Custom** (OpenAI-compatible APIs like OpenRouter)

### Available Ollama Models
- ✅ `deepseek-r1:8b` - **ACTIVE** (8B parameters, reasoning-focused)
- ⚠️ `llama3.1:8b` - Has UnicodeEncodeError with emojis
- ✅ `qwen3-vl:8b` - Available (8.8B parameters, vision model)
- ✅ `glm-4.7-flash:latest` - Available (29.9B parameters, NOT supported by Presenton)

### Image Providers (Currently Disabled)
- ❌ **DALL-E 3** (OpenAI)
- ❌ **Gemini Flash** (Google)
- ❌ **Pexels** (Stock photos)
- ❌ **Pixabay** (Stock photos)
- ❌ **ComfyUI** (Self-hosted)

### Configuration Management
- **Environment Variables**: Primary configuration method
- **UI Configuration**: Available when `CAN_CHANGE_KEYS="true"`
- **Config Storage**: `/app_data/user_config.json` (when UI is enabled)
- **Persistent Data**: Mounted to `./presenton/app_data`

---

## 📚 Documentation References

### Official Presenton Docs
- **Main Documentation**: https://docs.presenton.ai
- **Quickstart**: https://docs.presenton.ai/v3/get-started/quickstart.md
- **Environment Variables**: https://docs.presenton.ai/v3/configurations/environment-variables.md
- **Using Ollama Models**: https://docs.presenton.ai/v3/configurations/using-ollama-models.md
- **Custom LLM (OpenAI-compatible)**: https://docs.presenton.ai/v3/configurations/using-custom-llm.md

### API Endpoints
- **Generate Presentation**: `POST /api/v1/ppt/presentation/generate`
- **Upload Files**: `POST /api/v1/ppt/files/upload`
- **Presentation List**: UI available at http://localhost:5001

---

## 💡 Usage Notes

### Current Limitations
1. **No Automatic Fallback**: Presenton doesn't automatically switch providers
2. **Manual Switching Required**: Use UI to change providers when needed
3. **Image Generation Disabled**: Currently set to `true` to conserve resources
4. **Single Provider Active**: Only one LLM provider active at a time
5. **Remote Ollama Dependency**: Requires remote server to be accessible

### Best Practices
1. **Monitor Ollama Server**: Ensure remote Ollama server is running and accessible
2. **Test Before Use**: Verify Ollama connectivity before generating presentations
3. **Backup Configuration**: Save working configurations for quick recovery
4. **Switch Providers**: Use Google API or OpenRouter if Ollama is unavailable

---

## 🗓️ Timeline

| Date | Action | Status |
|------|--------|--------|
| 2026-02-16 | Cloned Presenton repository | ✅ Complete |
| 2026-02-16 | Started Docker container (default config) | ✅ Complete |
| 2026-02-16 | Tested Ollama remote integration (initial attempt) | ❌ Failed (network) |
| 2026-02-16 | Configured Google Gemini 2.5 Flash | ✅ Complete |
| 2026-02-16 | Verified Google API working | ✅ Complete |
| 2026-02-16 | Planned OpenRouter fallback | ⏳ Pending |
| 2026-02-18 | Reconfigured to use Ollama with llama3.1:8b | ✅ Complete |
| 2026-02-18 | Verified Ollama remote connectivity | ✅ Complete |
| 2026-02-18 | Upgraded to deepseek-r1:8b for better reasoning | ✅ Complete |
| 2026-02-18 | Switched to llama3.1:8b for faster responses (no thinking overhead) | ✅ Complete |
| ⏳ | Enable UI configuration for multi-provider | ⏳ Pending |
| ⏳ | Configure OpenRouter through UI | ⏳ Pending |

---

## 🆘 Troubleshooting

### Common Issues

**Issue**: Container can't connect to remote Ollama
**Solution**: Check firewall rules, ensure Ollama server accepts connections from Docker host

**Issue**: Google API quota exceeded
**Solution**: Switch to OpenRouter via UI or add Google Cloud billing

**Issue**: Can't modify LLM settings in UI
**Solution**: Restart container with `CAN_CHANGE_KEYS="true"`

**Issue**: Port 5001 already in use
**Solution**: Change port mapping (e.g., `-p 5002:80`) or stop conflicting service

---

## 📝 Notes for Future Development

### Potential Enhancements
1. **Automatic Provider Switching**: Script to monitor API quotas and auto-switch
2. **Load Balancing**: Distribute requests across multiple providers
3. **Cost Monitoring**: Dashboard showing usage and costs per provider
4. **Backup Configuration**: Export/import of provider configurations
5. **Image Generation**: Enable with Pexels or Pixabay API keys

### Cost Optimization
1. **Use Ollama**: Free, local processing with remote server
2. **Switch to Google/Cloud APIs**: Use when Ollama unavailable
3. **Model Selection**: Use smaller models for simple presentations
4. **Caching**: Cache repeated content generation

---

*Last Updated: 2026-02-18*
*Status: Ollama (deepseek-r1:8b) active via remote server at http://10.2.14.131:11434 - Reasoning-focused with thinking process overhead*
