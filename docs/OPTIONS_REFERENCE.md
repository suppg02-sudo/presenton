# Wazuh POC Deployment - Complete Instructions

## ✅ Working Infrastructure

| Service | Container | Status | Port | Access |
|---------|-----------|--------|-------|--------|
| **Elasticsearch** | wazuh-elasticsearch | ✅ Running | 9200, 9300 | http://10.2.1.182:9200/_cluster/health |
| **Wazuh Manager** | wazuh-manager | ✅ Running | 55000 | http://10.2.1.182:55000/api/healthcheck |
| **Wazuh Filebeat** | wazuh-filebeat | ✅ Running | - | Collects and ships logs |
| **Wazuh API** | Port 55000 | ✅ Available | http://10.2.1.182:55000/api |

---

## 🎯 Access Options

### Option 1: CLI Dashboard Script (Recommended for POC)

**Simple command-line interface** - No web UI needed!

```bash
cd /media/docker/wazuh
./wazuh-cli-dashboard.sh
```

**Features:**
- ✅ View agent status
- ✅ Get recent security events (last 20)
- ✅ Get file integrity monitoring events (last 20)
- ✅ All data via Wazuh Manager API
- ✅ No web UI dependencies
- ✅ Works even when web dashboard fails

**Script Location:** `/media/docker/wazuh/wazuh-cli-dashboard.sh`

---

### Option 2: Alternative Web Dashboard (HTTPS)

**Uses port 443 instead of 5601** - Should avoid port conflicts!

```bash
cd /media/docker/wazuh
docker-compose -f docker-compose-dashboard-v2.yml up -d
```

**Dashboard URL:** https://srvdocker02:443

**Login Credentials:**
```bash
cat /media/docker/wazuh/.env
```

**Key Changes:**
- Disables indexer service (fixes the `wazuh.indexer` error)
- Uses HTTPS port 443 (may avoid conflicts)
- Uses separate container and data volume
- Same backend services (Elasticsearch, Wazuh Manager)

---

## 🔧 Troubleshooting Dashboard v2

**If Option 2 fails:**

```bash
# Check logs
docker-compose -f docker-compose-dashboard-v2.yml logs wazuh-dashboard-v2

# Restart
docker-compose -f docker-compose-dashboard-v2.yml restart wazuh-dashboard-v2

# Clean restart
docker-compose -f docker-compose-dashboard-v2.yml down
docker-compose -f docker-compose-dashboard-v2.yml up -d
```

---

## 📋 What to Choose

### Choose Option 1 (CLI Dashboard) if:
- ✅ You want a simple, fast interface
- ✅ Web UI issues continue
- ✅ You only need to view data for POC
- ✅ You prefer command-line tools

### Choose Option 2 (Web Dashboard v2) if:
- ✅ You want full visual dashboards
- ✅ You need graphical event analysis
- ✅ HTTPS is preferred over HTTP
- ✅ Port 5601 has conflicts with other services

---

## 🚀 Quick Start (Option 1)

```bash
cd /media/docker/wazuh
./wazuh-cli-dashboard.sh

# Then select option 1, 2, or 3 from menu
```

---

## 🚀 Quick Start (Option 2)

```bash
cd /media/docker/wazuh
docker-compose -f docker-compose-dashboard-v2.yml up -d

# Then access: https://srvdocker02:443
```

---

## 📊 Current Issues Summary

**Original Issue:** Wazuh Dashboard web UI stuck trying to resolve `wazuh.indexer` hostname
**Root Cause:** Container expects an indexer service that doesn't exist in this deployment
**Impact:** Web dashboard not accessible via browser

**Solution:**
- ✅ **Option 1 (Recommended)**: CLI dashboard script - works with API directly
- ✅ **Option 2 (Alternative)**: Web dashboard on port 443 - disables indexer dependency

**What's Working:**
- ✅ Elasticsearch - Storing events
- ✅ Wazuh Manager - Processing security alerts
- ✅ Wazuh Filebeat - Collecting and shipping logs
- ✅ Wazuh API - Providing access to all data
- ⚠️ Wazuh Dashboard Web UI - Has indexer dependency issue

---

## 📝 Recommendation for POC

**For your POC (security monitoring + file integrity), use Option 1: CLI Dashboard**

**Reasons:**
1. Simpler - just view events from command line
2. Faster - no web UI overhead
3. Reliable - doesn't depend on problematic dashboard
4. Direct API access - full data control
5. All security monitoring functionality works

**Later expansion (full UI needed):**
- Consider deploying Wazuh Dashboard v3.x or 4.x (newer version without indexer dependency)
- Or use a separate dashboard service
- Or use Wazuh's hosted cloud dashboard

---

## 📚 Documentation

- **Wazuh API Docs:** https://documentation.wazuh.com/current/api/overview.html
- **Wazuh Guide:** https://documentation.wazuh.com/current/user-manual/
- **CLI Dashboard:** Run `./wazuh-cli-dashboard.sh` and follow prompts

---

## 🎯 Summary

**You have TWO options to access Wazuh data:**

1. ✅ **CLI Dashboard** (`./wazuh-cli-dashboard.sh`) - **RECOMMENDED FOR POC**
2. ✅ **Web Dashboard v2** (`docker-compose -f docker-compose-dashboard-v2.yml up`) - **Alternative on port 443**

**Both options use the same working backend services!**

**Start with Option 1 now for immediate access to your security events!** 🚀
