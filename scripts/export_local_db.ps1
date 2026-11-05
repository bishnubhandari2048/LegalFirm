# ============================================================================
# Export local lawfirm_db from Docker MySQL (erp-db-1) with UTF8MB4 encoding
# Usage: .\scripts\export_local_db.ps1
# ============================================================================

$ContainerName = "erp-db-1"
$DbName = "lawfirm_db"
$OutputFile = "lawfirm_db_backup.sql"

Write-Host "Exporting '$DbName' from Docker container '$ContainerName' to $OutputFile..." -ForegroundColor Cyan

docker exec $ContainerName mysqldump `
    -u root `
    -ppassword `
    --default-character-set=utf8mb4 `
    --single-transaction `
    --routines `
    --triggers `
    --databases $DbName > $OutputFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! Database backup saved to: $OutputFile" -ForegroundColor Green
    Write-Host "You can copy it to your Linux VPS using:" -ForegroundColor Yellow
    Write-Host "  scp $OutputFile user@<SERVER_IP>:/opt/lawfirm/"
} else {
    Write-Host "Failed to export database. Make sure container '$ContainerName' is running." -ForegroundColor Red
}
