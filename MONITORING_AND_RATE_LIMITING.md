# Presenton Monitoring & Rate Limiting Guide

**Version**: 2.0.0  
**Date**: February 18, 2026  
**Status**: Production Ready

---

## Overview

Presenton now includes comprehensive monitoring and rate limiting capabilities to handle OpenRouter free tier API constraints gracefully.

### Key Features

✅ **Exponential Backoff** - Automatic retry with intelligent delays  
✅ **Request Queuing** - Prevents rate limit cascades  
✅ **Quota Monitoring** - Tracks API usage in real-time  
✅ **Model Health Monitoring** - Tracks performance per model  
✅ **Monitoring API Endpoints** - Access health data via REST API  

---

## 1. Rate Limiting with Exponential Backoff

### What It Does

When OpenRouter returns HTTP 429 (Too Many Requests):
1. Detects the error
2. Calculates wait time using exponential backoff: 1s → 2s → 4s → 8s → 16s → 32s → 60s (capped)
3. Automatically retries after waiting
4. Logs attempt number and suggested wait time

### Configuration

**Location**: `servers/fastapi/utils/rate_limiter.py`

```python
RateLimiter(
    initial_backoff_seconds=1.0,    # Start with 1 second
    max_backoff_seconds=60.0,       # Cap at 60 seconds
    max_retries=5,                  # Max 5 retry attempts
)
```

### Usage

The rate limiter is used internally by the LLM client. No configuration needed for basic usage.

### Monitor Rate Limiter Status

```bash
curl http://localhost:8000/api/v1/monitoring/rate-limiter
```

**Response Example**:
```json
{
  "status": "rate_limiter",
  "data": {
    "retry_count": 2,
    "max_retries": 5,
    "rate_limited": false,
    "wait_until": null,
    "last_rate_limit_time": "2026-02-18T23:24:00.000Z"
  }
}
```

---

## 2. Request Queuing

### What It Does

Manages concurrent API requests to prevent overload:
1. Queues requests in FIFO order
2. Limits concurrent requests (default: 2)
3. Enforces minimum delay between requests (default: 0.5s)
4. Processes queue in order while respecting limits

### Configuration

**Location**: `servers/fastapi/utils/request_queue.py`

```python
RequestQueue(
    max_concurrent=2,           # Max 2 concurrent requests
    min_delay_seconds=0.5,      # Wait 0.5s between requests
)
```

### Benefits

- **Prevents Rate Limiting**: Spreading requests over time
- **Improves Success Rate**: No cascade failures
- **Fair Access**: FIFO ordering ensures fairness

### Monitor Queue Status

```bash
curl http://localhost:8000/api/v1/monitoring/queue
```

**Response Example**:
```json
{
  "status": "queue",
  "data": {
    "queue_size": 3,
    "active_requests": 2,
    "max_concurrent": 2,
    "min_delay_seconds": 0.5,
    "total_queued": 47,
    "total_processed": 44,
    "last_request_time": "2026-02-18T23:24:21.000Z"
  }
}
```

---

## 3. OpenRouter Quota Monitoring

### What It Does

Tracks API usage patterns:
1. Counts requests per minute/hour
2. Monitors rate limit hits
3. Estimates quota usage percentage
4. Provides status recommendations

### Quota Status Levels

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ HEALTHY | < 50% usage | Continue normally |
| ⚠️ WARNING | 50-80% usage | Monitor closely |
| 🔴 CRITICAL | 80-95% usage | Reduce request rate |
| ❌ OVERLOADED | > 95% usage | Immediate throttling |

### Monitor Quota Status

```bash
curl http://localhost:8000/api/v1/monitoring/quota
```

**Response Example**:
```json
{
  "status": "quota",
  "data": {
    "requests_per_minute": 2.5,
    "requests_per_hour": 47,
    "estimated_quota_percent": 4.2,
    "rate_limit_hits": 2,
    "errors": 1,
    "total_tokens_used": 5428,
    "top_models": [
      ["arcee-ai/trinity-large-preview:free", 8],
      ["nvidia/nemotron-nano-9b-v2:free", 2],
      ["meta-llama/llama-3.2-3b-instruct:free", 1]
    ],
    "status": "✅ HEALTHY - Low usage"
  }
}
```

---

## 4. Model Health Monitoring

### What It Does

Tracks performance per model:
1. Success/failure rates
2. Average response times
3. Consecutive failures
4. Automatic fallback recommendations

