# Frequently Asked Questions (FAQ)

**Version**: 1.0.0  
**Last Updated**: February 18, 2026  
**Audience**: Users with quick questions

---

## General Questions

### What is Presenton?

Presenton is an open-source AI presentation generator that creates professional presentations in minutes. Simply describe what you want, and Presenton generates a complete presentation with slides, images, and formatting—all running locally on your device.

**Key Features:**
- AI-powered content generation
- Multiple AI model support
- Automatic image generation
- Export as PPTX or PDF
- Completely free and open-source

---

### Is Presenton free?

Yes! Presenton is completely free and open-source. You only pay for AI models if you use premium providers (optional). Free models are included by default at no cost.

---

### Do I need an API key?

No, not required. Presenton includes free models by default. You can optionally add your own API keys for premium models if you want higher quality or faster generation.

---

### Can I use my own API keys?

Yes! You can use API keys from:
- OpenAI (GPT-4, GPT-3.5)
- Google (Gemini)
- Anthropic (Claude)
- Any OpenAI-compatible API

See [Configuration Guide](CONFIGURATION_GUIDE.md#api-key-management) for setup instructions.

---

### How much will it cost?

**Free tier**: $0 (using free models)

**Premium models**: $0.01-$0.50 per presentation (optional)

You only pay if you choose to use premium models. Free models are included at no cost.

---

### What data is stored?

Presenton stores:
- Presentation metadata (title, date created)
- Generation metrics (time, model used)
- User preferences (language, template)
- Analytics data (usage patterns)

**No personal data** is stored unless you provide it. All data stays on your device.

---

### Can I export my presentations?

Yes! You can export as:
- **PPTX** — PowerPoint format (fully editable)
- **PDF** — PDF format (fixed layout)

See [User Guide → Exporting](USER_GUIDE.md#exporting-presentations) for details.

---

## Language and Content

### What languages does Presenton support?

Presenton supports 15+ languages:

- English (US, UK, Australian)
- Spanish (Spain, Latin America)
- French (France, Canadian)
- German
- Italian
- Portuguese (Brazil, Portugal)
- Chinese (Simplified, Traditional)
- Japanese
- Korean
- Russian
- Arabic
- Hindi
- Dutch
- Swedish
- Polish

See [User Guide → Supported Languages](USER_GUIDE.md#supported-languages-and-slide-counts) for complete list.

---

### How many slides can I create?

**Minimum**: 5 slides  
**Maximum**: 20 slides  
**Recommended**: 8-12 slides

More slides = more detailed content but longer generation time.

---

### Can I edit presentations after creation?

Yes! You can:
- Edit slide text
- Replace images
- Change layout (on some templates)
- Reorder slides (in PowerPoint)

Click **Edit** on any slide to modify content.

---

### How do I create better presentations?

**Tips:**
1. **Be specific** — "Q4 Sales Report" not just "Sales"
2. **Provide context** — "For tech conference" or "For beginners"
3. **Use keywords** — Include important terms
4. **Increase slides** — More slides = more detail
5. **Use premium models** — Better quality content

See [User Guide → Best Practices](USER_GUIDE.md#best-practices-for-content) for more tips.

---

## Performance and Speed

### Why does it take X seconds?

Generation time depends on:
- **Slide count** — 5 slides: 1-2 min, 15 slides: 3-5 min
- **Model selection** — Free models are slower than premium
- **Image generation** — Adds 30-60 seconds
- **System load** — Other processes running

**Typical times:**
- 5 slides: 1-2 minutes
- 8 slides: 2-3 minutes
- 15 slides: 3-5 minutes

See [User Guide → Performance Tips](USER_GUIDE.md#performance-tips) for optimization.

---

### How can I make generation faster?

**Quick fixes:**
1. Use fewer slides (5-8 instead of 15-20)
2. Disable image generation
3. Use a faster model
4. Close other applications

See [Troubleshooting Guide → Performance](TROUBLESHOOTING_GUIDE.md#performance-problems) for more options.

---

### What's the difference between free and premium models?

| Aspect | Free | Premium |
|--------|------|---------|
| Cost | $0 | $0.01-$0.50 |
| Speed | 2-5 min | 2-4 min |
| Quality | Good | Excellent |
| Detail | Standard | Detailed |
| Best for | Testing, learning | Professional, clients |

**Examples:**
- Free: Meta Llama, Google Gemma
- Premium: Claude, GPT-4, Gemini Pro

---

### Can I use local models?

Yes! You can use Ollama to run models locally:
- No API costs
- Complete privacy
- Requires GPU for best performance

See [Configuration Guide → Ollama](CONFIGURATION_GUIDE.md#ollama-configuration-local-models) for setup.

---

## Features and Capabilities

### What templates are available?

Presenton includes multiple templates:
- General (versatile)
- Business (professional)
- Creative (colorful)
- Minimal (clean)
- And more...

You can change templates after generation.

---

### Can I use my own templates?

Yes! Presenton supports custom HTML templates with Tailwind CSS. See the main README for template development details.

---

### Can I generate presentations from documents?

Yes! You can upload documents (PDF, DOCX, etc.) and Presenton will generate presentations based on the content.

---

### What image providers are supported?

Presenton supports:
- **DALL-E 3** (OpenAI) — High quality
- **GPT Image 1.5** (OpenAI) — Fast
- **Gemini Flash** (Google) — Good quality
- **Pexels** (Stock photos) — Free
- **Pixabay** (Stock photos) — Free
- **ComfyUI** (Self-hosted) — Custom

See [Configuration Guide → Image Providers](CONFIGURATION_GUIDE.md#image-generation-configuration) for details.

---

### Can I disable image generation?

Yes! Set `DISABLE_IMAGE_GENERATION="true"` when starting Presenton. This makes generation faster.

---

## Technical Questions

### What are the system requirements?

**Minimum:**
- 2GB RAM
- 1GB disk space
- Docker installed
- Internet connection

**Recommended:**
- 4GB+ RAM
- 10GB+ disk space
- GPU (for local models)
- Stable internet

---

### Can I run Presenton on my computer?

Yes! Presenton runs on:
- Windows (with Docker Desktop)
- macOS (with Docker Desktop)
- Linux (with Docker)

See [Getting Started Guide](PRESENTON_GETTING_STARTED.md#5-minute-quick-start) for setup.

---

### Can I run Presenton on a server?

Yes! Presenton can be deployed as:
- Docker container
- Kubernetes pod
- Cloud service (AWS, GCP, Azure)
- Self-hosted server

See the main README for deployment options.

---

### Can I use Presenton as an API?

Yes! Presenton provides a REST API for programmatic access. See the main README for API documentation.

---

### What database does Presenton use?

Presenton uses SQLite by default. The database stores:
- Presentation metadata
- Generation metrics
- User preferences
- Analytics data

Database location: `/app_data/fastapi.db`

---

### Can I use an external database?

Yes! Presenton supports external SQL databases. See [Configuration Guide](CONFIGURATION_GUIDE.md#database-options) for details.

---

## Privacy and Security

### Is my data private?

Yes! All data stays on your device. Presenton:
- Runs locally
- Doesn't upload presentations to cloud
- Doesn't store personal information
- Doesn't track users (unless telemetry enabled)

---

### Can I disable telemetry?

Yes! Set `DISABLE_ANONYMOUS_TELEMETRY="true"` when starting Presenton.

---

### Is Presenton secure?

Presenton is:
- Open-source (code is auditable)
- Apache 2.0 licensed
- Regularly updated
- Community-maintained

You can review the source code on GitHub.

---

### What happens to my API keys?

API keys are:
- Stored locally on your device
- Never sent to Presenton servers
- Only used to call the API provider
- Encrypted if stored in config

---

## Troubleshooting

### I'm getting an API error

**Solutions:**
1. Check your API key is correct
2. Verify internet connection
3. Check API provider status
4. Try a different model

See [Troubleshooting Guide → API Errors](TROUBLESHOOTING_GUIDE.md#api-errors) for more help.

---

### Images aren't generating

**Solutions:**
1. Check image provider is configured
2. Verify image provider API key
3. Try a different image provider
4. Check image provider status

See [Troubleshooting Guide → Images](TROUBLESHOOTING_GUIDE.md#images-not-generating) for more help.

---

### Presentation quality is poor

**Solutions:**
1. Use a premium model
2. Be more specific in your topic
3. Increase slide count
4. Adjust verbosity setting

See [Troubleshooting Guide → Quality](TROUBLESHOOTING_GUIDE.md#poor-quality-content) for more help.

---

### I can't access Presenton

**Solutions:**
1. Check Presenton is running
2. Verify correct port (default: 5000)
3. Check firewall settings
4. Restart Docker

See [Troubleshooting Guide → Access](TROUBLESHOOTING_GUIDE.md#cant-access-presenton) for more help.

---

## Getting Help

### Where can I get help?

- **Documentation**: [Table of Contents](TABLE_OF_CONTENTS.md)
- **Getting Started**: [Getting Started Guide](PRESENTON_GETTING_STARTED.md)
- **User Guide**: [User Guide](USER_GUIDE.md)
- **Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- **Discord**: [Join our community](https://discord.gg/9ZsKKxudNE)
- **GitHub**: [Report issues](https://github.com/presenton/presenton/issues)
- **Email**: suraj@presenton.ai

---

### How do I report a bug?

1. Gather error message and logs
2. Note steps to reproduce
3. Open issue on GitHub
4. Or email suraj@presenton.ai

See [Troubleshooting Guide → Getting Help](TROUBLESHOOTING_GUIDE.md#getting-help) for details.

---

### How do I request a feature?

1. Check if feature already exists
2. Open GitHub issue with "Feature Request" label
3. Describe what you want and why
4. Or discuss on Discord

---

## Advanced Questions

### Can I contribute to Presenton?

Yes! Presenton is open-source and welcomes contributions:
- Code improvements
- Bug fixes
- Documentation
- Translations
- Feature development

See GitHub repository for contribution guidelines.

---

### Can I fork Presenton?

Yes! Presenton is Apache 2.0 licensed. You can:
- Fork the repository
- Modify the code
- Deploy your own version
- Contribute back improvements

---

### How often is Presenton updated?

Presenton is actively maintained with:
- Regular bug fixes
- New features
- Model updates
- Security patches

Check GitHub for latest releases.

---

### What's the roadmap?

Planned features include:
- Custom system prompts
- Advanced template editor
- Collaboration features
- Mobile app
- And more...

See GitHub for detailed roadmap.

---

## Still Have Questions?

**Can't find your answer?**

1. Check [Table of Contents](TABLE_OF_CONTENTS.md) for all docs
2. Search GitHub issues
3. Ask on Discord
4. Email suraj@presenton.ai

We're here to help!

---

**Last Updated**: February 18, 2026  
**Version**: 1.0.0
