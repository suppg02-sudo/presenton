# Getting Started with Presenton

**Version**: 1.0.0  
**Last Updated**: February 18, 2026  
**Audience**: End users, non-technical

---

## What is Presenton?

Presenton is an open-source AI presentation generator that creates professional presentations in minutes. Simply describe what you want, and Presenton generates a complete presentation with slides, images, and formatting—all running locally on your device. No subscriptions, no hidden fees, just AI-powered presentations you control.

---

## 5-Minute Quick Start

### Step 1: Start Presenton

**Using Docker** (recommended):

```bash
docker run -it --name presenton -p 5000:80 -v "./app_data:/app_data" ghcr.io/presenton/presenton:latest
```

**Then open**: http://localhost:5000

### Step 2: Create Your First Presentation

1. **Enter a topic** — e.g., "Introduction to Machine Learning"
2. **Choose slide count** — 5-20 slides (default: 8)
3. **Select language** — English, Spanish, French, German, Chinese, and more
4. **Pick a template** — Choose your design style
5. **Click Generate** — Presenton creates your presentation

### Step 3: Download Your Presentation

- **View online** — Present directly in Presenton
- **Download PPTX** — Edit in PowerPoint
- **Download PDF** — Share as a document

**Total time**: ~2-5 minutes depending on slide count and model speed.

---

## Basic Workflow

```
Create Presentation
    ↓
Enter Topic & Settings
    ↓
AI Generates Content
    ↓
Review & Edit (Optional)
    ↓
Download (PPTX or PDF)
```

---

## Supported Languages

Presenton supports presentations in:

- **English** (US, UK, Australian)
- **Spanish** (Spain, Latin America)
- **French** (France, Canadian)
- **German**
- **Italian**
- **Portuguese** (Brazil, Portugal)
- **Chinese** (Simplified, Traditional)
- **Japanese**
- **Korean**
- **Russian**
- **Arabic**
- **Hindi**
- **Dutch**
- **Swedish**
- **Polish**

---

## Common Tasks

### Create a Presentation

1. Go to http://localhost:5000
2. Enter your topic in the text box
3. Set number of slides (5-20)
4. Select language
5. Choose template
6. Click **Generate**
7. Wait for completion (2-5 minutes)

### View Presentation History

1. Click **History** in the sidebar
2. See all presentations you've created
3. Click any presentation to view or edit

### Export Your Presentation

**As PowerPoint (PPTX)**:
- Click **Download PPTX**
- Open in Microsoft PowerPoint, Google Slides, or LibreOffice

**As PDF**:
- Click **Download PDF**
- Share or print directly

### Edit a Presentation

1. Open the presentation in Presenton
2. Click **Edit** on any slide
3. Modify text, images, or layout
4. Changes save automatically

---

## Troubleshooting Quick Links

### "Presentation is taking too long"
- **Solution**: Presenton uses free AI models by default. Larger presentations (15+ slides) take 3-5 minutes. This is normal.
- **See**: [Troubleshooting Guide → Performance Issues](TROUBLESHOOTING_GUIDE.md#presentation-takes-too-long)

### "I got an API error"
- **Solution**: Check your internet connection and API configuration.
- **See**: [Troubleshooting Guide → API Errors](TROUBLESHOOTING_GUIDE.md#api-errors)

### "Images aren't generating"
- **Solution**: Image generation may be disabled or misconfigured.
- **See**: [Troubleshooting Guide → Image Generation Issues](TROUBLESHOOTING_GUIDE.md#images-not-generating)

### "Presentation quality is poor"
- **Solution**: Try using a different model or adjusting verbosity settings.
- **See**: [User Guide → Model Selection](USER_GUIDE.md#understanding-model-selection)

---

## Frequently Asked Questions

**Q: Is Presenton free?**  
A: Yes! Presenton is open-source and free to use. You only pay for AI models if you use premium providers (optional).

**Q: Do I need an API key?**  
A: Presenton includes free models by default. You can optionally add your own API keys for premium models.

**Q: Can I use my own API keys?**  
A: Yes! See [Configuration Guide → API Keys](CONFIGURATION_GUIDE.md#api-keys).

**Q: What languages are supported?**  
A: 15+ languages including English, Spanish, French, German, Chinese, Japanese, and more.

**Q: Can I edit presentations after creation?**  
A: Yes! Click **Edit** on any slide to modify content, images, or layout.

**Q: How do I export presentations?**  
A: Download as PPTX (PowerPoint) or PDF from the presentation view.

**For more questions**, see [FAQ.md](FAQ.md)

---

## Next Steps

1. **Create your first presentation** — Try the 5-minute quick start above
2. **Explore features** — See [User Guide](USER_GUIDE.md) for all capabilities
3. **Customize settings** — Check [Configuration Guide](CONFIGURATION_GUIDE.md) for options
4. **Troubleshoot issues** — Visit [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) if needed

---

## Need Help?

- **Documentation**: [Table of Contents](TABLE_OF_CONTENTS.md)
- **Discord Community**: [Join our Discord](https://discord.gg/9ZsKKxudNE)
- **GitHub Issues**: [Report a bug](https://github.com/presenton/presenton/issues)
- **Email**: suraj@presenton.ai

---

**Ready to create your first presentation?** Open http://localhost:5000 and start now!
