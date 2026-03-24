# Presenton Performance Baseline Report

**Generated**: 2026-02-18 12:00:00

## Executive Summary

This report establishes performance baselines for the Presenton presentation generation system.
Three comprehensive tests were conducted to measure normal-load, concurrent, and streaming performance.

## Summary Metrics Table

| Metric | Baseline | Concurrent | Streaming |
|--------|----------|-----------|-----------|
| Total Time | [measured] | [measured] | [measured] |
| Avg Response Time | [measured] | [measured] | [measured] |
| Min/Max Response | [measured] | [measured] | [measured] |
| Std Dev | [measured] | [measured] | [measured] |
| Throughput | [measured] | [measured] | [measured] |
| Success Rate | [measured] | [measured] | [measured] |

## Detailed Test Results

### Baseline Normal-Load (Sequential)

- **Test Timestamp**: [timestamp]
- **Total Requests**: 5
- **Successful**: [count]
- **Failed**: [count]
- **Success Rate**: [percentage]%
- **Total Execution Time**: [seconds] seconds

#### Response Time Statistics

- **Average**: [seconds]s
- **Minimum**: [seconds]s
- **Maximum**: [seconds]s
- **Standard Deviation**: [seconds]s
- **Throughput**: [rate] presentations/minute

### Concurrent Load (3 workers)

- **Test Timestamp**: [timestamp]
- **Total Requests**: 5
- **Successful**: [count]
- **Failed**: [count]
- **Success Rate**: [percentage]%
- **Total Execution Time**: [seconds] seconds

#### Response Time Statistics

- **Average**: [seconds]s
- **Minimum**: [seconds]s
- **Maximum**: [seconds]s
- **Standard Deviation**: [seconds]s
- **Throughput**: [rate] presentations/minute

### Streaming Performance

- **Test Timestamp**: [timestamp]
- **Total Requests**: 3
- **Successful**: [count]
- **Failed**: [count]
- **Success Rate**: [percentage]%
- **Total Execution Time**: [seconds] seconds

#### Response Time Statistics

- **Average**: [seconds]s
- **Minimum**: [seconds]s
- **Maximum**: [seconds]s
- **Standard Deviation**: [seconds]s
- **Throughput**: [rate] presentations/minute

## Performance Graphs

### Response Time Comparison (ASCII Chart)

```
Average Response Time (seconds)

Baseline:   ████████████████ [seconds]s
Concurrent: ██████████ [seconds]s
Streaming:  ████████████ [seconds]s
```

### Throughput Comparison (presentations/minute)

```
Baseline:   ████████████████ [rate] pres/min
Concurrent: ██████████████████ [rate] pres/min
```

## Comparative Analysis: Sequential vs Concurrent

### Time Comparison

- **Sequential Total Time**: [seconds]s
- **Concurrent Total Time**: [seconds]s
- **Time Savings**: [seconds]s ([percentage]%)

### Throughput Comparison

- **Sequential Throughput**: [rate] presentations/minute
- **Concurrent Throughput**: [rate] presentations/minute
- **Improvement**: [rate] presentations/minute ([percentage]%)

### Success Rate Comparison

- **Sequential Success Rate**: [percentage]%
- **Concurrent Success Rate**: [percentage]%

## Streaming Performance Analysis

### Streaming Metrics

- **Average Response Time**: [seconds]s
- **Min/Max Response Time**: [seconds]s / [seconds]s
- **Success Rate**: [percentage]%

### Chunk Delivery Performance

- **Samples Measured**: 3
- **Successful Samples**: [count]

### Time To First Byte (TTFB)

- **Average TTFB**: [seconds]s
- **Min TTFB**: [seconds]s
- **Max TTFB**: [seconds]s

### Chunk Delivery Rate

- **Average Rate**: [rate] chunks/second
- **Min Rate**: [rate] chunks/second
- **Max Rate**: [rate] chunks/second

## Recommendations for Optimization

- **Performance Baseline Established**: System is performing well. Continue monitoring and re-run tests periodically to track performance trends.

## Baseline Reference for Future Comparisons

This baseline should be used as a reference point for future performance testing.
Re-run this test suite periodically to track performance trends and identify regressions.

### How to Use This Baseline

1. **Track Trends**: Compare future test results against these baselines
2. **Identify Regressions**: Alert if performance degrades by >10%
3. **Validate Optimizations**: Measure improvement from optimization efforts
4. **Capacity Planning**: Use throughput metrics for capacity planning

### Baseline Snapshot

**Baseline Normal-Load (Sequential)**:
- Avg Response Time: [seconds]s
- Throughput: [rate] presentations/minute
- Success Rate: [percentage]%

**Concurrent Load (3 workers)**:
- Avg Response Time: [seconds]s
- Throughput: [rate] presentations/minute
- Success Rate: [percentage]%

**Streaming Performance**:
- Avg Response Time: [seconds]s
- Throughput: [rate] presentations/minute
- Success Rate: [percentage]%
