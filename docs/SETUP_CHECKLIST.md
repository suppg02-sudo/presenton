# Presenton Production Setup Checklist

**Last Updated**: February 18, 2026  
**Version**: 1.0  
**Status**: Ready for Production Deployment

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Step-by-Step Setup](#step-by-step-setup)
3. [Verification Steps](#verification-steps)
4. [Troubleshooting](#troubleshooting)
5. [Post-Deployment](#post-deployment)

---

## Pre-Deployment Checklist

Before starting the deployment process, ensure you have all prerequisites in place.

### Hardware Requirements

- [ ] **CPU**: Minimum 2 cores (4+ cores recommended)
- [ ] **RAM**: Minimum 4GB (8GB+ recommended)
- [ ] **Disk Space**: Minimum 20GB free (50GB+ recommended)
- [ ] **Network**: Stable internet connection with at least 10 Mbps
- [ ] **Uptime**: Server can run 24/7 without interruption

### Software Requirements

- [ ] **Docker**: Version 20.10+ installed
  ```bash
  docker --version
  ```
- [ ] **Docker Compose**: Version 1.29+ installed
  ```bash
  docker-compose --version
  ```
- [ ] **Git**: Version 2.25+ installed (for cloning repository)
  ```bash
  git --version
  ```
- [ ] **curl**: For testing endpoints
  ```bash
  curl --version
  ```
- [ ] **nc (netcat)**: For port checking
  ```bash
  nc -h
  ```

### Network Requirements

- [ ] **Port 80**: Available and not in use (HTTP)
- [ ] **Port 443**: Available and not in use (HTTPS/SSL)
- [ ] **Port 8000**: Available for FastAPI (internal only)
- [ ] **Port 3000**: Available for Next.js (internal only)
- [ ] **Firewall**: Configured to allow inbound traffic on ports 80 and 443
- [ ] **DNS**: Domain name configured and pointing to server IP

### SSL/TLS Certificate

- [ ] **SSL Certificate**: Obtained from Certificate Authority (Let's Encrypt recommended)
- [ ] **Private Key**: Securely stored
- [ ] **Certificate Chain**: Complete chain available
- [ ] **Expiration Date**: Certificate valid for at least 30 days
- [ ] **Certificate Location**: Ready to place in `./ssl/` directory

### API Keys and Credentials

- [ ] **LLM API Key**: Obtained from your LLM provider (OpenRouter, OpenAI, etc.)
- [ ] **Image Generation API Key**: Obtained (Pexels, Pixabay, or Unsplash)
- [ ] **Database Credentials**: If using external database
- [ ] **Monitoring API Keys**: If using Sentry, Datadog, etc.
- [ ] **Backup Storage Credentials**: If using S3 or other cloud storage

### Domain and Hosting

- [ ] **Domain Name**: Registered and configured
- [ ] **DNS Records**: A record pointing to server IP
- [ ] **Reverse DNS**: Configured (optional but recommended)
- [ ] **Email**: For SSL certificate notifications

### Access and Permissions

- [ ] **Server Access**: SSH access to production server
- [ ] **File Permissions**: Ability to create directories and files
- [ ] **Docker Permissions**: User can run Docker commands (or sudo access)
- [ ] **Backup Access**: Access to backup storage location

---

## Step-by-Step Setup

Follow these steps in order to deploy Presenton to production.

### Step 1: Clone Repository

Clone the Presenton repository to your server:

```bash
cd /home/usdaw
git clone https://github.com/presenton/presenton.git
cd presenton
```

**Verification**:
- [ ] Repository cloned successfully
- [ ] All files present (check with `ls -la`)
- [ ] Git history available (check with `git log`)

---

### Step 2: Create Environment Configuration

Create the `.env` file from the template:

```bash
cp ENV_TEMPLATE.txt .env
```

**Verification**:
- [ ] `.env` file created
- [ ] File is readable (check with `cat .env`)

---

### Step 3: Configure Environment Variables

Edit the `.env` file with your production settings:

```bash
nano .env
# or
vim .env
```

**Required Variables to Configure**:

- [ ] `CUSTOM_LLM_URL`: Your LLM provider URL
- [ ] `CUSTOM_LLM_API_KEY`: Your LLM API key
- [ ] `CUSTOM_MODEL`: Model name to use
- [ ] `CORS_ORIGINS`: Allowed origins (set to your domain)
- [ ] `ALLOWED_HOSTS`: Allowed hostnames
- [ ] `LOG_LEVEL`: Set to `WARN` for production
- [ ] `DEBUG`: Set to `false`

**Optional Variables**:

- [ ] `DISABLE_IMAGE_GENERATION`: Set to `false` if enabling images
- [ ] `PEXELS_API_KEY`: If using Pexels for images
- [ ] `METRICS_ENABLED`: Set to `true` for monitoring
- [ ] `ANALYTICS_RETENTION_DAYS`: Set retention period

**Verification**:
- [ ] All required variables have values
- [ ] No empty required fields
- [ ] API keys are valid
- [ ] File saved without errors

---

### Step 4: Create Data Directories

Create necessary directories for data persistence:

```bash
mkdir -p ./app_data
mkdir -p ./app_data/images
mkdir -p ./app_data/exports
mkdir -p ./app_data/uploads
mkdir -p ./app_data/fonts
mkdir -p ./logs
chmod 755 ./app_data
chmod 755 ./logs
```

**Verification**:
- [ ] `app_data` directory created
- [ ] Subdirectories created
- [ ] Directories are writable (check with `touch ./app_data/test.txt`)
- [ ] Test file removed

---

### Step 5: Configure SSL/TLS Certificates

Create SSL directory and place certificates:

```bash
mkdir -p ./ssl
# Copy your certificate files
cp /path/to/certificate.crt ./ssl/
cp /path/to/private.key ./ssl/
cp /path/to/chain.crt ./ssl/
chmod 600 ./ssl/private.key
chmod 644 ./ssl/certificate.crt
chmod 644 ./ssl/chain.crt
```

**Verification**:
- [ ] SSL directory created
- [ ] Certificate file present
- [ ] Private key present
- [ ] Chain file present
- [ ] Permissions set correctly

---

### Step 6: Update Nginx Configuration

Update `nginx.conf` with your domain and SSL settings:

```bash
nano nginx.conf
```

**Changes to Make**:

- [ ] Update `server_name` to your domain
- [ ] Add SSL certificate paths
- [ ] Configure SSL protocols
- [ ] Set up redirects (HTTP to HTTPS)

**Example SSL Configuration**:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_trusted_certificate /etc/nginx/ssl/chain.crt;
    
    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**Verification**:
- [ ] Nginx configuration updated
- [ ] SSL paths correct
- [ ] Configuration syntax valid (test with `docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx nginx -t`)

---

### Step 7: Start Docker Containers

Start all services using the production docker-compose file:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Verification**:
- [ ] Command executed without errors
- [ ] All containers started (check with `docker ps`)
- [ ] No containers in "Exited" state

---

### Step 8: Wait for Services to Be Ready

Wait for all services to initialize and become healthy:

```bash
# Wait 30-60 seconds for services to start
sleep 60

# Check container status
docker ps

# Check logs for any errors
docker logs presenton-fastapi
docker logs presenton-nextjs
docker logs presenton-nginx
```

**Verification**:
- [ ] All containers running
- [ ] No error messages in logs
- [ ] Services have had time to initialize

---

### Step 9: Run Health Checks

Execute the health check script to verify all services:

```bash
bash health_check.sh
```

**Expected Output**:
- [ ] All Docker containers running
- [ ] FastAPI health endpoint responding
- [ ] Frontend responding on port 3000
- [ ] Nginx proxy responding on port 80
- [ ] Database accessible
- [ ] Metrics endpoint responding
- [ ] All API endpoints responding

**If Health Check Fails**:
- [ ] Review the output for specific failures
- [ ] Check container logs: `docker logs <container-name>`
- [ ] See [Troubleshooting](#troubleshooting) section

---

### Step 10: Test API Endpoints

Test critical API endpoints manually:

```bash
# Test health endpoint
curl http://localhost/api/v1/health

# Test presentations endpoint
curl http://localhost/api/v1/presentations

# Test API documentation
curl http://localhost/docs

# Test frontend
curl http://localhost/
```

**Verification**:
- [ ] Health endpoint returns 200 OK
- [ ] Presentations endpoint responds
- [ ] API docs accessible
- [ ] Frontend loads successfully

---

### Step 11: Configure SSL/TLS (If Using HTTPS)

If using Let's Encrypt with Certbot:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/certificate.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/private.key
sudo chown $USER:$USER ./ssl/*
```

**Verification**:
- [ ] Certificate obtained successfully
- [ ] Certificates copied to ssl directory
- [ ] Nginx configuration updated
- [ ] HTTPS working (test with `curl https://yourdomain.com`)

---

### Step 12: Set Up Backup Schedule

Create a backup script and schedule it:

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/presenton_backup_$TIMESTAMP.tar.gz ./app_data/
echo "Backup completed: $BACKUP_DIR/presenton_backup_$TIMESTAMP.tar.gz"
EOF

chmod +x backup.sh

# Schedule daily backup at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * cd /home/usdaw/presenton && ./backup.sh") | crontab -
```

**Verification**:
- [ ] Backup script created
- [ ] Backup script is executable
- [ ] Cron job scheduled
- [ ] Test backup: `./backup.sh`
- [ ] Backup file created successfully

---

### Step 13: Set Up Monitoring and Alerting

Configure monitoring for your deployment:

**Option 1: Using Sentry (Error Tracking)**:

```bash
# Add to .env
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

# Restart containers
docker-compose -f docker-compose.prod.yml restart
```

**Option 2: Using Datadog (Metrics)**:

```bash
# Add to .env
DATADOG_API_KEY=your_datadog_api_key

# Restart containers
docker-compose -f docker-compose.prod.yml restart
```

**Option 3: Using Prometheus (Self-Hosted)**:

```bash
# Configure Prometheus to scrape /api/v1/metrics
# Add to prometheus.yml:
# - job_name: 'presenton'
#   static_configs:
#     - targets: ['localhost:8000']
```

**Verification**:
- [ ] Monitoring service configured
- [ ] Metrics being collected
- [ ] Alerts configured (if applicable)

---

### Step 14: Configure Log Rotation

Set up log rotation to prevent disk space issues:

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/presenton > /dev/null << 'EOF'
/home/usdaw/presenton/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    sharedscripts
}
EOF

# Test logrotate
sudo logrotate -f /etc/logrotate.d/presenton
```

**Verification**:
- [ ] Logrotate configuration created
- [ ] Configuration tested
- [ ] Old logs being rotated

---

### Step 15: Test Recovery Procedures

Test that you can recover from failures:

```bash
# Test container restart
docker-compose -f docker-compose.prod.yml restart presenton-fastapi

# Verify service recovers
sleep 30
bash health_check.sh

# Test full restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
sleep 60
bash health_check.sh
```

**Verification**:
- [ ] Services restart successfully
- [ ] Health checks pass after restart
- [ ] No data loss after restart
- [ ] Services recover automatically

---

### Step 16: Document Custom Configuration

Document any custom configuration for your deployment:

```bash
# Create deployment documentation
cat > DEPLOYMENT_NOTES.md << 'EOF'
# Deployment Notes

## Server Information
- Hostname: [your-hostname]
- IP Address: [your-ip]
- Domain: [your-domain]
- Deployment Date: [date]

## Configuration
- LLM Provider: [provider]
- Image Generation: [enabled/disabled]
- Monitoring: [service]
- Backup Location: [location]

## Important Contacts
- System Administrator: [name/email]
- Support Contact: [name/email]

## Custom Modifications
- [List any custom changes made]

## Known Issues
- [List any known issues]

## Maintenance Schedule
- Daily: Health checks
- Weekly: Backup verification
- Monthly: Log review
- Quarterly: Security updates
EOF
```

**Verification**:
- [ ] Documentation created
- [ ] All important information documented
- [ ] Contact information included
- [ ] File saved and accessible

---

### Step 17: Get Sign-Off from Stakeholders

Obtain approval from relevant stakeholders:

- [ ] **System Administrator**: Reviewed and approved
- [ ] **Security Team**: Reviewed security configuration
- [ ] **Operations Team**: Reviewed monitoring and alerting
- [ ] **Project Manager**: Approved for production
- [ ] **Business Owner**: Approved deployment

**Sign-Off Template**:

```
Presenton Production Deployment Sign-Off

Date: _______________
Deployment Version: _______________

Reviewed By:
- System Administrator: _________________ Date: _______
- Security Team: _________________ Date: _______
- Operations Team: _________________ Date: _______
- Project Manager: _________________ Date: _______
- Business Owner: _________________ Date: _______

Approved for Production: YES / NO

Notes:
_________________________________________________________________
_________________________________________________________________
```

---

## Verification Steps

After completing the setup, verify everything is working correctly.

### All Services Running

```bash
docker ps
```

**Expected Output**:
- [ ] presenton-fastapi running
- [ ] presenton-nextjs running
- [ ] presenton-nginx running

### All Health Checks Pass

```bash
bash health_check.sh
```

**Expected Output**:
- [ ] All checks marked with ✓
- [ ] No ✗ marks
- [ ] Summary shows "All services are healthy"

### API Responding Correctly

```bash
# Test health endpoint
curl -i http://localhost/api/v1/health

# Test presentations endpoint
curl -i http://localhost/api/v1/presentations

# Test metrics
curl -i http://localhost/api/v1/metrics/dashboard
```

**Expected Output**:
- [ ] HTTP 200 responses
- [ ] Valid JSON responses
- [ ] No error messages

### Database Initialized

```bash
# Check database file exists
ls -lh ./app_data/presenton.db

# Verify database is accessible
sqlite3 ./app_data/presenton.db "SELECT 1;"
```

**Expected Output**:
- [ ] Database file exists
- [ ] File size > 0 bytes
- [ ] Query returns 1

### Metrics Collecting

```bash
# Check metrics endpoint
curl http://localhost/api/v1/metrics/dashboard | jq .

# Verify metrics data
docker logs presenton-fastapi | grep -i "metric"
```

**Expected Output**:
- [ ] Metrics endpoint returns data
- [ ] Metrics being collected
- [ ] No errors in logs

---

## Troubleshooting

### Container Won't Start

**Symptoms**: Container exits immediately or stays in "Exited" state

**Solutions**:

1. Check container logs:
   ```bash
   docker logs presenton-fastapi
   docker logs presenton-nextjs
   docker logs presenton-nginx
   ```

2. Verify environment variables:
   ```bash
   docker-compose -f docker-compose.prod.yml config | grep -A 20 "environment:"
   ```

3. Check file permissions:
   ```bash
   ls -la ./app_data
   ls -la ./ssl
   ```

4. Verify ports are available:
   ```bash
   netstat -tlnp | grep -E ":(80|443|8000|3000)"
   ```

5. Restart containers:
   ```bash
   docker-compose -f docker-compose.prod.yml restart
   ```

### API Returning 500 Errors

**Symptoms**: API endpoints return HTTP 500 errors

**Solutions**:

1. Check FastAPI logs:
   ```bash
   docker logs presenton-fastapi -f
   ```

2. Verify database connectivity:
   ```bash
   sqlite3 ./app_data/presenton.db "SELECT 1;"
   ```

3. Check environment variables:
   ```bash
   docker exec presenton-fastapi env | grep -E "LLM|DATABASE"
   ```

4. Verify API key is valid:
   ```bash
   curl -X POST https://your-llm-provider/api/v1/test \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

5. Restart FastAPI service:
   ```bash
   docker-compose -f docker-compose.prod.yml restart presenton-fastapi
   ```

### Database Errors

**Symptoms**: Database connection errors in logs

**Solutions**:

1. Check database file exists:
   ```bash
   ls -la ./app_data/presenton.db
   ```

2. Verify database is not corrupted:
   ```bash
   sqlite3 ./app_data/presenton.db "PRAGMA integrity_check;"
   ```

3. Check file permissions:
   ```bash
   chmod 666 ./app_data/presenton.db
   ```

4. Verify database URL in .env:
   ```bash
   grep DATABASE_URL .env
   ```

5. Recreate database if corrupted:
   ```bash
   rm ./app_data/presenton.db
   docker-compose -f docker-compose.prod.yml restart presenton-fastapi
   ```

### Memory Usage Too High

**Symptoms**: Container using excessive memory, system slow

**Solutions**:

1. Check memory usage:
   ```bash
   docker stats
   ```

2. Increase memory limits in docker-compose.prod.yml:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 4G  # Increase from 2G
   ```

3. Restart containers:
   ```bash
   docker-compose -f docker-compose.prod.yml restart
   ```

4. Check for memory leaks in logs:
   ```bash
   docker logs presenton-fastapi | grep -i "memory"
   ```

5. Reduce analytics retention:
   ```bash
   # Edit .env
   ANALYTICS_RETENTION_DAYS=30  # Reduce from 90
   docker-compose -f docker-compose.prod.yml restart
   ```

### Nginx Not Proxying Correctly

**Symptoms**: Requests not reaching backend services

**Solutions**:

1. Check Nginx logs:
   ```bash
   docker logs presenton-nginx
   ```

2. Verify Nginx configuration:
   ```bash
   docker exec presenton-nginx nginx -t
   ```

3. Check backend services are running:
   ```bash
   docker ps | grep presenton
   ```

4. Verify network connectivity:
   ```bash
   docker exec presenton-nginx curl http://presenton-fastapi:8000/api/v1/health
   ```

5. Reload Nginx configuration:
   ```bash
   docker exec presenton-nginx nginx -s reload
   ```

---

## Post-Deployment

### Daily Tasks

- [ ] Check health status: `bash health_check.sh`
- [ ] Review error logs: `docker logs presenton-fastapi | grep ERROR`
- [ ] Monitor resource usage: `docker stats`

### Weekly Tasks

- [ ] Verify backups completed successfully
- [ ] Review metrics and performance
- [ ] Check for security updates
- [ ] Test recovery procedures

### Monthly Tasks

- [ ] Review and rotate logs
- [ ] Update documentation
- [ ] Perform security audit
- [ ] Review and optimize resource allocation

### Quarterly Tasks

- [ ] Update Docker images
- [ ] Review and update dependencies
- [ ] Perform full system backup
- [ ] Conduct disaster recovery drill

### Annual Tasks

- [ ] Renew SSL certificates
- [ ] Review and update security policies
- [ ] Perform comprehensive security audit
- [ ] Plan capacity upgrades if needed

---

## Support and Escalation

### Getting Help

1. **Check Documentation**:
   - TROUBLESHOOTING_GUIDE.md
   - README.md
   - CONFIGURATION_GUIDE.md

2. **Check Logs**:
   ```bash
   docker logs presenton-fastapi
   docker logs presenton-nextjs
   docker logs presenton-nginx
   ```

3. **Run Health Checks**:
   ```bash
   bash health_check.sh
   ```

4. **Contact Support**:
   - Email: support@presenton.dev
   - GitHub Issues: https://github.com/presenton/presenton/issues
   - Documentation: https://presenton.dev/docs

---

## Deployment Completion Checklist

- [ ] All steps completed
- [ ] All verification checks passed
- [ ] Health checks passing
- [ ] Backups configured and tested
- [ ] Monitoring and alerting configured
- [ ] Documentation completed
- [ ] Sign-offs obtained
- [ ] Team trained on operations
- [ ] Runbooks created
- [ ] Deployment successful!

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Approved By**: _______________  
**Notes**: _______________________________________________________________

---

*For questions or issues, refer to TROUBLESHOOTING_GUIDE.md or contact support.*
