# Presenton Performance Testing Guide

## Overview

This guide explains how to run the Presenton performance test suite (Tests 18-20) to establish performance baselines and measure system performance under various load conditions.

## Test Suite Components

### Test 18: Baseline Normal-Load Performance
**Purpose**: Establish baseline performance metrics for sequential presentation creation

**What it measures**:
- Response time for each presentation creation request
- Average, minimum, and maximum response times
- Standard deviation of response times
- Throughput (presentations per minute)
- Success rate

**Configuration**:
- Creates 5 presentations sequentially
- 0.5 second delay between requests
- Measures wall-clock time (not CPU time)

**Expected Results**:
- Baseline response time: 5-15 seconds per presentation
- Throughput: 4-12 presentations per minute
- Success rate: 100% (or close to it)

### Test 19: Concurrent Presentation Creation
**Purpose**: Measure system performance under concurrent load

**What it measures**:
- Response times for concurrent requests
- Comparison with sequential baseline
- Success rate under concurrent load
- Throughput improvement from parallelization
- Queue behavior and timeout patterns

**Configuration**:
- Creates 5 presentations concurrently
- Uses 3 worker threads
- Measures wall-clock time for all requests to complete

**Expected Results**:
- Concurrent time should be less than sequential time
- Throughput improvement: 20-50% (depending on I/O bottlenecks)
- Success rate: 100% (or close to it)

### Test 20: Streaming Performance & Report Generation
**Purpose**: Measure streaming response characteristics and generate comprehensive report

**What it measures**:
- Time To First Byte (TTFB)
- Chunk delivery rate (chunks per second)
- Streaming response consistency
- Overall streaming performance

**Configuration**:
- Measures 3 streaming requests
- Tracks chunk delivery metrics
- Generates comprehensive performance report

**Expected Results**:
- TTFB: 0.1-0.5 seconds
- Chunk rate: 10-50 chunks per second
- Consistent delivery (low variance)

## Running the Tests

### Prerequisites

1. **Presenton API Running**:
   ```bash
   docker-compose up -d
   ```

2. **Python Dependencies**:
   ```bash
   pip install requests
   ```

### Running the Full Test Suite

```bash
cd /home/usdaw/presenton
python3 performance_tests.py
```

This will:
1. Run Test 18 (Baseline Normal-Load)
2. Run Test 19 (Concurrent Load)
3. Run Test 20 (Streaming Performance)
4. Generate `performance_baseline_report.md`
5. Save metrics to `performance_baseline_report.json`

### Running Individual Tests

You can modify `performance_tests.py` to run individual tests:

```python
# Run only Test 18
runner = PerformanceTestRunner()
baseline_metrics = runner.test_baseline_normal_load(num_presentations=5)
runner.save_report()
```

## Output Files

### performance_baseline_report.md
Comprehensive markdown report containing:
- Executive summary
- Summary metrics table
- Detailed test results
- ASCII performance graphs
- Comparative analysis (sequential vs concurrent)
- Streaming performance analysis
- Optimization recommendations
- Baseline reference for future comparisons

### performance_baseline_report.json
Machine-readable JSON file with all metrics for:
- Programmatic analysis
- Trend tracking
- Integration with monitoring systems

## Interpreting Results

### Response Time Analysis

**Good Performance**:
- Average response time: < 15 seconds
- Standard deviation: < 5 seconds
- Min/Max ratio: < 3x

**Warning Signs**:
- Average response time: > 20 seconds
- High standard deviation (> 50% of average)
- Frequent timeouts

### Throughput Analysis

**Good Performance**:
- Sequential: > 4 presentations/minute
- Concurrent: > 6 presentations/minute
- Improvement: > 20%

**Warning Signs**:
- Sequential: < 3 presentations/minute
- Concurrent: < 4 presentations/minute
- No improvement from concurrency

### Success Rate Analysis

**Good Performance**:
- Success rate: 100%
- No timeout errors
- No resource exhaustion

**Warning Signs**:
- Success rate: < 95%
- Increasing failures under concurrent load
- Timeout errors

## Optimization Recommendations

### If Response Time is High

1. **Profile LLM Calls**:
   - Check OpenRouter API response times
   - Consider model selection
   - Implement request caching

