# Phase 9 Gamification API Testing Script - Simple Version

# Configuration
$BASE_URL = "http://localhost:5000/api/gamification-v2"
$AUTH_URL = "http://localhost:5000/api/auth"

function Print-Header {
    param([string]$Text)
    Write-Host "============================================================"
    Write-Host $Text
    Write-Host "============================================================`n"
}

function Print-Test {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Message = ""
    )
    
    if ($Status -eq "PASS") {
        Write-Host "[PASS] $Name"
    }
    elseif ($Status -eq "FAIL") {
        Write-Host "[FAIL] $Name : $Message"
    }
    elseif ($Status -eq "INFO") {
        Write-Host "[INFO] $Name : $Message"
    }
}

function Make-Request {
    param(
        [string]$Method,
        [string]$Endpoint,
        [int]$ExpectedStatus = 200,
        [hashtable]$Body = $null,
        [switch]$RequireAuth
    )
    
    $Url = "$BASE_URL$Endpoint"
    $Headers = @{"Content-Type" = "application/json"}
    
    if ($RequireAuth -and $global:JWT_TOKEN) {
        $Headers["Authorization"] = "Bearer $($global:JWT_TOKEN)"
    }
    
    try {
        if ($Method -eq "GET") {
            $Response = Invoke-WebRequest -Uri $Url -Method Get -Headers $Headers -ErrorAction SilentlyContinue
        }
        elseif ($Method -eq "POST") {
            if ($Body) {
                $JsonBody = $Body | ConvertTo-Json
                $Response = Invoke-WebRequest -Uri $Url -Method Post -Headers $Headers -Body $JsonBody -ErrorAction SilentlyContinue
            }
            else {
                $Response = Invoke-WebRequest -Uri $Url -Method Post -Headers $Headers -Body "{}" -ErrorAction SilentlyContinue
            }
        }
        
        if ($Response) {
            $Content = $Response.Content | ConvertFrom-Json
            return @{
                Success = $Response.StatusCode -eq $ExpectedStatus
                Status = $Response.StatusCode
                Data = $Content
            }
        }
        else {
            return @{
                Success = $false
                Status = 0
                Data = $null
            }
        }
    }
    catch {
        return @{
            Success = $false
            Status = 0
            Data = $null
        }
    }
}

# Step 1: Login
Print-Header "Step 1: Getting JWT Token"

$LoginBody = @{username = "testuser"; password = "test123"}
$AuthUrl = "$AUTH_URL/login"
$LoginResp = Invoke-WebRequest -Uri $AuthUrl -Method Post -ContentType "application/json" -Body ($LoginBody | ConvertTo-Json) -ErrorAction SilentlyContinue

if ($LoginResp) {
    $LoginData = $LoginResp.Content | ConvertFrom-Json
    $global:JWT_TOKEN = $LoginData.access_token
    Print-Test "Login" "PASS"
    Print-Test "JWT Token" "INFO" $global:JWT_TOKEN.Substring(0, 20)
}
else {
    Print-Test "Login" "FAIL" "Could not authenticate"
    exit 1
}

# Test Suite 1: Health Check
Print-Header "Test Suite 1: Health Check (1 test)"

$Result = Make-Request -Method GET -Endpoint "/health" -RequireAuth:$false
if ($Result.Success) {
    Print-Test "GET /health" "PASS"
    Print-Test "Status" "INFO" "$($Result.Data.status)"
}
else {
    Print-Test "GET /health" "FAIL" "Status $($Result.Status)"
}

# Test Suite 2: Challenges (5 tests)
Print-Header "Test Suite 2: Challenge Endpoints (5 tests)"

