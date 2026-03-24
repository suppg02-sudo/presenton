# Wazuh POC Deployment Guide

## Overview
Single-node Wazuh deployment for security monitoring, file integrity monitoring, and dashboard review on this server (10.2.1.182).

## Components
- **Elasticsearch 8.15.0** - Data storage and search
- **Wazuh Manager 4.8.2** - Core SIEM engine
- **Wazuh Filebeat 8.15.0** - Log and event shipper (telemetry client)
- **Wazuh Dashboard 4.8.2** - Web UI for review

## Architecture
```
Host Server (10.2.1.182)
  ├── Wazuh Agent (FIM, HIDS)
  │   ↓ Monitors security events
  ↓
  ├── System Logs (/var/log/)
  │   ↓ Auth, syslog, kern
  ↓
  ├── Filebeat (Telemetry Client)
  │   ↓ Collects & ships
  ↓
  ├── Wazuh Manager API (55000)
  │   ↓ Processes alerts
  ↓
  ├── Elasticsearch (9200)
  │   ↓ Stores events
  ↓
  └── Wazuh Dashboard (5601)
```

## Quick Start

### 1. Deploy Containers
```bash
cd /media/docker/wazuh
docker-compose up -d
```

### 2. Wait for Services to Start
```bash
# Check status
docker-compose ps

# Watch Elasticsearch startup
docker logs -f wazuh-elasticsearch

# Wait until you see: "started"
```

### 3. Install Local Wazuh Agent
```bash
# Download agent
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent_4.8.2-1_amd64.deb

# Install agent
sudo dpkg -i wazuh-agent_4.8.2-1_amd64.deb

# Register agent
sudo /var/ossec/bin/wazuh-control register 10.2.1.182 local-server 6ceed028375aa35fa102779e4cb71b46c93bdc4641e2aecbf16356d154f3ce84

# Start agent
sudo systemctl restart wazuh-agent
```

## Access URLs

| Component | URL | Credentials |
|-----------|-----|------------|
| **Wazuh Dashboard** | http://10.2.1.182:5601 | wazuh-admin / `WAZUH_ADMIN_PASSWORD` |
| **Wazuh API** | http://10.2.1.182:55000/api | wazuh-admin / `WAZUH_ADMIN_PASSWORD` |
| **Elasticsearch** | http://10.2.1.182:9200 | elastic / `ELASTIC_PASSWORD` |

## Ports Exposed

- **1515/UDP** - Agent connection to Wazuh Manager
- **1514** - Agent registration
- **55000** - Wazuh Manager API
- **55001** - Events API
- **55002** - Syslog API
- **9200** - Elasticsearch HTTP
- **9300** - Elasticsearch Transport
- **5601** - Wazuh Dashboard

## What Filebeat Monitors (Telemetry Client)

Filebeat collects and ships:

### Security Events
- Wazuh agent alerts (intrusions, rootkits, policy violations)
- File integrity monitoring (FIM) events
- Syscheck (configuration changes)
- Rootcheck (rootkit detection)
- Vulnerability scanner results

### System Logs
- `/var/log/syslog` - System messages
- `/var/log/auth.log` - Authentication attempts
- `/var/log/kern.log` - Kernel messages
- Systemd journals - Service logs

## File Integrity Monitoring (FIM)

After installing agent, configure FIM to monitor:

### Recommended Paths
- `/etc/` - System configuration
- `/var/www/` - Web files (Sterling PDF)
- `/home/` - User home directories
- `/opt/` - Applications

### Enable FIM
```bash
# Edit Wazuh agent config
sudo nano /var/ossec/etc/ossec.conf

# Add syscheck section
<syscheck>
  <directories check_all="yes" realtime="yes" report_changes="yes">
    <directories>/etc</directories>
    <directories>/var/www</directories>
    <directories>/home</directories>
    <directories>/opt</directories>
  </directories>
</syscheck>

# Restart agent
sudo systemctl restart wazuh-agent
```

## Credentials

Stored in `.env` file (secure, chmod 600):
- `WAZUH_ADMIN_USERNAME` - wazuh-admin
- `WAZUH_ADMIN_PASSWORD` - Auto-generated
- `ELASTIC_USERNAME` - elastic
- `ELASTIC_PASSWORD` - Auto-generated
- `API_KEY` - Auto-generated

**⚠️ IMPORTANT**: Save these credentials securely!

## Storage

Data volumes (persistent across container restarts):
- `./elasticsearch-data/` - Elasticsearch indices
- `./wazuh-manager-data/` - Wazuh rules and state
- `./wazuh-manager-config/` - API configuration
- `./filebeat-data/` - Filebeat registry
- `./dashboard-data/` - Dashboard saved searches

## Commands

### Start
```bash
docker-compose up -d
```

### Stop
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f wazuh-manager
docker logs -f wazuh-filebeat
docker logs -f wazuh-elasticsearch
```

### Restart Service
```bash
docker-compose restart wazuh-manager
```

### Check Health
```bash
# Elasticsearch
curl -u elastic:ELASTIC_PASSWORD http://localhost:9200/_cluster/health

# Wazuh Manager
curl http://localhost:55000/api/healthcheck

# Dashboard
curl http://localhost:5601
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs wazuh-[service-name]

# Check if ports are in use
sudo netstat -tulpn | grep -E '1515|55000|9200|5601'
```

### Agent can't register
```bash
# Check manager is running
curl http://localhost:55000/api/healthcheck

# Check firewall
sudo ufw status
sudo ufw allow 1514/udp
```

### No events in dashboard
```bash
# Check agent status
sudo systemctl status wazuh-agent

# Check agent log
sudo tail -f /var/ossec/logs/ossec.log

# Check filebeat logs
docker logs wazuh-filebeat
```

## Next Steps (Post-POC)

1. **Expand to Multiple Hosts** - Deploy agents on other servers
2. **Configure Alert Rules** - Set up email, Slack, or webhook notifications
3. **Custom Wazuh Rules** - Create rules for Sterling PDF security
4. **Integrate with Existing Stack** - Connect to Splunk, other SIEM if needed
5. **Set Up Log Rotation** - Configure Elasticsearch index lifecycle
6. **Enable SSL/TLS** - Secure agent-manager communication
7. **Dashboard Customization** - Create custom visualizations and dashboards

## Security Notes

- **Default credentials** are auto-generated but should be changed in production
- **Network isolation** - Containers run on dedicated `wazuh-network` bridge
- **Volume permissions** - Data directories are owned by root (containers)
- **Backup credentials** - `.env` file is the only copy of generated passwords

## Resource Requirements

| Component | RAM | CPU | Storage |
|-----------|-----|-----|----------|
| Elasticsearch | 1GB+ | 1 core | 10-20GB |
| Wazuh Manager | 512MB | 1 core | 1-2GB |
| Filebeat | 256MB | 0.5 core | 500MB |
| Dashboard | 512MB | 1 core | 1-2GB |
| **Total** | **~3GB** | **~3.5 cores** | **~25GB** |

## Support

- Wazuh Documentation: https://documentation.wazuh.com/
- Wazuh GitHub: https://github.com/wazuh/wazuh
- Elastic Beats: https://www.elastic.co/guide/en/beats/

## License

Wazuh is licensed under GPLv2 - free and open source.
