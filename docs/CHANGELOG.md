# Changelog

All notable changes to Presenton are documented in this file.

## [2.0.0] - 2026-02-18

### Added

#### Metrics & Analytics
- New `metrics_service.py` module for metrics collection and storage
- New `analytics_service.py` module for analytics and reporting
- Metrics collection via `store_metric()` in all LLM operations
- `GET /api/v1/metrics/dashboard` endpoint for dashboard statistics
- `GET /api/v1/metrics/analytics` endpoint for detailed analytics
- `GET /api/v1/metrics/export` endpoint for JSON/CSV export
- Model usage tracking and distribution analysis
- Cost savings calculations
- Performance metrics (response time, tokens, success rate)

#### Testing
- 10 test presentations with varying parameters
- 5 error handling scenarios tested
- 3 performance testing scenarios established
- Model distribution analysis script
- Performance baseline report
- Error handling test suite
- 50+ unit tests added

#### Documentation
- 22 markdown documentation files (25-30 KB total)
- User guides: Getting Started, User Guide, Configuration, Troubleshooting, FAQ
- Admin guides: Architecture, Deployment, Monitoring
- API documentation: Complete endpoints and error codes
- Deployment configuration: docker-compose.prod.yml, .env.example, health_check.sh
- Setup checklist with 17 steps
- Production readiness checklist
- Contributing guide
- Security policy
- Release notes

#### Production Readiness
- `docker-compose.prod.yml` - Production-optimized configuration
- `.env.example` - Environment variable template
- `health_check.sh` - Automated health check script
- Resource limits and restart policies
- Health checks for all services
- Monitoring and alerting guidelines

### Changed

#### Code Improvements
- Updated `llm_client.py` with metrics instrumentation
- Non-blocking metrics collection (async via `asyncio.create_task()`)
- Enhanced error handling with proper logging
- Improved response time tracking
- Better token count tracking

#### Configuration
- Added metrics-related environment variables
- Updated docker-compose.yml with health checks
- Volume mounts optimized for metrics persistence
- Logging improved for metrics tracking

### Fixed

- Metrics collection no longer blocks API responses
- Depth-based deduplication prevents duplicate metrics
- Error handling improved in all LLM methods
- Response time calculation accuracy improved

### Performance

- Concurrent request handling optimized
- Analytics queries use database aggregation
- Streaming performance optimized
- Metrics collection is non-blocking

### Security

- API keys managed via environment variables
- No hardcoded secrets in configuration
- Input validation for all API endpoints
- Error messages sanitized
- CORS configuration documented

### Documentation

- Complete user documentation
- Complete admin/DevOps documentation
- Complete API documentation
- Setup and deployment guides
- Troubleshooting guides
- FAQ with 43 Q&A pairs

## [1.0.0] - 2026-02-16

### Initial Release

- Presenton AI presentation generator
- OpenRouter free tier integration
- Basic presentation creation API
- Streaming responses
- SQLite database
- Docker Compose deployment

---

## Format

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes
- **Performance**: Performance improvements

---

## Versioning

Presenton uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new features (backward compatible)
- **PATCH** version for bug fixes

---

## Upcoming

### v2.1.0 (March 2026)
- Image generation via Pexels integration
- Advanced analytics dashboards
- Multi-tenancy support

### v2.2.0 (April 2026)
- Custom model configuration
- Team collaboration features
- Presentation templates

---

Last Updated: February 18, 2026
