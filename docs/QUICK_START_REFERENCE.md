# Wazuh POC - Quick Start Guide

## 🚀 Deploy in 30 Seconds

```bash
cd /media/docker/wazuh
sudo ./deploy.sh
```

That's it! The script handles everything automatically.

---

## 📊 Access Your Dashboard

**URL:** http://10.2.1.182:5601

**Login:** Check `.env` file for credentials:
```bash
cat /media/docker/wazuh/.env
```

---

## 🎯 What You'll See

### 1. Security Events
- Failed login attempts
- File integrity changes
- System modifications
- Malicious activity alerts

### 2. File Integrity Monitoring (FIM)
- Changes to `/etc/`
- Changes to `/var/www/` (Sterling PDF)
- Changes to `/home/`
- Changes to `/opt/`

### 3. System Logs
- `/var/log/auth.log` - Auth events
- `/var/log/syslog` - System events
- Kernel messages

---

## 🔧 Configure FIM (Optional)

If you want to adjust monitored paths or scan frequency:

```bash
cd /media/docker/wazuh
sudo ./configure-fim.sh
```

Default FIM config:
- Monitors: `/etc/`, `/var/www/`, `/home/`, `/opt/`
- Scan every: 6 hours
- Real-time: Yes

---

## 📋 Common Commands

### Check Services
```bash
cd /media/docker/wazuh
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs wazuh-manager
docker logs wazuh-filebeat
```

### Check Agent Status
```bash
sudo systemctl status wazuh-agent
sudo tail -f /var/ossec/logs/ossec.log
```

### Restart Everything
```bash
docker-compose restart
```

### Stop Everything
```bash
docker-compose down
```

---

## 🆘 Troubleshooting

### Dashboard Not Loading?
```bash
# Check if containers are running
docker-compose ps

# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check logs
docker logs wazuh-elasticsearch
```

### No Events in Dashboard?
```bash
# Check agent status
sudo systemctl status wazuh-agent

# Check Filebeat
docker logs wazuh-filebeat

# Verify FIM is configured
grep syscheck /var/ossec/etc/ossec.conf
```

### Port Already in Use?
```bash
# Check what's using ports
sudo netstat -tulpn | grep -E '1515|55000|9200|5601'

# Stop conflicting service
sudo systemctl stop <conflicting-service>
```

---

## 📚 Documentation

- **Full Guide:** `README.md`
- **Deployment Summary:** `DEPLOYMENT_SUMMARY.md`
- **Online Docs:** https://documentation.wazuh.com/

---

## 🎉 Ready to Deploy!

Run this now:
```bash
cd /media/docker/wazuh
sudo ./deploy.sh
```

Then open http://10.2.1.182:5601 in your browser.
