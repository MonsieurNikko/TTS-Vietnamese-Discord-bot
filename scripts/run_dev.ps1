# Quick script to run bot in DEV mode
# Usage: .\scripts\run_dev.ps1

Write-Host "🚀 Starting TTS Bot in DEV mode..." -ForegroundColor Green

# Check if .env.dev exists
if (-Not (Test-Path ".env.dev")) {
    Write-Host "❌ Error: .env.dev not found!" -ForegroundColor Red
    Write-Host "📝 Create it from template: Copy-Item config\.env.dev.example .env.dev" -ForegroundColor Yellow
    Write-Host "   Then edit .env.dev and add your DEV token" -ForegroundColor Yellow
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

# Set ENV=dev for explicit mode (optional, bot auto-detects .env.dev)
$env:ENV = "dev"

# Run bot (will auto-load .env.dev)
Write-Host "🤖 Starting bot from src/tts_bot.py..." -ForegroundColor Green
Write-Host "Bot will auto-load .env.dev file" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python src\tts_bot.py
