# Quick script to run bot in PROD mode (for local testing)
# Usage: .\scripts\run_prod.ps1

Write-Host "🚀 Starting TTS Bot in PROD mode..." -ForegroundColor Green

# Check if .env.prod exists
if (-Not (Test-Path ".env.prod")) {
    Write-Host "❌ Error: .env.prod not found!" -ForegroundColor Red
    Write-Host "📝 Create it from template: Copy-Item config\.env.prod.example .env.prod" -ForegroundColor Yellow
    Write-Host "   Then edit .env.prod and add your PROD token" -ForegroundColor Yellow
    exit 1
}

# Activate venv
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "📝 Create it: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Set ENV=prod for explicit mode
$env:ENV = "prod"

# Run bot (will auto-load .env.prod)
Write-Host "🤖 Starting bot from src/tts_bot.py..." -ForegroundColor Green
Write-Host "Bot will auto-load .env.prod file" -ForegroundColor Cyan
Write-Host "⚠️  WARNING: This uses PRODUCTION token!" -ForegroundColor Red
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python src\tts_bot.py