2. **Optimize Database**:
   - Add indexes on frequently queried columns
   - Consider connection pooling
   - Profile slow queries

3. **Implement Caching**:
   - Cache presentation outlines
   - Cache slide layouts
   - Cache image generation results

### If Concurrent Performance is Poor

1. **Increase Worker Pool**:
   - Modify `max_workers` parameter
   - Monitor resource usage
   - Find optimal worker count

2. **Optimize I/O**:
   - Use async/await for I/O operations
   - Implement connection pooling
   - Reduce database round-trips

3. **Add Rate Limiting**:
   - Implement request queuing
   - Add backpressure handling
   - Prevent resource exhaustion

### If Streaming Performance is Poor

1. **Optimize Chunk Size**:
   - Experiment with different chunk sizes
   - Balance between latency and throughput
   - Monitor network utilization

2. **Reduce TTFB**:
   - Optimize initial request processing
   - Implement request prioritization
   - Reduce startup overhead

## Tracking Performance Over Time

### Creating a Performance Trend

1. **Run tests regularly** (e.g., weekly):
   ```bash
   python3 performance_tests.py
   ```

2. **Archive reports**:
   ```bash
   cp performance_baseline_report.md reports/baseline_$(date +%Y%m%d).md
   cp performance_baseline_report.json reports/baseline_$(date +%Y%m%d).json
   ```

3. **Compare results**:
   - Track average response time
   - Monitor throughput trends
   - Alert on regressions (> 10% degradation)

### Regression Detection

Create a simple script to detect performance regressions:

```python
import json

def check_regression(current_file, baseline_file, threshold=0.10):
    with open(current_file) as f:
        current = json.load(f)
    with open(baseline_file) as f:
        baseline = json.load(f)
    
    for curr, base in zip(current, baseline):
        if curr['test_name'] == base['test_name']:
            response_time_change = (
                (curr['avg_response_time'] - base['avg_response_time']) 
                / base['avg_response_time']
            )
            if response_time_change > threshold:
                print(f"⚠️  REGRESSION: {curr['test_name']}")
                print(f"   Response time increased by {response_time_change*100:.1f}%")
```

## Troubleshooting

### "Connection refused" Error

**Problem**: Cannot connect to API
**Solution**:
1. Verify Presenton is running: `docker-compose ps`
2. Check port 5001 is accessible: `curl http://localhost:5001/api/v1/ppt/all`
3. Check firewall rules

### High Failure Rate

**Problem**: Many requests failing
**Solution**:
1. Check API logs: `docker-compose logs presenton`
2. Verify database is accessible
3. Check OpenRouter API key is valid
4. Reduce concurrent worker count

### Timeout Errors

**Problem**: Requests timing out
**Solution**:
1. Increase `REQUEST_TIMEOUT` in script
2. Check API performance: `docker stats presenton`
3. Reduce concurrent load
4. Check network latency

### Inconsistent Results

**Problem**: Results vary significantly between runs
**Solution**:
1. Run tests multiple times and average results
2. Ensure consistent system load
3. Check for background processes
4. Verify network stability

## Advanced Usage

### Custom Test Scenarios

Modify `performance_tests.py` to test custom scenarios:

```python
# Test with different slide counts
runner.test_baseline_normal_load(num_presentations=10)

# Test with more concurrent workers
runner.test_concurrent_load(num_presentations=10, max_workers=5)

# Test with different languages
# (modify _create_test_payload method)
```

### Integration with CI/CD

Add performance tests to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: python3 performance_tests.py
  
- name: Check for Regressions
  run: python3 check_regression.py
```

## Best Practices

1. **Run tests in isolation**: Avoid running other tests simultaneously
2. **Use consistent hardware**: Run tests on the same machine for comparisons
3. **Warm up the system**: Run a few requests before measuring
4. **Multiple runs**: Run tests multiple times and average results
5. **Document changes**: Note any system changes that might affect performance
6. **Monitor resources**: Check CPU, memory, and network during tests

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API logs: `docker-compose logs presenton`
3. Check system resources: `docker stats presenton`
4. Review performance report for recommendations

## References

- [Presenton Documentation](README.md)
- [API Endpoints](ENDPOINT_SUMMARY.md)
- [Performance Baseline Report](performance_baseline_report.md)
