# Error Handling & Fallback Testing Guide

## Overview

This guide provides instructions for running the comprehensive error handling test suite for the Presenton AI presentation generator. The test suite covers 5 critical error scenarios to ensure robust error handling and graceful degradation.

## Test Suite Components

### Test 13: API Downtime/Bad API Key
**Purpose**: Verify graceful handling of API failures and invalid credentials
**Scenarios**:
- Invalid API key format
- API downtime (simulated via timeout)
- Connection failures

**Expected Behavior**:
- Errors are caught and reported
- Graceful failure messages are returned
- Recovery time is documented

**Success Criteria**:
- Error messages are clear and actionable
- HTTP status codes are appropriate (4xx/5xx)
- No unhandled exceptions

### Test 14: Rate Limiting
**Purpose**: Verify system behavior under rapid request load
**Scenarios**:
- 10 rapid sequential requests
- Measure response times
- Track success/failure rates

**Expected Behavior**:
- Some requests may be rate limited (429)
- Response times increase under load
- System remains stable

**Success Criteria**:
- At least some requests succeed
- Rate limiting is graceful (not crashing)
- Response times are documented

### Test 15: Malformed Input
**Purpose**: Verify input validation and error reporting
**Scenarios**:
- Invalid JSON payloads
- Missing required fields
- Invalid language codes
- Negative/zero slide counts
- Invalid export formats

**Expected Behavior**:
- Validation errors return 400/422 status codes
- Error messages describe the validation failure
- No data corruption occurs

**Success Criteria**:
- All validation errors are caught
- Error messages are descriptive
- Appropriate HTTP status codes are returned

### Test 16: Timeout Scenarios
**Purpose**: Verify timeout handling and recovery
**Scenarios**:
- Very short timeout (1 second)
- Short timeout (3 seconds)
- Normal timeout (10 seconds)

**Expected Behavior**:
- Timeouts are caught and reported
- Requests fail gracefully
- No hanging connections

**Success Criteria**:
- Timeout exceptions are properly caught
- Error messages indicate timeout
- System recovers after timeout

### Test 17: Error Report Compilation
**Purpose**: Aggregate all test results and generate comprehensive report
**Deliverables**:
- error_handling_report.md - Comprehensive markdown report
- error_handling_results.json - Machine-readable results
- error_handling_tests.log - Detailed execution log

## Running the Tests

### Prerequisites

1. **Python 3.8+** installed
2. **requests library** installed:
   ```bash
   pip install requests
   ```
3. **Presenton API running** on http://localhost:5001/api/v1/ppt

### Basic Execution

```bash
cd /home/usdaw/presenton
python3 error_handling_tests.py
```

### Expected Output

The test suite will:
1. Run all 5 tests sequentially
2. Log results to console and `error_handling_tests.log`
3. Generate `error_handling_report.md` with comprehensive findings
4. Save machine-readable results to `error_handling_results.json`

### Sample Output

```
================================================================================
PRESENTON ERROR HANDLING TEST SUITE
================================================================================
2024-02-18 10:30:45,123 - INFO - [__main__] - Starting Test 13: API Downtime/Bad API Key
2024-02-18 10:30:45,234 - INFO - [__main__] - Test 13.1: Testing with invalid API key format
2024-02-18 10:30:47,456 - INFO - [__main__] - Test completed: Test 13: API Downtime/Bad API Key - passed
...
================================================================================
TEST EXECUTION SUMMARY
================================================================================
Total Tests: 5
Passed: 5 (100.0%)
Failed: 0 (0.0%)
Partial: 0 (0.0%)
Total Duration: 45234.56ms
================================================================================
```

## Test Results Interpretation

### Status Codes

- **✅ PASSED**: Test completed successfully, all criteria met
- **❌ FAILED**: Test failed, criteria not met
- **⚠️ PARTIAL**: Test partially successful, some criteria met

### Key Metrics

- **Duration (ms)**: Time taken to execute the test
- **Status Code**: HTTP response status code
- **Error Type**: Category of error encountered
- **Recovery Time**: Time to recover from error

## Generated Reports

### error_handling_report.md

Comprehensive markdown report including:
- Executive summary
- Test results overview table
- Detailed test results with error messages
- Error patterns and analysis
- Recommendations for improvements
- Test environment details

### error_handling_results.json

Machine-readable JSON format with:
- Timestamp of execution
- Total number of tests
- Individual test results with all details
- Status codes and error messages

### error_handling_tests.log

Detailed execution log with:
- Timestamp for each operation
- Log level (INFO, WARNING, ERROR)
- Detailed error messages and stack traces
- Request/response details

## Troubleshooting

### API Connection Issues

**Problem**: "Connection refused" error
**Solution**: 
1. Verify Presenton API is running: `docker-compose ps`
2. Check API port: `curl http://localhost:5001/api/v1/ppt/presentation/all`
3. Restart API if needed: `docker-compose restart fastapi`

### Timeout Issues

**Problem**: All tests timeout
**Solution**:
1. Check API performance: `docker-compose logs fastapi`
2. Verify system resources: `docker stats`
3. Increase timeout values in test script if needed

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'requests'"
**Solution**:
```bash
pip install requests
```

## Customization

### Changing API URL

Edit the test script initialization:
```python
suite = ErrorHandlingTestSuite(api_base_url="http://your-api:port/api/v1/ppt")
```

### Adjusting Timeout Values

Modify timeout values in individual test methods:
```python
response = self.session.post(
    endpoint,
    json=payload,
    timeout=10,  # Change this value
)
```

### Adding Custom Tests

Add new test methods following the pattern:
```python
async def test_XX_custom_test(self) -> TestResult:
    """Test description"""
    test_name = "Test XX: Custom Test"
    logger.info(f"Starting {test_name}")
    start_time = time.time()
    
    try:
        # Test implementation
        return TestResult(
            test_id=XX,
            test_name=test_name,
            status=TestStatus.PASSED,
            duration_ms=(time.time() - start_time) * 1000,
            details={...},
        )
    except Exception as e:
        return TestResult(
            test_id=XX,
            test_name=test_name,
            status=TestStatus.FAILED,
            duration_ms=(time.time() - start_time) * 1000,
            error_message=str(e),
        )
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Error Handling Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install requests
      - run: python3 error_handling_tests.py
      - uses: actions/upload-artifact@v2
        with:
          name: error-handling-reports
          path: |
            error_handling_report.md
            error_handling_results.json
            error_handling_tests.log
```

## Performance Benchmarks

Expected execution times:
- Test 13 (API Downtime): 2-5 seconds
- Test 14 (Rate Limiting): 5-10 seconds
- Test 15 (Malformed Input): 3-5 seconds
- Test 16 (Timeout Scenarios): 15-20 seconds
- Test 17 (Report Compilation): 1-2 seconds

**Total Expected Duration**: 30-45 seconds

## Best Practices

1. **Run tests regularly**: Execute test suite after API changes
2. **Monitor trends**: Track error patterns over time
3. **Review recommendations**: Implement suggested improvements
4. **Update tests**: Add new test cases as features are added
5. **Document changes**: Keep test documentation up to date

## Support & Feedback

For issues or suggestions:
1. Check the troubleshooting section
2. Review error_handling_tests.log for details
3. Consult error_handling_report.md for analysis
4. Contact development team with findings

## References

- [Presenton API Documentation](./ENDPOINT_SUMMARY.md)
- [Error Handling Report](./error_handling_report.md)
- [Test Results JSON](./error_handling_results.json)
- [Execution Log](./error_handling_tests.log)

---

**Last Updated**: 2024-02-18
**Test Suite Version**: 1.0
**Status**: Production Ready