### Model Status

| Status | Success Rate | Action |
|--------|--------------|--------|
| ✅ Healthy | ≥ 95% | Preferred |
| ⚠️ Degraded | 80-95% | Monitor, can use |
| 🔴 Unavailable | < 80% | Avoid, fallback |

### Automatic Fallback

If a model fails 3+ times consecutively:
1. Model marked as "unavailable"
2. Automatic rotation to healthy model
3. Recommendation system suggests best alternative

### Monitor Model Health

```bash
curl http://localhost:8000/api/v1/monitoring/models
```

**Response Example**:
```json
{
  "status": "models",
  "summary": {
    "total_models_monitored": 3,
    "healthy_models": 2,
    "degraded_models": 1,
    "unavailable_models": 0,
    "healthy_list": ["arcee-ai/trinity-large-preview:free", "nvidia/nemotron-nano-9b-v2:free"],
    "degraded_list": ["meta-llama/llama-3.2-3b-instruct:free"],
    "unavailable_list": [],
    "recommended_model": "arcee-ai/trinity-large-preview:free"
  },
  "details": {
    "arcee-ai/trinity-large-preview:free": {
      "model": "arcee-ai/trinity-large-preview:free",
      "status": "✅ healthy",
      "success_rate_percent": 100.0,
      "success_count": 8,
      "failure_count": 0,
      "avg_response_time_ms": 7289.5,
      "total_tokens": 4582,
      "consecutive_failures": 0,
      "last_used": "2026-02-18T23:24:21.000Z"
    }
  }
}
```

---

## 5. Monitoring API Endpoints

### Available Endpoints

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/api/v1/monitoring/rate-limiter` | Rate limit status | Check if backoff active |
| `/api/v1/monitoring/queue` | Request queue status | Monitor concurrency |
| `/api/v1/monitoring/quota` | API quota usage | Track usage percentage |
| `/api/v1/monitoring/models` | Model health | Monitor performance |
| `/api/v1/monitoring/health` | Complete health check | Full system status |
| `/api/v1/monitoring/summary` | Quick summary | Dashboard display |

### Quick Health Check

```bash
curl http://localhost:8000/api/v1/monitoring/summary
```

**Response Example**:
```json
{
  "system_status": "operational",
  "quota_status": "✅ HEALTHY - Low usage",
  "quota_usage_percent": 4.2,
  "rate_limit_hits": 2,
  "active_requests": 1,
  "queue_size": 0,
  "healthy_models": 2,
  "model_recommendation": "arcee-ai/trinity-large-preview:free"
}
```

---

## 6. Integration with LLM Client

### How It Works

When `llm_client.py` makes a request:

1. **Rate Limiter**: Checks if waiting required from previous 429
2. **Request Queue**: Queues request, waits for capacity
3. **Executes**: Makes actual API call
4. **On Success**: Records model success, resets rate limiter
5. **On 429**: Records rate limit hit, calculates backoff, retries
6. **On Error**: Records model failure, checks for rotation
7. **Quota Monitor**: Records usage for quota tracking

### Flow Diagram

```
Request → Rate Limiter Check → Request Queue → API Call
                                                   ↓
                                         Success → Record Success
                                                → Reset Backoff
                                                → Update Quota
                                                → Return Result
                                           ↓
                                         429 → Record Rate Limit
                                              → Calculate Backoff
                                              → Wait & Retry
                                           ↓
                                         Error → Record Failure
                                              → Check Model Rotation
                                              → Try Fallback
