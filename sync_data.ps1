# LifeLog Data Sync Script (PowerShell)

# 1. Pull data from Docker to Local
function Pull-Data {
    docker cp lifelog-backend-1:/app/data/lifelog.db backend/data/lifelog.db
    Write-Host "Data pulled from Docker to backend/data/lifelog.db" -ForegroundColor Green
}

# 2. Push data from Local to Docker
function Push-Data {
    docker cp backend/data/lifelog.db lifelog-backend-1:/app/data/lifelog.db
    docker restart lifelog-backend-1
    Write-Host "Data pushed from Local to Docker and backend restarted." -ForegroundColor Green
}

# Usage: 
# . ./sync_data.ps1
# Pull-Data
# Push-Data
