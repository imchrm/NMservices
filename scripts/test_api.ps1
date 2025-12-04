# NMservices API Remote Testing Script (PowerShell)
# This script tests all API endpoints remotely using Invoke-RestMethod
# Usage: .\test_api.ps1 [-Host <host>] [-Port <port>] [-ApiKey <key>]

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [string]$ApiKey = "test_secret",
    [int]$Timeout = 10,
    [switch]$Verbose,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host @"
Usage: .\test_api.ps1 [OPTIONS]

Remote API testing script for NMservices.

OPTIONS:
    -Host <host>         API host (default: 127.0.0.1)
    -Port <port>         API port (default: 8000)
    -ApiKey <key>        X-API-Key header value (default: test_secret)
    -Timeout <seconds>   Request timeout (default: 10)
    -Verbose             Enable verbose output
    -Help                Show this help message

EXAMPLES:
    # Test local server with defaults
    .\test_api.ps1

    # Test remote server
    .\test_api.ps1 -Host api.example.com -Port 443 -ApiKey "your_api_key"

    # Verbose mode
    .\test_api.ps1 -Verbose

"@
    exit 0
}

# Test counters
$script:TotalTests = 0
$script:PassedTests = 0
$script:FailedTests = 0

# Build base URL
$BaseUrl = "http://${Host}:${Port}"

# Print header
function Print-Header {
    Write-Host "========================================"
    Write-Host "  NMservices API Remote Testing"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Base URL:     $BaseUrl" -ForegroundColor Yellow
    Write-Host "API Key:      $($ApiKey.Substring(0, 4))****" -ForegroundColor Yellow
    Write-Host "Timeout:      ${Timeout}s" -ForegroundColor Yellow
    Write-Host ""
}

# Print test result
function Print-Result {
    param(
        [string]$TestName,
        [string]$Status,
        [string]$Message
    )

    $script:TotalTests++

    if ($Status -eq "PASS") {
        $script:PassedTests++
        Write-Host "✓ " -NoNewline -ForegroundColor Green
        Write-Host $TestName
        if ($Verbose) {
            Write-Host "  $Message" -ForegroundColor Gray
        }
    }
    else {
        $script:FailedTests++
        Write-Host "✗ " -NoNewline -ForegroundColor Red
        Write-Host $TestName
        Write-Host "  $Message" -ForegroundColor Red
    }
}

# Print footer
function Print-Footer {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "Total tests:  $script:TotalTests"
    Write-Host "Passed:       $script:PassedTests" -ForegroundColor Green
    Write-Host "Failed:       $script:FailedTests" -ForegroundColor Red
    Write-Host "========================================"

    if ($script:FailedTests -eq 0) {
        Write-Host "All tests passed!" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host "Some tests failed!" -ForegroundColor Red
        exit 1
    }
}

# Make HTTP request
function Invoke-ApiRequest {
    param(
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Body = $null,
        [bool]$UseAuth = $false
    )

    $Uri = "$BaseUrl$Endpoint"
    $Headers = @{
        "Content-Type" = "application/json"
    }

    if ($UseAuth) {
        $Headers["X-API-Key"] = $ApiKey
    }

    try {
        $params = @{
            Uri                = $Uri
            Method             = $Method
            Headers            = $Headers
            TimeoutSec         = $Timeout
            UseBasicParsing    = $true
        }

        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Compress)
        }

        if ($Verbose) {
            Write-Host "Request: $Method $Uri" -ForegroundColor Gray
            if ($Body) {
                Write-Host "Body: $($params.Body)" -ForegroundColor Gray
            }
        }

        $response = Invoke-RestMethod @params
        return @{
            StatusCode = 200
            Body       = $response
        }
    }
    catch {
        $statusCode = 0
        $errorBody = $null

        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $errorBody = $reader.ReadToEnd() | ConvertFrom-Json -ErrorAction SilentlyContinue
            $reader.Close()
        }

        return @{
            StatusCode = $statusCode
            Body       = $errorBody
            Error      = $_.Exception.Message
        }
    }
}

# Test 1: Health check
function Test-HealthCheck {
    Write-Host ""
    Write-Host "[1/6] Testing health check endpoint..." -ForegroundColor Yellow

    $response = Invoke-ApiRequest -Method "GET" -Endpoint "/" -UseAuth $false

    if ($response.StatusCode -eq 200) {
        if ($response.Body.message -eq "NoMus API is running") {
            Print-Result "GET / - Health check" "PASS" "API is running"
        }
        else {
            Print-Result "GET / - Health check" "FAIL" "Unexpected response: $($response.Body)"
        }
    }
    else {
        Print-Result "GET / - Health check" "FAIL" "HTTP $($response.StatusCode) (expected 200)"
    }
}