```

---

## 7. Best Practices

### For Users

1. **Monitor Quota Regularly**
   ```bash
   curl http://localhost:8000/api/v1/monitoring/summary | jq '.quota_usage_percent'
   ```

2. **Check Model Health Before High-Volume Work**
   ```bash
   curl http://localhost:8000/api/v1/monitoring/models
   ```

3. **Set Up Alerts**
   - Alert when quota_usage_percent > 80%
   - Alert when rate_limit_hits > 5 in last hour
   - Alert when healthy_models < 1

### For Operations

1. **Daily Check**
   ```bash
   curl http://localhost:8000/api/v1/monitoring/health > daily_health.json
   ```

2. **Monitor Trends**
   - Track requests_per_minute over time
   - Watch for increasing response times
   - Monitor model rotation frequency

3. **Capacity Planning**
   - If quota_usage > 75%, reduce concurrent requests
   - If rate_limit_hits > 10, increase min_delay_seconds
   - If models keep failing, check OpenRouter status

---

## 8. Troubleshooting

### Issue: Rate Limiting (429 Errors)

**Symptoms**: Frequent 429 errors in logs

**Solutions**:
1. Increase `min_delay_seconds` in request_queue.py
2. Decrease `max_concurrent` in request_queue.py
3. Reduce incoming request rate from clients
4. Check quota_status to see current usage

```bash
# Check current settings
curl http://localhost:8000/api/v1/monitoring/queue
```

### Issue: High Response Times

**Symptoms**: Response times > 20 seconds

**Solutions**:
1. Check model health (may be degraded)
2. Check queue size (requests waiting)
3. Check quota usage (may be near limit)
4. Consider rotating to healthier model

```bash
# Check model performance
curl http://localhost:8000/api/v1/monitoring/models | jq '.details[] | {model, status, avg_response_time_ms}'
```

### Issue: Models Marked Unavailable

**Symptoms**: All models show "unavailable"

**Solutions**:
1. Check OpenRouter service status
2. Verify API key is valid
3. Check rate limit hits (may be over quota)
4. Restart container to reset model stats

```bash
# Reset and restart
docker-compose restart presenton
```

---

## 9. Configuration Examples

### Conservative (Low Risk)

For production with strict reliability requirements:

```python
# Rate Limiter
initial_backoff_seconds=2.0
max_backoff_seconds=120.0
max_retries=7

# Request Queue
max_concurrent=1
min_delay_seconds=1.0
```

### Balanced (Recommended)

For typical production use:

```python
# Rate Limiter
initial_backoff_seconds=1.0
max_backoff_seconds=60.0
max_retries=5

# Request Queue
max_concurrent=2
min_delay_seconds=0.5
```

### Aggressive (High Throughput)

For low-risk environments:

```python
# Rate Limiter
initial_backoff_seconds=0.5
max_backoff_seconds=30.0
max_retries=3

# Request Queue
max_concurrent=4
min_delay_seconds=0.2
```

---

## 10. Monitoring Dashboard Integration

### Metrics to Track

For external monitoring systems (Prometheus, Datadog, etc.):

1. **Rate Limiting**
   - `rate_limit_hits_total` - Total 429 hits
   - `rate_limit_hits_per_hour` - Current hourly rate
   - `backoff_active_bool` - Is system backing off

2. **Queue**
   - `queue_size_current` - Items waiting
   - `active_requests_current` - Ongoing requests
   - `total_processed_requests` - Lifetime count

3. **Quota**
   - `quota_usage_percent` - Current percentage
   - `requests_per_minute` - Current RPM
   - `requests_per_hour` - Current hourly count

4. **Models**
   - `healthy_models_count` - Number available
   - `model_success_rate_percent[model]` - Per model
   - `model_avg_response_time_ms[model]` - Per model

---

## 11. API Reference

### Rate Limiter API

```python
from utils.rate_limiter import (
    wait_if_rate_limited,      # Wait if needed
    handle_rate_limit_error,   # Record 429 error
    reset_rate_limiter,        # Reset after success
    get_rate_limiter_status,   # Get current status
)
```

### Request Queue API

```python
from utils.request_queue import (
    enqueue_request,   # Queue and execute request
    get_queue_stats,   # Get queue statistics
)
```

### Quota Monitor API

```python
from utils.quota_monitor import (
    record_request,      # Record successful request
    record_rate_limit,   # Record 429 error
    record_error,        # Record any error
    get_quota_status,    # Get quota status
    get_monitor_stats,   # Get all statistics
)
```

### Model Monitor API

```python
from utils.model_monitor import (
    record_model_success,      # Record success
    record_model_failure,      # Record failure
    should_rotate_model,       # Check rotation needed
    get_recommended_model,     # Get best model
    get_model_summary,         # Get summary
    get_all_models_status,     # Get all models
)
```

---

## Summary

Presenton v2.0.0 includes production-grade monitoring and rate limiting:

✅ **Exponential Backoff** prevents cascade failures  
✅ **Request Queuing** ensures fair access  
✅ **Quota Monitoring** tracks API usage  
✅ **Model Health** tracks per-model performance  
✅ **API Endpoints** expose all metrics  

These features work automatically with zero configuration needed. Monitor them via the `/api/v1/monitoring/` endpoints.

---

**Last Updated**: February 18, 2026  
**Version**: 2.0.0  
**Status**: Production Ready
