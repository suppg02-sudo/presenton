# Wazuh POC Deployment - Complete

## What's Been Created

### Deployment Files
✓ `docker-compose.yml` - Main orchestration file
✓ `.env` - Secure credentials (chmod 600)
✓ `filebeat.yml` - Telemetry client configuration
✓ `generate-credentials.sh` - Credential generator
✓ `deploy.sh` - Automated deployment script
✓ `configure-fim.sh` - FIM configuration script
✓ `README.md` - Complete documentation

### Architecture Overview

```
Server: 10.2.1.182
  ├─┐
  │  └─┐
  │    ├─ Elasticsearch 8.15.0 (Port 9200)
  │    │
  │    ├─ Wazuh Manager 4.8.2 (Ports 1514, 1515, 55000, 55001, 55002)
  │    │
  │    ├─ Wazuh Filebeat 8.15.0
  │    │  ├─ Collects system logs
  │    │  ├─ Collects Wazuh agent events
  │    │  └─ Ships to Elasticsearch
  │    │
  │    └─ Wazuh Dashboard 4.8.2 (Port 5601)
  │       └─ Web UI for monitoring
  │
  ├─ Wazuh Agent (installed locally)
  │  ├─ FIM (File Integrity Monitoring)
  │  ├─ HIDS (Host Intrusion Detection)
  │  └─ Sends events to Manager
  │
  └─ Filebeat (container)
     ├─ Ships agent events
     ├─ Ships system logs
     └─ Ships FIM alerts
```

## One-Line Deployment

```bash
cd /media/docker/wazuh
sudo ./deploy.sh
```

This will:
1. Generate secure credentials
2. Create data directories
3. Pull Docker images
4. Start all containers
5. Wait for Elasticsearch
6. Install local Wazuh agent
7. Register agent with manager
8. Configure FIM

## Access Information

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://10.2.1.182:5601 | Review security events |
| **API** | http://10.2.1.182:55000/api | Automation & integration |
| **Elasticsearch** | http://10.2.1.182:9200 | Direct data access |

## Generated Credentials

Stored in `.env` (auto-generated):
```
Wazuh Admin: wazuh-admin / <generated_password>
Elasticsearch: elastic / <generated_password>
API Key: <generated_32_char_hex>
```

## What You'll See in Dashboard

### 1. Overview Tab
- Active agents: 1 (local-server)
- Security events: Real-time count
- Level 12+ alerts: High priority issues

### 2. Agents Tab
- Agent status: Active/Disconnected
- Last connection time
- OS information

### 3. Events Tab
- Security alerts (intrusions, FIM)
- System events (logs via Filebeat)
- Alert levels: 1-15 (1=info, 15=critical)

### 4. FIM (Syscheck) Tab
- Files added
- Files modified
- Files deleted
- Permission changes
- Checksum changes

## File Integrity Monitoring Configuration

### Monitored Paths
- `/etc/` - System configuration changes
- `/var/www/` - Web application changes (Sterling PDF)
- `/home/` - User file changes
- `/opt/` - Application installations
- `/usr/bin/` - Binary modifications
- `/boot/` - Boot configuration

### Scan Settings
- **Frequency**: Every 6 hours
- **Real-time**: Yes (immediate alerts)
- **Startup scan**: Yes (on agent restart)
- **Check attributes**: Size, permissions, ownership, MD5, SHA1

### Ignored Patterns
- System directories: `/var/log/`, `/var/lib/`, `/tmp/`, `/dev/`
- Log files: `*.log`, `*.bak`, `*.backup`, `*.tmp`
- Web cache: `/var/www/html/cache/`
- User cache: `*/.cache/`

## Telemetry (Filebeat)

### What It Monitors
1. **Wazuh Agent Events**
   - `/var/ossec/logs/alerts/alerts.log` - Security alerts
   - `/var/ossec/logs/active-responses.log` - Agent responses
   - `/var/ossec/logs/syscheck/*.log` - FIM events

2. **System Logs**
   - `/var/log/syslog` - System messages
   - `/var/log/auth.log` - Authentication attempts
   - `/var/log/kern.log` - Kernel events
   - Systemd journals - Service logs

### Why "Telemetry Client"?
Filebeat is called a telemetry client because it:
- Continuously monitors (like telemetry)
- Ships all events to central location
- Provides real-time visibility
- Acts as "eyes and ears" of your infrastructure

## Commands Reference

### Deploy
```bash
cd /media/docker/wazuh
sudo ./deploy.sh
```

### Start/Stop Containers
```bash
docker-compose up -d      # Start
docker-compose down         # Stop
docker-compose restart     # Restart all
docker-compose ps          # Status
```

