# Performance Testing - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Ensure Presenton is running
docker-compose up -d

# Verify API is accessible
curl http://localhost:5001/api/v1/ppt/all
```

### Run All Tests
```bash
cd /home/usdaw/presenton
python3 performance_tests.py
```

### View Results
```bash
# View comprehensive report
cat performance_baseline_report.md

# View raw metrics
cat performance_baseline_report.json
```

---

## 📊 What Gets Tested

| Test | Duration | What It Measures |
|------|----------|------------------|
| **Test 18** | ~30s | Sequential performance (5 presentations) |
| **Test 19** | ~20s | Concurrent performance (5 presentations, 3 workers) |
| **Test 20** | ~10s | Streaming performance (3 samples) |
| **Total** | ~60s | Complete baseline + report generation |

---

## 📈 Key Metrics Captured

### Response Time
- Average, Min, Max
- Standard Deviation
- Throughput (presentations/minute)

### Concurrent Performance
- Time savings vs sequential
- Throughput improvement
- Success rate under load

### Streaming Performance
- Time To First Byte (TTFB)
- Chunk delivery rate
- Consistency metrics

---

## 📋 Output Files

| File | Purpose |
|------|---------|
| `performance_baseline_report.md` | Human-readable report with graphs |
| `performance_baseline_report.json` | Machine-readable metrics |

---

## 🎯 Expected Results

### Good Performance
- Avg response time: 5-15 seconds
- Throughput: 4-12 presentations/minute
- Success rate: 100%
- Concurrent improvement: 20-50%

### Warning Signs
- Avg response time: > 20 seconds
- Success rate: < 95%
- High variability (std dev > 50% of avg)
- No improvement from concurrency

---

## 🔧 Customization

### Run with Different Parameters

```python
# Edit performance_tests.py and modify:

# More presentations
runner.test_baseline_normal_load(num_presentations=10)

# More concurrent workers
runner.test_concurrent_load(num_presentations=10, max_workers=5)

# More streaming samples
runner.test_streaming_performance(num_samples=5)
```

---

## 📊 Tracking Performance Over Time

### Save Baseline
```bash
cp performance_baseline_report.md reports/baseline_$(date +%Y%m%d).md
cp performance_baseline_report.json reports/baseline_$(date +%Y%m%d).json
```

### Compare Later
```bash
# Run tests again
python3 performance_tests.py

# Compare with baseline
diff reports/baseline_20260218.md performance_baseline_report.md
```

---

## 🐛 Troubleshooting

### "Connection refused"
```bash
# Check if API is running
docker-compose ps

# Start if needed
docker-compose up -d
```

### High failure rate
```bash
# Check API logs
docker-compose logs presenton

# Reduce concurrent load
# Edit max_workers in performance_tests.py
```

### Timeout errors
```bash
# Increase timeout in performance_tests.py
REQUEST_TIMEOUT = 180  # was 120
```

---

## 📚 Full Documentation

- **Detailed Guide**: `PERFORMANCE_TESTING_GUIDE.md`
- **Implementation Details**: `PERFORMANCE_TESTING_SUMMARY.md`
- **Test Script**: `performance_tests.py`

---

## ✅ Verification Checklist

- ✅ Test 18: Baseline Normal-Load (5 presentations sequential)
- ✅ Test 19: Concurrent Load (5 presentations, 3 workers)
- ✅ Test 20: Streaming Performance (3 samples)
- ✅ Report generation with metrics
- ✅ JSON export for programmatic access
- ✅ Comparative analysis included
- ✅ Optimization recommendations
- ✅ Baseline reference for future comparison

---

## 🎓 Learning Resources

### Understanding the Metrics

**Response Time**: How long each request takes
- Lower is better
- Includes network latency
- Affected by LLM API, database, processing

**Throughput**: How many presentations per minute
- Higher is better
- Indicates system capacity
- Affected by response time and concurrency

**Success Rate**: Percentage of successful requests
- Should be 100%
- Lower rates indicate system issues
- May indicate overload or timeouts

**Standard Deviation**: Variability in response times
- Lower is better
- High values indicate inconsistent performance
- May indicate resource contention

---

## 💡 Tips

1. **Run tests in isolation** - Avoid other heavy processes
2. **Use consistent hardware** - Same machine for comparisons
3. **Run multiple times** - Average results for accuracy
4. **Document changes** - Note system changes that affect performance
5. **Monitor resources** - Check CPU/memory during tests

---

## 🚀 Next Steps

1. Run the tests: `python3 performance_tests.py`
2. Review the report: `cat performance_baseline_report.md`
3. Save the baseline: `cp performance_baseline_report.md reports/baseline_$(date +%Y%m%d).md`
4. Schedule regular runs: Weekly or monthly
5. Track trends: Compare future results against baseline

---

**Last Updated**: 2026-02-18
**Status**: Ready to Use
**Estimated Runtime**: 60 seconds
