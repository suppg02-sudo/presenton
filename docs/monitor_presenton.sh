#!/bin/bash
# Presenton Monitoring Script
# Shows real-time logs from Presenton container

echo "=== Presenton Monitoring ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "=== Presenton Monitoring ==="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "--- Container Status ---"
    docker ps --format "Name: {{.Names}} | Status: {{.Status}} | CPU: {{.CPUPerc}} | Memory: {{.MemUsage}}" | grep presenton || echo "Container not running!"
    echo ""
    
    echo "--- Recent Logs (last 15 lines) ---"
    docker logs presenton --tail 15 2>&1
    echo ""
    
    echo "--- Database Summary ---"
    docker exec presenton python3 -c "
import sqlite3
conn = sqlite3.connect('/app_data/fastapi.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM presentations')
pres_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM slides')
slides_count = cursor.fetchone()[0]
cursor.execute('SELECT id, title, created_at FROM presentations ORDER BY created_at DESC LIMIT 1')
latest = cursor.fetchone()
conn.close()
print(f'Presentations: {pres_count} | Slides: {slides_count}')
if latest:
    print(f'Latest: {str(latest[0])[:12]}... - {(latest[1] or \"\")[:30]}')
" 2>/dev/null || echo "Database not accessible"
    echo ""
    
    echo "--- Ollama Server Status ---"
    curl -s http://10.2.14.131:11434/api/ps 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for m in data.get('models', []):
        print(f\"{m['name']}: LOADED ({m.get('size_vram', 0)//1024//1024}MB VRAM)\")
except:
    print('No models loaded')
" || echo "Ollama server not accessible"
    echo ""
    
    echo "--- HTTP Test ---"
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 2>/dev/null || echo "000")
    if [ "$http_code" = "200" ]; then
        echo "✅ Presenton Web UI: OK ($http_code)"
    else
        echo "❌ Presenton Web UI: FAIL ($http_code)"
    fi
    echo ""
    
    echo "Updating in 5 seconds... (Ctrl+C to stop)"
    sleep 5
done
