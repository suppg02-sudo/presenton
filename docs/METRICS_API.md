# Metrics API Documentation

## Overview

The Metrics API provides endpoints for retrieving LLM metrics and performance statistics. This API is designed to support monitoring and analytics dashboards.

## Endpoints

### GET /api/v1/metrics/dashboard

Returns aggregated metrics and statistics for the last 24 hours (or specified time period).

#### Request

```
GET /api/v1/metrics/dashboard?hours=24
```

**Query Parameters:**
- `hours` (optional, default: 24): Number of hours to look back for metrics

#### Response

**Status Code:** 200 OK

**Response Body:**
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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_requests` | integer | Total number of requests in the time period |
| `success_count` | integer | Number of successful requests |
| `error_count` | integer | Number of failed requests |
| `success_rate` | float | Success rate as a percentage (0.0-100.0) |
| `avg_response_time_ms` | float | Average response time in milliseconds |
| `model_usage` | object | Count of requests per model (model_name -> count) |
| `avg_tokens_input` | float | Average input tokens per request |
| `avg_tokens_output` | float | Average output tokens per request |
| `last_updated` | datetime | ISO 8601 timestamp of when metrics were last updated |

#### Error Responses

**Status Code:** 500 Internal Server Error

```json
{
  "detail": "Failed to retrieve metrics: [error message]"
}
```

## Usage Examples

### cURL

```bash
# Get metrics for the last 24 hours
curl -X GET "http://localhost:8000/api/v1/metrics/dashboard"

# Get metrics for the last 7 days
curl -X GET "http://localhost:8000/api/v1/metrics/dashboard?hours=168"
```

### Python (requests)

```python
import requests

# Get metrics
response = requests.get("http://localhost:8000/api/v1/metrics/dashboard")
metrics = response.json()

print(f"Total Requests: {metrics['total_requests']}")
print(f"Success Rate: {metrics['success_rate']}%")
print(f"Avg Response Time: {metrics['avg_response_time_ms']}ms")
```

### JavaScript (fetch)

```javascript
// Get metrics
const response = await fetch('http://localhost:8000/api/v1/metrics/dashboard');
const metrics = await response.json();

console.log(`Total Requests: ${metrics.total_requests}`);
console.log(`Success Rate: ${metrics.success_rate}%`);
console.log(`Avg Response Time: ${metrics.avg_response_time_ms}ms`);
```

## Implementation Details

### Data Source

The endpoint queries the `metrics` table in the SQLite database, which stores:
- Model name
- Input/output tokens
- Response time
- Request status (success/error/timeout)
- Timestamp

### Calculations

- **Success Rate**: `(successful_requests / total_requests) * 100`
- **Average Response Time**: Sum of all response times / total requests
- **Average Tokens**: Sum of tokens / total requests
- **Model Usage**: Count of requests grouped by model name

### Error Handling

- Database connection errors return HTTP 500
- Invalid query parameters are handled by FastAPI validation
- Empty result sets return zero values for all metrics

## Integration

The endpoint is registered in `/api/main.py`:

```python
from api.v1.metrics_routes import METRICS_ROUTER

