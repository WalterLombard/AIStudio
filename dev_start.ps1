# Navigate to project directory
Set-Location -Path "C:\AIStudio_Alt_Architecture"

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Display locally installed Ollama models
Write-Host "`n--- Local Ollama Models ---" -ForegroundColor Cyan
ollama list

# Launch Ollama server in a new window so it doesn't block the script
Write-Host "`nStarting Ollama server in background..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized

# Give the server 3 seconds to initialize
Start-Sleep -Seconds 3

# Verify API connectivity
Write-Host "`n--- Testing Ollama API Endpoint ---" -ForegroundColor Green
Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" | Select-Object -ExpandProperty models | Format-Table name, size, modified_at