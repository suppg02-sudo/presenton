# Presenton Troubleshooting Guide

**Version**: 1.0.0  
**Last Updated**: February 18, 2026  
**Audience**: Users encountering issues

---

## Common Issues and Solutions

### Presentation Takes Too Long

**Symptoms:**
- Generation takes 5+ minutes
- Waiting longer than expected
- Progress seems stuck

**Causes:**
- Using free models (slower)
- Large slide count (15+ slides)
- System under heavy load
- Network latency

**Solutions:**

1. **Reduce slide count**
   - Try 5-8 slides instead of 15-20
   - Fewer slides = faster generation

2. **Use a faster model**
   - Switch to premium models (faster)
   - See [Configuration Guide](CONFIGURATION_GUIDE.md#model-selection-strategy)

3. **Disable images**
   - Images add 30-60 seconds
   - Set `DISABLE_IMAGE_GENERATION="true"`

4. **Check system resources**
   - Close other applications
   - Check available disk space
   - Restart Presenton if needed

5. **Wait longer**
   - Free models can take 3-5 minutes
   - This is normal behavior

---

### API Errors

**Symptoms:**
- Error message: "API Error" or "Connection failed"
- Presentation generation fails
- Error code appears

**Causes:**
- Invalid API key
- API provider down
- Network connectivity issue
- Rate limit exceeded

**Solutions:**

1. **Check API key**
   ```bash
   # Verify key is set correctly
   docker logs presenton | grep "API_KEY"
   ```
   - Ensure key is not expired
   - Verify key has correct permissions
   - Try a fresh key from provider

2. **Check internet connection**
   ```bash
   # Test connectivity
   curl https://api.openai.com/v1/models
   ```
   - Verify you can reach the API
   - Check firewall settings
   - Try from different network

3. **Check API provider status**
   - OpenAI: https://status.openai.com
   - Google: https://status.cloud.google.com
   - Anthropic: Check their status page

4. **Check rate limits**
   - You may have exceeded API limits
   - Wait a few minutes and retry
   - Upgrade to higher tier if needed

5. **Restart Presenton**
   ```bash
   docker restart presenton
   ```

---

### Model Selection Issues

**Symptoms:**
- "Model not found" error
- Model doesn't work
- Wrong model being used

**Causes:**
- Model name is incorrect
- Model not available in region
- API key doesn't have access
- Model is deprecated

**Solutions:**

1. **Verify model name**
   - Check [Configuration Guide](CONFIGURATION_GUIDE.md) for correct names
   - Model names are case-sensitive
   - Example: `gpt-4-turbo` not `GPT-4-TURBO`

2. **Check model availability**
   - Some models are region-restricted
   - Some models require specific API tiers
   - Try a different model

3. **Verify API access**
   - Ensure your API key has access to the model
   - Check API provider documentation
   - Try a model you know works

4. **Try a different model**
   - If one model fails, try another
   - See [User Guide → Model Selection](USER_GUIDE.md#understanding-model-selection)

---

### Streaming Not Working

**Symptoms:**
- Presentation doesn't stream
- Content appears all at once
- No real-time updates

**Causes:**
- Browser doesn't support streaming
- Network connection issue
- Streaming disabled in config
- Firewall blocking streaming

**Solutions:**

1. **Check browser compatibility**
   - Use Chrome, Firefox, Safari, or Edge
   - Update to latest version
   - Try a different browser

2. **Check network connection**
   - Verify stable internet connection
   - Try from different network
   - Check firewall settings

3. **Clear browser cache**
   ```
   Ctrl+Shift+Delete (Windows)
   Cmd+Shift+Delete (Mac)
   ```

4. **Restart Presenton**
   ```bash
   docker restart presenton
   ```

---

### Database Errors

**Symptoms:**
- "Database error" message
- Can't save presentations
- History not loading

**Causes:**
- Database file corrupted
- Disk space full
- Permission issues
- Database locked

**Solutions:**

1. **Check disk space**
   ```bash
   df -h /app_data
   ```
   - Ensure at least 1GB free
   - Delete old presentations if needed

2. **Check permissions**
   ```bash
   ls -la /app_data/
   ```
   - Ensure Docker has write access
   - Fix permissions if needed

3. **Restart Presenton**
   ```bash
   docker restart presenton
   ```

4. **Reset database** (last resort)
   ```bash
   # Backup first
   cp /app_data/fastapi.db /app_data/fastapi.db.backup
   
   # Remove database
   rm /app_data/fastapi.db
   
   # Restart Presenton
   docker restart presenton
   ```

---

### Images Not Generating

**Symptoms:**
- Slides have no images
- Image generation fails
- "Image generation error"

**Causes:**
- Image generation disabled
- Image provider API key invalid
- Image provider down
- Unsupported image format

**Solutions:**

1. **Check if images are enabled**
   ```bash
   # Verify DISABLE_IMAGE_GENERATION is not set to true
   docker logs presenton | grep "IMAGE_GENERATION"
   ```

2. **Verify image provider**
   - Check `IMAGE_PROVIDER` is set
   - Verify API key is correct
   - Try a different provider

3. **Check image provider status**
   - DALL-E: https://status.openai.com
   - Gemini: https://status.cloud.google.com
   - Pexels: https://www.pexels.com
   - Pixabay: https://pixabay.com

4. **Try different provider**
   ```bash
   # Switch to Pexels (free stock photos)
   docker run -e IMAGE_PROVIDER="pexels" -e PEXELS_API_KEY="..." ...
   ```

5. **Disable images temporarily**
   ```bash
   docker run -e DISABLE_IMAGE_GENERATION="true" ...
   ```

---

### Poor Quality Content

**Symptoms:**
- Content is generic or irrelevant
- Slides lack detail
- Information is incorrect

**Causes:**
- Using free models (lower quality)
- Topic too vague
- Model doesn't understand context
- Slide count too low

**Solutions:**

1. **Use a premium model**
   - Switch to Claude, GPT-4, or Gemini
   - See [Configuration Guide](CONFIGURATION_GUIDE.md)

2. **Be more specific in topic**
   - Instead of: "Business"
   - Try: "Q4 2025 Sales Report for Tech Industry"

3. **Increase slide count**
   - More slides = more detail
   - Try 12-15 slides instead of 8

4. **Adjust verbosity**
   - Set to "text-heavy" for more detail
   - See [User Guide](USER_GUIDE.md#creating-presentations)

5. **Try a different model**
   - Each model has different strengths
   - Experiment to find best fit

---

### Presentation Won't Download

**Symptoms:**
- Download button doesn't work
- File doesn't save
- Browser shows error

**Causes:**
- Browser download settings
- File too large
- Disk space full
- Network interrupted

**Solutions:**

1. **Check browser download settings**
   - Ensure downloads are enabled
   - Check download folder permissions
   - Try a different browser

2. **Check file size**
   - PPTX files are typically 5-50 MB
   - If larger, try fewer slides or images

3. **Check disk space**
   ```bash
   df -h
   ```
   - Ensure at least 100 MB free
   - Delete old files if needed

4. **Try different format**
   - If PPTX fails, try PDF
   - If PDF fails, try PPTX

5. **Restart browser**
   - Close and reopen browser
   - Clear cache
   - Try again

---

### Can't Access Presenton

**Symptoms:**
- "Connection refused"
- "Cannot reach server"
- Page won't load

**Causes:**
- Presenton not running
- Wrong port
- Firewall blocking
- Network issue

**Solutions:**

1. **Check if Presenton is running**
   ```bash
   docker ps | grep presenton
   ```
   - If not running, start it:
   ```bash
   docker run -it --name presenton -p 5000:80 -v "./app_data:/app_data" ghcr.io/presenton/presenton:latest
   ```

2. **Check correct port**
   - Default: http://localhost:5000
   - If you changed port, use that instead
   - Example: http://localhost:8080

3. **Check firewall**
   - Ensure port 5000 is open
   - Check Windows Firewall or macOS settings
   - Try disabling firewall temporarily

4. **Check network**
   - Verify internet connection
   - Try from different device
   - Check router settings

5. **Check Docker**
   ```bash
   docker logs presenton
   ```
   - Look for error messages
   - Restart Docker if needed

---

## Error Codes and Meanings

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check your input parameters |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | API key doesn't have permission |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limited | Wait and retry later |
| 500 | Server Error | Restart Presenton |
| 503 | Service Unavailable | API provider is down |

---

## Performance Problems

### Slow Generation

**Check:**
1. Slide count (reduce to 5-8)
2. Model selection (use faster model)
3. Image generation (disable if not needed)
4. System resources (close other apps)

### High Memory Usage

**Check:**
1. Number of concurrent presentations
2. Slide count per presentation
3. Image generation enabled
4. System available memory

### Network Issues

**Check:**
1. Internet connection speed
2. API provider latency
3. Firewall settings
4. Network congestion

---

## Memory and Resource Issues

### "Out of Memory" Error

**Solutions:**
1. Reduce slide count
2. Disable image generation
3. Close other applications
4. Increase Docker memory limit

### "Disk Space Full"

**Solutions:**
1. Delete old presentations
2. Clear temporary files
3. Expand storage
4. Archive old data

---

## When to Escalate

Contact support if:

1. **Persistent API errors** — After trying all solutions
2. **Database corruption** — Can't recover
3. **Hardware issues** — Out of memory, disk full
4. **Security concerns** — Suspicious activity
5. **Feature requests** — Want new functionality

---

## Getting Help

### Gather Information

Before contacting support, collect:

1. **Error message** — Exact text of error
2. **Logs** — Last 50 lines from Docker logs
3. **Configuration** — Environment variables used
4. **Steps to reproduce** — How to trigger the issue
5. **System info** — OS, Docker version, hardware

### View Logs

```bash
# Last 50 lines
docker logs presenton | tail -50

# Save to file
docker logs presenton > presenton.log

# Real-time logs
docker logs -f presenton
```

### Share Logs Safely

1. Remove sensitive information (API keys)
2. Save to file
3. Share with support team

---

## Log Locations

**Docker logs:**
```bash
docker logs presenton
```

**Application logs:**
```
/app_data/logs/
```

**Database:**
```
/app_data/fastapi.db
```

---

## Frequently Asked Questions

**Q: How long should generation take?**  
A: 2-5 minutes is normal. Free models are slower than premium.

**Q: Why are images not generating?**  
A: Check image provider is configured and API key is valid.

**Q: Can I cancel a presentation?**  
A: Not currently. Wait for completion or restart Presenton.

**Q: How do I reset everything?**  
A: Delete `/app_data/` folder and restart Presenton.

---

## Next Steps

1. **Try the solution** — Follow steps for your issue
2. **Test** — Create a presentation to verify fix
3. **Report** — If issue persists, contact support
4. **Document** — Share logs and steps taken

---

## Need Help?

- **Discord Community**: [Join our Discord](https://discord.gg/9ZsKKxudNE)
- **GitHub Issues**: [Report a bug](https://github.com/presenton/presenton/issues)
- **Email**: suraj@presenton.ai
- **Documentation**: [Table of Contents](TABLE_OF_CONTENTS.md)