### View Logs
```bash
docker-compose logs -f wazuh-manager
docker-compose logs -f wazuh-filebeat
docker-compose logs -f elasticsearch
```

### Agent Commands
```bash
# Check status
sudo systemctl status wazuh-agent

# Restart
sudo systemctl restart wazuh-agent

# Register (if needed)
sudo /var/ossec/bin/wazuh-control register 10.2.1.182 local-server <API_KEY>

# View logs
sudo tail -f /var/ossec/logs/ossec.log
```

### Reconfigure FIM
```bash
cd /media/docker/wazuh
sudo ./configure-fim.sh
```

### Check Health
```bash
# Elasticsearch
curl -u elastic:<password> http://localhost:9200/_cluster/health

# Wazuh API
curl http://localhost:55000/api/healthcheck

# Dashboard
curl http://localhost:5601
```

## Troubleshooting

### Container Issues
```bash
# Check what's running
docker-compose ps

# Check logs
docker logs wazuh-manager
docker logs wazuh-filebeat
docker logs elasticsearch

# Rebuild
docker-compose down
docker-compose up -d
```

### Agent Issues
```bash
# Check if registered
sudo /var/ossec/bin/wazuh-control list-agents

# Verify communication
sudo tail -f /var/ossec/logs/ossec.log

# Test manager connectivity
curl http://10.2.1.182:1514
```

### No Events in Dashboard
1. Check Filebeat: `docker logs wazuh-filebeat`
2. Check Manager: `docker logs wazuh-manager`
3. Check Agent: `sudo systemctl status wazuh-agent`
4. Verify FIM paths exist and are readable
5. Test file change: `touch /var/www/test.txt` → should see in dashboard

## Security Considerations

✓ **Credentials** - Auto-generated, stored in `.env` (chmod 600)
✓ **Network** - Containers on isolated bridge network (`wazuh-net`)
✓ **Volumes** - Persistent storage, data survives restarts
✓ **Backup** - Original configs backed up before changes

⚠️ **Production Notes**:
- Change default credentials
- Enable SSL/TLS for agent communication
- Configure log rotation for Elasticsearch
- Set up alert notifications (email, Slack, etc.)
- Use firewall rules to restrict port access

## Resource Requirements (Current POC)

| Component | RAM | CPU | Storage | Status |
|-----------|-----|-----|----------|--------|
| Elasticsearch | 512MB-1GB | 1 core | 10-20GB | Container |
| Wazuh Manager | 512MB | 1 core | 1-2GB | Container |
| Filebeat | 256MB | 0.5 core | 500MB | Container |
| Dashboard | 512MB | 1 core | 1-2GB | Container |
| Wazuh Agent | 256MB | 0.5 core | 100MB | Local |
| **Total** | **~2.5-3.5GB** | **~3.5 cores** | **~12-25GB** | |

## Verification Checklist

After deployment, verify:

- [ ] All containers running: `docker-compose ps`
- [ ] Elasticsearch healthy: `curl http://localhost:9200/_cluster/health`
- [ ] Wazuh Manager accessible: `curl http://localhost:55000/api/healthcheck`
- [ ] Dashboard loading: `curl http://localhost:5601`
- [ ] Agent registered: `sudo /var/ossec/bin/wazuh-control list-agents`
- [ ] Agent active: `sudo systemctl status wazuh-agent`
- [ ] FIM monitoring configured: Check `/var/ossec/etc/ossec.conf`
- [ ] Filebeat shipping logs: `docker logs wazuh-filebeat`
- [ ] Events appearing in dashboard: Check dashboard → Events tab

## Next Steps for Expansion

1. **Deploy Remote Agents** - On other servers
2. **Configure Notifications** - Email, Slack, webhook
3. **Create Custom Rules** - Sterling PDF specific security rules
4. **Integrate SIEM** - Connect to Splunk or other platforms
5. **Set Up Backups** - Elasticsearch snapshots, Wazuh configs
6. **Enable SSL/TLS** - Secure agent-manager communication
7. **Configure Log Rotation** - Elasticsearch index lifecycle management
8. **Dashboard Customization** - Create custom visualizations and dashboards

## Support & Documentation

- **Wazuh Docs**: https://documentation.wazuh.com/
- **Wazuh GitHub**: https://github.com/wazuh/wazuh
- **Elastic Beats**: https://www.elastic.co/guide/en/beats/current/

## Status

🎉 **Ready to Deploy!**

Run `sudo ./deploy.sh` to start the Wazuh POC.