app.include_router(METRICS_ROUTER)
```

### GET /api/v1/metrics/analytics

Returns comprehensive analytics report for a specified period.

#### Request

```
GET /api/v1/metrics/analytics?period=daily
```

**Query Parameters:**
- `period` (optional, default: daily): Period type - `daily`, `weekly`, or `monthly`

#### Response

**Status Code:** 200 OK

**Response Body:**
```json
{
  "period": "daily",
  "model_distribution": {
    "total_requests": 100,
    "models": {
      "gpt-4": {
        "count": 50,
        "percentage": 50.0,
        "successful": 48,
        "failed": 2,
        "avg_response_time_ms": 1200.5,
        "total_input_tokens": 25000,
        "total_output_tokens": 15000
      }
    },
    "period": {
      "start": "2024-02-17T12:00:00",
      "end": "2024-02-18T12:00:00"
    }
  },
  "performance_stats": {
    "avg_response_time_ms": 1200.5,
    "min_response_time_ms": 500.0,
    "max_response_time_ms": 2500.0,
    "avg_tokens_per_request": 400.0,
    "total_requests": 100,
    "successful_requests": 98,
    "failed_requests": 2,
    "success_rate": 98.0,
    "period": {
      "start": "2024-02-17T12:00:00",
      "end": "2024-02-18T12:00:00"
    }
  },
  "cost_analysis": {
    "total_requests": 100,
    "total_tokens": 4000000,
    "openrouter_cost": 0.0,
    "ollama_estimated_cost": 0.004,
    "savings": 0.004,
    "savings_percentage": 100.0,
    "period": {
      "start": "2024-02-17T12:00:00",
      "end": "2024-02-18T12:00:00"
    }
  },
  "summary": {
    "total_requests": 100,
    "successful_requests": 98,
    "failed_requests": 2,
    "success_rate": 98.0,
    "unique_models": 1
  },
  "generated_at": "2024-02-18T12:30:45.123456"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `period` | string | Period type (daily, weekly, monthly) |
| `model_distribution` | object | Model usage distribution and statistics |
| `performance_stats` | object | Performance metrics and statistics |
| `cost_analysis` | object | Cost analysis and savings calculation |
| `summary` | object | Summary statistics for the period |
| `generated_at` | datetime | ISO 8601 timestamp when report was generated |

#### Error Responses

**Status Code:** 400 Bad Request (invalid period)

```json
{
  "detail": "Invalid period: [error message]"
}
```

**Status Code:** 500 Internal Server Error

```json
{
  "detail": "Failed to generate analytics report: [error message]"
}
```

### GET /api/v1/metrics/analytics/daily

Convenience endpoint for daily analytics report (last 24 hours).

#### Request

```
GET /api/v1/metrics/analytics/daily
```

#### Response

**Status Code:** 200 OK

Returns AnalyticsResponse with `period: "daily"`

### GET /api/v1/metrics/analytics/weekly

Convenience endpoint for weekly analytics report (last 7 days).

#### Request

```
GET /api/v1/metrics/analytics/weekly
```

#### Response

**Status Code:** 200 OK

Returns AnalyticsResponse with `period: "weekly"`

### GET /api/v1/metrics/analytics/monthly

Convenience endpoint for monthly analytics report (last 30 days).

#### Request

```
GET /api/v1/metrics/analytics/monthly
```

#### Response

**Status Code:** 200 OK

Returns AnalyticsResponse with `period: "monthly"`

## Usage Examples

### cURL

```bash
# Get daily analytics
curl -X GET "http://localhost:8000/api/v1/metrics/analytics?period=daily"

# Get weekly analytics
curl -X GET "http://localhost:8000/api/v1/metrics/analytics?period=weekly"

# Get monthly analytics
curl -X GET "http://localhost:8000/api/v1/metrics/analytics?period=monthly"

# Use convenience endpoint
curl -X GET "http://localhost:8000/api/v1/metrics/analytics/daily"
```

### Python (requests)

```python
import requests

# Get analytics for a specific period
response = requests.get("http://localhost:8000/api/v1/metrics/analytics?period=weekly")
analytics = response.json()

print(f"Total Requests: {analytics['summary']['total_requests']}")
print(f"Success Rate: {analytics['summary']['success_rate']}%")
print(f"Unique Models: {analytics['summary']['unique_models']}")
print(f"Cost Savings: ${analytics['cost_analysis']['savings']:.4f}")
```

### JavaScript (fetch)

```javascript
// Get daily analytics
const response = await fetch('http://localhost:8000/api/v1/metrics/analytics/daily');
const analytics = await response.json();

console.log(`Total Requests: ${analytics.summary.total_requests}`);
console.log(`Success Rate: ${analytics.summary.success_rate}%`);
console.log(`Cost Savings: $${analytics.cost_analysis.savings.toFixed(4)}`);
```

## Testing

Unit tests are available in `tests/test_metrics_routes.py`:

```bash
pytest tests/test_metrics_routes.py -v
```

### GET /api/v1/metrics/export

Exports metrics in JSON or CSV format with optional date range filtering.

#### Request

```
GET /api/v1/metrics/export?format=json&start_date=2024-02-17&end_date=2024-02-18
```

**Query Parameters:**
- `format` (optional, default: json): Export format - `json` or `csv`
- `start_date` (optional): Start date in ISO format (YYYY-MM-DD or ISO 8601). If not provided, defaults to 24 hours ago
- `end_date` (optional): End date in ISO format (YYYY-MM-DD or ISO 8601). If not provided, defaults to now

#### Response (JSON Format)

**Status Code:** 200 OK

**Content-Type:** application/json

**Response Body:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "model_name": "gpt-4",
    "tokens_input": 450,
    "tokens_output": 320,
    "response_time_ms": 1250.5,
    "status": "success",
    "timestamp": "2024-02-18T12:30:45.123456+00:00",
    "error_message": null
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "model_name": "gpt-3.5-turbo",
    "tokens_input": 200,
    "tokens_output": 150,
    "response_time_ms": 800.0,
    "status": "success",
    "timestamp": "2024-02-18T12:25:30.654321+00:00",
    "error_message": null
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (UUID) for the metric record |
| `model_name` | string | Name of the LLM model used |
| `tokens_input` | integer | Number of input tokens |
| `tokens_output` | integer | Number of output tokens |
| `response_time_ms` | float | Response time in milliseconds |
| `status` | string | Request status (success, error, timeout) |
| `timestamp` | datetime | ISO 8601 timestamp of the request |
| `error_message` | string or null | Error message if status is error, otherwise null |

#### Response (CSV Format)

**Status Code:** 200 OK

**Content-Type:** text/csv

**Content-Disposition:** attachment; filename=metrics_export.csv

**Response Body:**
```csv
id,model_name,tokens_input,tokens_output,response_time_ms,status,timestamp,error_message
550e8400-e29b-41d4-a716-446655440000,gpt-4,450,320,1250.5,success,2024-02-18T12:30:45.123456+00:00,
550e8400-e29b-41d4-a716-446655440001,gpt-3.5-turbo,200,150,800.0,success,2024-02-18T12:25:30.654321+00:00,
```

#### Error Responses

**Status Code:** 400 Bad Request (invalid date format)

```json
{
  "detail": "Invalid date format. Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
}
```

**Status Code:** 422 Unprocessable Entity (invalid format parameter)

```json
{
  "detail": [
    {
      "type": "string_pattern",
      "loc": ["query", "format"],
      "msg": "String should match pattern '^(json|csv)$'",
      "input": "invalid"
    }
  ]
}
```

**Status Code:** 500 Internal Server Error

```json
{
  "detail": "Failed to export metrics: [error message]"
}
```

#### Usage Examples

### cURL

```bash
# Export metrics as JSON (last 24 hours)
curl -X GET "http://localhost:8000/api/v1/metrics/export?format=json"

# Export metrics as CSV (last 24 hours)
curl -X GET "http://localhost:8000/api/v1/metrics/export?format=csv" \
  -o metrics_export.csv

# Export metrics with date range (JSON)
curl -X GET "http://localhost:8000/api/v1/metrics/export?format=json&start_date=2024-02-17&end_date=2024-02-18"

# Export metrics with date range (CSV)
curl -X GET "http://localhost:8000/api/v1/metrics/export?format=csv&start_date=2024-02-17T00:00:00&end_date=2024-02-18T23:59:59" \
  -o metrics_export.csv
```

### Python (requests)

```python
import requests
import json
from datetime import datetime, timedelta

# Export as JSON
response = requests.get("http://localhost:8000/api/v1/metrics/export?format=json")
metrics = response.json()

print(f"Exported {len(metrics)} metrics")
for metric in metrics[:5]:  # Print first 5
    print(f"  {metric['model_name']}: {metric['response_time_ms']}ms")

# Export as CSV
response = requests.get("http://localhost:8000/api/v1/metrics/export?format=csv")
with open("metrics_export.csv", "w") as f:
    f.write(response.text)

# Export with date range
start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
end_date = datetime.utcnow().isoformat()
response = requests.get(
    "http://localhost:8000/api/v1/metrics/export",
    params={
        "format": "json",
        "start_date": start_date,
        "end_date": end_date
    }
)
metrics = response.json()
print(f"Metrics from last 7 days: {len(metrics)}")
```

### JavaScript (fetch)

```javascript
// Export as JSON
const response = await fetch('http://localhost:8000/api/v1/metrics/export?format=json');
const metrics = await response.json();

console.log(`Exported ${metrics.length} metrics`);
metrics.slice(0, 5).forEach(metric => {
  console.log(`  ${metric.model_name}: ${metric.response_time_ms}ms`);
});

// Export as CSV
const csvResponse = await fetch('http://localhost:8000/api/v1/metrics/export?format=csv');
const csvText = await csvResponse.text();
const blob = new Blob([csvText], { type: 'text/csv' });
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'metrics_export.csv';
a.click();

// Export with date range
const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
const endDate = new Date().toISOString();
const rangeResponse = await fetch(
  `http://localhost:8000/api/v1/metrics/export?format=json&start_date=${startDate}&end_date=${endDate}`
);
const rangeMetrics = await rangeResponse.json();
console.log(`Metrics from last 7 days: ${rangeMetrics.length}`);
```

## Related Services

- **analytics_service.py**: Core service for analytics operations
- **metrics_service.py**: Core service for metrics operations
- **MetricsRecord**: SQLModel for metrics data
- **database.py**: Database session management