# Test 2: Register without auth
function Test-RegisterNoAuth {
    Write-Host ""
    Write-Host "[2/6] Testing security - register without auth..." -ForegroundColor Yellow

    $body = @{
        phone_number = "+998900000000"
    }

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/register" -Body $body -UseAuth $false

    if ($response.StatusCode -eq 403) {
        if ($response.Body.detail -match "Could not validate credentials") {
            Print-Result "POST /register - No auth" "PASS" "Correctly rejected (403)"
        }
        else {
            Print-Result "POST /register - No auth" "FAIL" "Wrong error message: $($response.Body.detail)"
        }
    }
    else {
        Print-Result "POST /register - No auth" "FAIL" "HTTP $($response.StatusCode) (expected 403)"
    }
}

# Test 3: Register with wrong auth
function Test-RegisterWrongAuth {
    Write-Host ""
    Write-Host "[3/6] Testing security - register with wrong auth..." -ForegroundColor Yellow

    $oldApiKey = $script:ApiKey
    $script:ApiKey = "wrong_password"

    $body = @{
        phone_number = "+998900000000"
    }

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/register" -Body $body -UseAuth $true
    $script:ApiKey = $oldApiKey

    if ($response.StatusCode -eq 403) {
        if ($response.Body.detail -match "Could not validate credentials") {
            Print-Result "POST /register - Wrong auth" "PASS" "Correctly rejected (403)"
        }
        else {
            Print-Result "POST /register - Wrong auth" "FAIL" "Wrong error message: $($response.Body.detail)"
        }
    }
    else {
        Print-Result "POST /register - Wrong auth" "FAIL" "HTTP $($response.StatusCode) (expected 403)"
    }
}

# Test 4: Register with valid auth
function Test-RegisterSuccess {
    Write-Host ""
    Write-Host "[4/6] Testing user registration (legacy endpoint)..." -ForegroundColor Yellow

    $body = @{
        phone_number = "+998901234567"
    }

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/register" -Body $body -UseAuth $true

    if ($response.StatusCode -eq 200) {
        if ($response.Body.status -eq "ok" -and $response.Body.user_id) {
            Print-Result "POST /register - Success" "PASS" "User registered with ID: $($response.Body.user_id)"
        }
        else {
            Print-Result "POST /register - Success" "FAIL" "Invalid response structure: $($response.Body)"
        }
    }
    else {
        Print-Result "POST /register - Success" "FAIL" "HTTP $($response.StatusCode) (expected 200). Error: $($response.Error)"
    }
}

# Test 5: Register validation error
function Test-RegisterValidation {
    Write-Host ""
    Write-Host "[5/6] Testing validation - empty request body..." -ForegroundColor Yellow

    $body = @{}

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/register" -Body $body -UseAuth $true

    if ($response.StatusCode -eq 422) {
        Print-Result "POST /register - Validation error" "PASS" "Correctly rejected invalid data (422)"
    }
    else {
        Print-Result "POST /register - Validation error" "FAIL" "HTTP $($response.StatusCode) (expected 422)"
    }
}

# Test 6: Create order
function Test-CreateOrder {
    Write-Host ""
    Write-Host "[6/6] Testing order creation (legacy endpoint)..." -ForegroundColor Yellow

    $body = @{
        user_id     = 101
        tariff_code = "standard_300"
    }

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/create_order" -Body $body -UseAuth $true

    if ($response.StatusCode -eq 200) {
        if ($response.Body.status -eq "ok" -and $response.Body.order_id) {
            Print-Result "POST /create_order - Success" "PASS" "Order created with ID: $($response.Body.order_id)"
        }
        else {
            Print-Result "POST /create_order - Success" "FAIL" "Invalid response structure: $($response.Body)"
        }
    }
    else {
        Print-Result "POST /create_order - Success" "FAIL" "HTTP $($response.StatusCode) (expected 200). Error: $($response.Error)"
    }
}

# Main execution
Print-Header

# Run all tests
Test-HealthCheck
Test-RegisterNoAuth
Test-RegisterWrongAuth
Test-RegisterSuccess
Test-RegisterValidation
Test-CreateOrder

Print-Footer
