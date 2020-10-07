$application = "https://test.metering.space/api/";

# Define the user credentials
$username = $env:C4_USER;
$password = $env:C4_PASS; # Read-Host -Prompt "Enter your password: "

$communication_path_id = 107171

$headers = @{
    "Content-Type" = 'application/json'
    "Referer" = $application
    "Origin" = $application
}

Function Authenticate
{
    $creds = @{
        username = $username
        password = $password
    } | ConvertTo-Json

    try
    {
        $response = Invoke-RestMethod $application"login/user-login" -Method Post -Body $creds -Headers $headers;
        $token = $response.token;
        $headers['Authorization'] = "Bearer $token"
        return $token;
    }
    catch
    {
        $result = $_.Exception.Response.GetResponseStream();
        $reader = New-Object System.IO.StreamReader($result);
        $reader.BaseStream.Position = 0;
        $reader.DiscardBufferedData();
        $responseBody = $reader.ReadToEnd() | ConvertFrom-Json
        Write-Host "ERROR: $($responseBody.error)"
        return;
    }
}

Function Get-Meters
{
    param( [int]$CommunicationPathId )
    
    try
    {
        $response = Invoke-RestMethod $application"acquisition/comm-path/$CommunicationPathId/meter/list" -Method Get -Headers $headers;
        return $response;
    }
    catch
    {
        Write-Output $_
        $result = $_.Exception.Response.GetResponseStream();
        $reader = New-Object System.IO.StreamReader($result);
        $reader.BaseStream.Position = 0;
        $reader.DiscardBufferedData();
        $responseBody = $reader.ReadToEnd() | ConvertFrom-Json
        Write-Host "ERROR: $($responseBody.error)"
        return;
    }
}

Function Get-Virtual-Meters
{
    param( [int]$MeterId )
    
    try
    {
        $response = Invoke-RestMethod $application"acquisition/meter/$MeterId/virtual-meter/list" -Method Get -Headers $headers;
        return $response;
    }
    catch
    {
        Write-Output $_
        $result = $_.Exception.Response.GetResponseStream();
        $reader = New-Object System.IO.StreamReader($result);
        $reader.BaseStream.Position = 0;
        $reader.DiscardBufferedData();
        $responseBody = $reader.ReadToEnd() | ConvertFrom-Json
        Write-Host "ERROR: $($responseBody.error)"
        return;
    }
}

Function List-Attributes
{
    param( [int]$VirtualMeterId )
    
    try
    {
        $response = Invoke-RestMethod $application"acquisition/virtual-meter/$VirtualMeterId" -Method Get -Headers $headers;
        return $response;
    }
    catch
    {
        Write-Output $_
        $result = $_.Exception.Response.GetResponseStream();
        $reader = New-Object System.IO.StreamReader($result);
        $reader.BaseStream.Position = 0;
        $reader.DiscardBufferedData();
        $responseBody = $reader.ReadToEnd() | ConvertFrom-Json
        Write-Host "ERROR: $($responseBody.error)"
        return;
    }
}

$token = Authenticate
if ([string]::IsNullOrEmpty($token)) { throw "Authentication has failed" }

$meters = Get-Meters($communication_path_id)
if ([string]::IsNullOrEmpty($token)) { throw "Meter listing has failed" }

foreach ($meter in $meters) {
    $name = $meter.name
    Write-Output "Meter: $name"
    foreach ($vm in Get-Virtual-Meters($meter.id)) {
        $vmname = $vm.name
        Write-Output "    Virtual Meter: $vmname"
        $attribute_object = List-Attributes($vm.id)
        $attribute_object = $attribute_object.attributes | Format-Table -Property id, value
        Write-Output $attribute_object
    }
}