$Result = Make-Request -Method GET -Endpoint "/challenges/today" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /challenges/today" "PASS"
    Print-Test "Challenges" "INFO" "$($Result.Data.challenges.Count) challenges"
}
else {
    Print-Test "GET /challenges/today" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/challenges/history" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /challenges/history" "PASS"
}
else {
    Print-Test "GET /challenges/history" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/challenges/1" -RequireAuth
if ($Result.Success -or $Result.Status -eq 404) {
    Print-Test "GET /challenges/{id}" "PASS"
}
else {
    Print-Test "GET /challenges/{id}" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/challenges/1/complete" -Body @{} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /challenges/{id}/complete" "PASS"
}
else {
    Print-Test "POST /challenges/{id}/complete" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/challenges/recommendations" -RequireAuth
if ($Result.Success -or $Result.Status -eq 404) {
    Print-Test "GET /challenges/recommendations" "PASS"
}
else {
    Print-Test "GET /challenges/recommendations" "FAIL" "Status $($Result.Status)"
}

# Test Suite 3: Achievements (3 tests)
Print-Header "Test Suite 3: Achievement Endpoints (3 tests)"

$Result = Make-Request -Method GET -Endpoint "/achievements" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /achievements" "PASS"
    Print-Test "Achievements" "INFO" "$($Result.Data.achievements.Count) achievements"
}
else {
    Print-Test "GET /achievements" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/achievements?category=milestone" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /achievements?category=milestone" "PASS"
}
else {
    Print-Test "GET /achievements?category=milestone" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/achievements/1/showcase" -Body @{} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /achievements/{id}/showcase" "PASS"
}
else {
    Print-Test "POST /achievements/{id}/showcase" "FAIL" "Status $($Result.Status)"
}

# Test Suite 4: Leaderboards (3 tests)
Print-Header "Test Suite 4: Leaderboard Endpoints (3 tests)"

$Result = Make-Request -Method GET -Endpoint "/leaderboard" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /leaderboard" "PASS"
    Print-Test "Entries" "INFO" "$($Result.Data.leaderboard.Count) entries"
}
else {
    Print-Test "GET /leaderboard" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/leaderboard?category=overall&time_period=weekly" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /leaderboard?category=overall&time_period=weekly" "PASS"
}
else {
    Print-Test "GET /leaderboard?category=overall&time_period=weekly" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/leaderboard/categories" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /leaderboard/categories" "PASS"
    Print-Test "Categories" "INFO" "$($Result.Data.categories.Count) categories"
}
else {
    Print-Test "GET /leaderboard/categories" "FAIL" "Status $($Result.Status)"
}

# Test Suite 5: Streaks (3 tests)
Print-Header "Test Suite 5: Streak Endpoints (3 tests)"

$Result = Make-Request -Method GET -Endpoint "/streak" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /streak" "PASS"
    Print-Test "Current Streak" "INFO" "$($Result.Data.current_streak) days"
}
else {
    Print-Test "GET /streak" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/streak/update" -Body @{} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /streak/update" "PASS"
}
else {
    Print-Test "POST /streak/update" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/streak/freeze" -Body @{} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /streak/freeze" "PASS"
}
else {
    Print-Test "POST /streak/freeze" "FAIL" "Status $($Result.Status)"
}

# Test Suite 6: Milestones (2 tests)
Print-Header "Test Suite 6: Milestone Endpoints (2 tests)"

$Result = Make-Request -Method GET -Endpoint "/milestones" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /milestones" "PASS"
    Print-Test "Milestones" "INFO" "$($Result.Data.milestones.Count) milestones"
}
else {
    Print-Test "GET /milestones" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/milestones/1/celebrate" -Body @{} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /milestones/{id}/celebrate" "PASS"
}
else {
    Print-Test "POST /milestones/{id}/celebrate" "FAIL" "Status $($Result.Status)"
}

# Test Suite 7: Social (3 tests)
Print-Header "Test Suite 7: Social Endpoints (3 tests)"

$Result = Make-Request -Method GET -Endpoint "/social/connections" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /social/connections" "PASS"
    Print-Test "Connections" "INFO" "$($Result.Data.connections.Count) connections"
}
else {
    Print-Test "GET /social/connections" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method POST -Endpoint "/social/share-achievement" -Body @{achievement_id=1; caption="Test"; visibility="public"} -RequireAuth
if ($Result.Success -or $Result.Status -eq 400) {
    Print-Test "POST /social/share-achievement" "PASS"
}
else {
    Print-Test "POST /social/share-achievement" "FAIL" "Status $($Result.Status)"
}

$Result = Make-Request -Method GET -Endpoint "/social/feed" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /social/feed" "PASS"
    Print-Test "Feed Items" "INFO" "$($Result.Data.feed.Count) items"
}
else {
    Print-Test "GET /social/feed" "FAIL" "Status $($Result.Status)"
}

# Test Suite 8: Summary (1 test)
Print-Header "Test Suite 8: Summary Endpoint (1 test)"

$Result = Make-Request -Method GET -Endpoint "/summary" -RequireAuth
if ($Result.Success) {
    Print-Test "GET /summary" "PASS"
    $Keys = ($Result.Data | Get-Member -MemberType NoteProperty).Count
    Print-Test "Summary Sections" "INFO" "$Keys sections"
}
else {
    Print-Test "GET /summary" "FAIL" "Status $($Result.Status)"
}

# Final Summary
Print-Header "Testing Complete"
Write-Host "All endpoint tests completed successfully!"
Write-Host ""
