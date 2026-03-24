# Presenton Test Presentations - Enhancement-11

## Overview

This test suite generates 10 test presentations with varying parameters to validate Presenton system functionality and test model variety across different languages, slide counts, and topics.

## Test Matrix

| Test # | Language | Slides | Topic | Content | Images |
|--------|----------|--------|-------|---------|--------|
| 1 | English | 3 | Simple topic | Introduction to basic concepts | No |
| 2 | Spanish | 5 | Business topic | Estrategias empresariales | No |
| 3 | French | 5 | Technology topic | Avancées technologiques | No |
| 4 | English | 10 | Educational topic | Learning materials | No |
| 5 | German | 3 | Creative topic | Kreative Ideen | No |
| 6 | English | 5 | Marketing topic | Digital marketing strategies | No |
| 7 | Spanish | 10 | Science topic | Descubrimientos científicos | No |
| 8 | English | 3 | Mixed topic | Interdisciplinary approaches | No |
| 9 | French | 5 | Professional topic | Développement professionnel | No |
| 10 | Italian | 5 | Cultural topic | Patrimonio culturale | No |

## Files

### `test_presentations.py`
Main test script that:
- Creates 10 presentations via the Presenton API
- Captures presentation IDs and metadata
- Logs results to `test_results_presentations.txt`
- Generates JSON results for programmatic access
- Provides detailed reporting by language and slide count

### `run_tests.sh`
Shell script wrapper that:
- Verifies Python 3 is available
- Checks if the Presenton API is running
- Executes the test script
- Displays results summary

### `test_results_presentations.txt`
Generated test results file containing:
- Detailed results for each test
- Presentation IDs
- Timestamps
- Status (success/failed/error)
- Summary by language
- Summary by slide count

### `test_results_presentations.json`
Machine-readable JSON results for programmatic access

## Prerequisites

1. **Presenton Container Running**
   ```bash
   cd /home/usdaw/presenton
   docker-compose up -d
   ```

2. **Python 3 Installed**
   - The script will auto-install `requests` library if needed

3. **API Accessible**
   - Default: `http://localhost:5001/api/v1/ppt`

## Running the Tests

### Option 1: Using Shell Script (Recommended)
```bash
cd /home/usdaw/presenton
bash run_tests.sh
```

### Option 2: Direct Python Execution
```bash
cd /home/usdaw/presenton
python3 test_presentations.py
```

## Expected Output

### Console Output
```
========================================
PRESENTON TEST PRESENTATIONS - ENHANCEMENT-11
========================================
Starting test run at 2026-02-18T...
Total tests to run: 10
========================================

Test 1: Creating presentation - Simple topic (English, 3 slides)
Test 1: ✓ Created successfully - ID: <uuid>
...
```

### Results File Format

```
====================================================================================================
PRESENTON TEST PRESENTATIONS - RESULTS REPORT
====================================================================================================
Report Generated: 2026-02-18T...
Total Tests: 10
Successful: 10
Failed: 0
====================================================================================================

DETAILED RESULTS:
----------------------------------------------------------------------------------------------------
Test #01 | Topic: Simple topic           | Language: English    | Slides: 3  | Images: No | Status: success
         Presentation ID: <uuid>
         Timestamp: 2026-02-18T...

...

SUMMARY BY LANGUAGE:
----------------------------------------------------------------------------------------------------
English            - Total: 4, Successful: 4
French             - Total: 2, Successful: 2
German             - Total: 1, Successful: 1
Italian            - Total: 1, Successful: 1
Spanish            - Total: 2, Successful: 2

SUMMARY BY SLIDE COUNT:
----------------------------------------------------------------------------------------------------
3 slides - Total: 3, Successful: 3
5 slides - Total: 5, Successful: 5
10 slides - Total: 2, Successful: 2

====================================================================================================
```

## Verification Checklist

After running tests, verify:

- [ ] All 10 presentations created successfully
- [ ] Each presentation has a unique UUID
- [ ] Presentation IDs are captured in results
- [ ] Test results file created: `test_results_presentations.txt`
- [ ] JSON results file created: `test_results_presentations.json`
- [ ] All languages represented (English, Spanish, French, German, Italian)
- [ ] Slide counts vary (3, 5, 10)
- [ ] Timestamps recorded for each test
- [ ] No error messages in results

## API Endpoint Details

### Presentation Creation Endpoint
- **URL**: `POST /api/v1/ppt/presentation/create`
- **Base URL**: `http://localhost:5001`

### Request Payload
```json
{
  "content": "Presentation topic/content",
  "n_slides": 5,
  "language": "English",
  "tone": "default",
  "verbosity": "standard",
  "include_table_of_contents": false,
  "include_title_slide": true,
  "web_search": false,
  "file_paths": null
}
```

### Response
```json
{
  "id": "uuid",
  "content": "...",
  "n_slides": 5,
  "language": "English",
  "created_at": "2026-02-18T...",
  "updated_at": "2026-02-18T...",
  ...
}
```

## Troubleshooting

### API Not Running
```bash
# Check if container is running
docker ps | grep presenton

# Start container if needed
docker-compose up -d

# Check logs
docker-compose logs -f presenton
```

### Connection Refused
```bash
# Verify API is accessible
curl http://localhost:5001/api/v1/ppt/presentation/all

# Check if port 5001 is in use
lsof -i :5001
```

### Python Dependencies
```bash
# Install requests manually if needed
pip3 install requests

# Or use the script's auto-install feature
python3 test_presentations.py
```

## Metrics Collection

The test suite generates metrics data that can be monitored:

1. **Presentation Creation Rate**: 10 presentations created
2. **Language Distribution**: 5 different languages tested
3. **Slide Count Variation**: 3, 5, and 10 slide presentations
4. **Response Times**: Captured in timestamps
5. **Success Rate**: Percentage of successful creations

## Next Steps

After successful test execution:

1. Review `test_results_presentations.txt` for detailed results
2. Check database for created presentations:
   ```bash
   sqlite3 /home/usdaw/presenton/app_data/fastapi.db
   SELECT id, language, n_slides, created_at FROM presentations ORDER BY created_at DESC LIMIT 10;
   ```
3. Verify presentations in UI at `http://localhost:3000`
4. Monitor metrics dashboard for performance data
5. Archive results for regression testing

## Notes

- Tests run sequentially with 0.5s delay between requests
- No images are generated (DISABLE_IMAGE_GENERATION=true)
- All presentations use default tone and standard verbosity
- Web search is disabled for consistent results
- Results are timestamped for audit trail
- JSON results enable automated validation

## Support

For issues or questions:
1. Check logs: `docker-compose logs presenton`
2. Review API documentation: `/home/usdaw/presenton/ENDPOINT_SUMMARY.md`
3. Check database directly for created presentations
4. Verify network connectivity to API endpoint
