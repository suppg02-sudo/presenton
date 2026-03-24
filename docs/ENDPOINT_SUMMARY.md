# Metrics Dashboard Endpoint - Quick Reference

## Endpoint Details

```
GET /api/v1/metrics/dashboard
```

## Request

### URL
```
http://localhost:8000/api/v1/metrics/dashboard
```

### Query Parameters
- `hours` (optional, default: 24) - Number of hours to look back

### Examples
```bash
# Last 24 hours (default)
GET /api/v1/metrics/dashboard

# Last 7 days
GET /api/v1/metrics/dashboard?hours=168

# Last 30 days
GET /api/v1/metrics/dashboard?hours=720
```

## Response

### Status Code
- **200 OK** - Success
- **500 Internal Server Error** - Database error

### Response Body (200 OK)
```json
{
  "total_requests": 150,
  "success_count": 145,
  "error_count": 5,
  "success_rate": 96.67,
  "avg_response_time_ms": 1250.5,
  "model_usage": {
    "gpt-4": 75,
    "gpt-3.5-turbo": 75
  },
  "avg_tokens_input": 450.25,
  "avg_tokens_output": 320.75,
  "last_updated": "2024-02-18T12:30:45.123456"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_requests` | integer | Total number of requests in the time period |
| `success_count` | integer | Number of successful requests |
| `error_count` | integer | Number of failed requests |
| `success_rate` | float | Success rate as a percentage (0.0-100.0) |
| `avg_response_time_ms` | float | Average response time in milliseconds |
| `model_usage` | object | Count of requests per model |
| `avg_tokens_input` | float | Average input tokens per request |
| `avg_tokens_output` | float | Average output tokens per request |
| `last_updated` | string | ISO 8601 timestamp of last update |

### Error Response (500)
```json
{
  "detail": "Failed to retrieve metrics: [error message]"
}
```

## Implementation Files

### Core Implementation
- **File:** `/home/usdaw/presenton/servers/fastapi/api/v1/metrics_routes.py`
- **Lines:** 188
- **Key Components:**
  - `DashboardResponse` - Pydantic response model
  - `get_metrics_dashboard()` - Endpoint handler
  - `_get_model_usage_breakdown()` - Helper function

### Integration
- **File:** `/home/usdaw/presenton/servers/fastapi/api/main.py`
- **Changes:**
  - Import: `from api.v1.metrics_routes import METRICS_ROUTER`
  - Registration: `app.include_router(METRICS_ROUTER)`

### Testing
- **File:** `/home/usdaw/presenton/servers/fastapi/tests/test_metrics_routes.py`
- **Tests:** 6 unit tests

### Documentation
- **File:** `/home/usdaw/presenton/servers/fastapi/api/v1/METRICS_API.md`
- **Sections:** 10+ comprehensive sections

## Usage Examples

### cURL
```bash
# Get metrics
curl -X GET "http://localhost:8000/api/v1/metrics/dashboard"

# Get metrics for last 7 days
curl -X GET "http://localhost:8000/api/v1/metrics/dashboard?hours=168"

# Pretty print JSON
curl -X GET "http://localhost:8000/api/v1/metrics/dashboard" | jq
```

### Python (requests)
```python
import requests
import json

# Get metrics
response = requests.get("http://localhost:8000/api/v1/metrics/dashboard")
metrics = response.json()

# Display results
print(f"Total Requests: {metrics['total_requests']}")
print(f"Success Rate: {metrics['success_rate']}%")
print(f"Avg Response Time: {metrics['avg_response_time_ms']}ms")
print(f"Model Usage: {json.dumps(metrics['model_usage'], indent=2)}")
```

### Python (httpx - async)
```python
import httpx
import asyncio

async def get_metrics():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/metrics/dashboard")
        metrics = response.json()
        print(f"Success Rate: {metrics['success_rate']}%")

asyncio.run(get_metrics())
```

### JavaScript (fetch)
```javascript
// Get metrics
fetch('http://localhost:8000/api/v1/metrics/dashboard')
  .then(response => response.json())
  .then(metrics => {
    console.log(`Total Requests: ${metrics.total_requests}`);
    console.log(`Success Rate: ${metrics.success_rate}%`);
    console.log(`Avg Response Time: ${metrics.avg_response_time_ms}ms`);
    console.log('Model Usage:', metrics.model_usage);
  })
  .catch(error => console.error('Error:', error));
```

### JavaScript (async/await)
```javascript
async function getMetrics() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/metrics/dashboard');
    const metrics = await response.json();
    
    console.log(`Total Requests: ${metrics.total_requests}`);
    console.log(`Success Rate: ${metrics.success_rate}%`);
    console.log(`Avg Response Time: ${metrics.avg_response_time_ms}ms`);
    console.log('Model Usage:', metrics.model_usage);
  } catch (error) {
    console.error('Error:', error);
  }
}

getMetrics();
```

### React Component
```jsx
import { useEffect, useState } from 'react';

export function MetricsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/v1/metrics/dashboard')
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>Metrics Dashboard</h2>
      <p>Total Requests: {metrics.total_requests}</p>
      <p>Success Rate: {metrics.success_rate}%</p>
      <p>Avg Response Time: {metrics.avg_response_time_ms}ms</p>
      <h3>Model Usage</h3>
      <ul>
        {Object.entries(metrics.model_usage).map(([model, count]) => (
          <li key={model}>{model}: {count}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Testing

### Run Unit Tests
```bash
cd /home/usdaw/presenton/servers/fastapi
pytest tests/test_metrics_routes.py -v
```

### Run Specific Test
```bash
pytest tests/test_metrics_routes.py::test_dashboard_response_model_validation -v
```

### Run with Coverage
```bash
pytest tests/test_metrics_routes.py --cov=api.v1.metrics_routes
```

## Integration Points

### Dependencies
- `services.database.get_async_session` - Database session
- `services.metrics_service.get_metrics_summary` - Metrics aggregation
- `models.sql.metrics.MetricsRecord` - Metrics data model

### Related Endpoints
- `/api/v1/ppt/*` - Presentation endpoints
- `/api/v1/webhook/*` - Webhook endpoints
- `/api/v1/mock/*` - Mock endpoints

## Performance Considerations

- **Query Time:** O(n) where n = number of metrics in time period
- **Caching:** Consider adding Redis caching for frequently accessed data
- **Rate Limiting:** Consider adding rate limiting to prevent abuse
- **Pagination:** Consider adding pagination for large datasets

## Future Enhancements

1. Add caching (Redis)
2. Add time-series data endpoint
3. Add filtering by model name
4. Add export functionality (CSV, JSON)
5. Add webhook notifications for alerts
6. Add rate limiting
7. Add pagination
8. Add aggregation by time intervals (hourly, daily, weekly)

## Troubleshooting

### 500 Error
- Check database connection
- Check metrics table exists
- Check logs for detailed error message

### Empty Results
- Check if metrics have been recorded
- Verify time range (hours parameter)
- Check database for metrics records

### Slow Response
- Check database query performance
- Consider adding indexes
- Consider implementing caching

## Support

For issues or questions:
1. Check `/home/usdaw/presenton/servers/fastapi/api/v1/METRICS_API.md`
2. Review unit tests in `tests/test_metrics_routes.py`
3. Check metrics service documentation in `services/METRICS_SERVICE_README.md`
