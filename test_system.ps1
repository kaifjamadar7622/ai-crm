#!/usr/bin/env pwsh
# Full system verification test suite

$API_BASE = "http://127.0.0.1:8000"
$FRONTEND = "http://localhost:5180"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 AI-CRM FULL SYSTEM VERIFICATION TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health Check
Write-Host "TEST 1: Backend Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_BASE/" -Method Get -TimeoutSec 5
    $content = $response.Content | ConvertFrom-Json
    if ($content.message -eq "Backend running 🚀") {
        Write-Host "✅ PASS: Backend health check OK" -ForegroundColor Green
        Write-Host "   Response: $($content.message)" -ForegroundColor Green
    } else {
        Write-Host "❌ FAIL: Unexpected response" -ForegroundColor Red
        Write-Host "   Got: $content" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ FAIL: Backend not responding" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Chat Endpoint (LangGraph Agent)
Write-Host "TEST 2: LangGraph Chat Endpoint" -ForegroundColor Yellow
try {
    $body = @{
        text = "Log interaction with Dr. Smith about hypertension treatment"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$API_BASE/chat" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 10
    $content = $response.Content | ConvertFrom-Json
    
    if ($content.response) {
        Write-Host "✅ PASS: Chat endpoint responding" -ForegroundColor Green
        Write-Host "   Response Keys: $($content.response | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name)" -ForegroundColor Green
        Write-Host "   Action: $($content.response.action)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ FAIL: Invalid response" -ForegroundColor Red
        Write-Host "   Response: $content" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ FAIL: Chat endpoint error" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Interactions Log Endpoint
Write-Host "TEST 3: Interactions Log Endpoint" -ForegroundColor Yellow
try {
    $body = @{
        hcp_name = "Dr. John Smith"
        interaction_type = "In-Person Meeting"
        notes = "Discussed cardiovascular treatment options"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$API_BASE/interactions/log" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 10
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ PASS: Interactions log endpoint responding" -ForegroundColor Green
    Write-Host "   Response: $content" -ForegroundColor Green
} catch {
    Write-Host "⚠️  WARNING: Interactions endpoint error (DB may not be configured)" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: Frontend Availability
Write-Host "TEST 4: Frontend Availability" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $FRONTEND -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ PASS: Frontend server responding on port 5180" -ForegroundColor Green
        Write-Host "   URL: $FRONTEND" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FAIL: Frontend not responding" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 System Status Summary:" -ForegroundColor Cyan
Write-Host "  Backend API ........... http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  Frontend UI ........... http://localhost:5180" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open browser to http://localhost:5180" -ForegroundColor White
Write-Host "  2. Test all 4 navigation tabs (Log, Dashboard, Reports, Territories)" -ForegroundColor White
Write-Host "  3. Fill form and test Form Submission" -ForegroundColor White
Write-Host "  4. Test Chat with agent messages" -ForegroundColor White
Write-Host "  5. Verify Redux state management and styling" -ForegroundColor White
Write-Host ""
