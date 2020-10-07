const baseUrl = "https://test.metering.space/api/"

'Define the user credentials
dim username
dim password
dim token

const COMMUNICATION_PATH_ID = 107171


set oShell = CreateObject( "WScript.Shell" )
username = oShell.ExpandEnvironmentStrings("%C4_USER%")
password = oShell.ExpandEnvironmentStrings("%C4_PASS%")

Function ParseJson(strJson)
    Set html = CreateObject("htmlfile")
    Set window = html.parentWindow
    window.execScript "var json = " & strJson, "JScript"
    Set ParseJson = window.json
End Function

Function Authenticate()

    'declare a variable
    Dim objXmlHttp

    Set objXmlHttp = CreateObject("Microsoft.XMLHTTP")

    'If the API needs userName and Password authentication then pass the values here
    objXmlHttp.Open "POST", baseUrl+"login/user-login", False
    objXmlHttp.SetRequestHeader "Content-Type", "application/json"
    objXmlHttp.SetRequestHeader "User-Agent", "ASP/3.0"

    'send the json string to the API server
    objXmlHttp.Send "{""username"": """+username+""",""password"":"""+password+"""}"

    If objXmlHttp.Status <> 200 Then
        WScript.echo "Authentication has failed"
        WScript.Quit 1
    end if

    ASPPostJSON = CStr(objXmlHttp.ResponseText)

    Set objXmlHttp = Nothing

    'return the response from the API server
    set x = ParseJson(ASPPostJSON)
    Authenticate = x.token

End Function

Function GetMeters(CommunicationPathId)

    'declare a variable
    Dim objXmlHttp

    Set objXmlHttp = CreateObject("Microsoft.XMLHTTP")

    'If the API needs userName and Password authentication then pass the values here
    objXmlHttp.Open "GET", baseUrl+"acquisition/comm-path/"+CStr(CommunicationPathId)+"/meter/list", False
    objXmlHttp.SetRequestHeader "Content-Type", "application/json"
    objXmlHttp.SetRequestHeader "User-Agent", "ASP/3.0"
    objXmlHttp.SetRequestHeader "Authorization", "Bearer "+token

    objXmlHttp.Send

    If objXmlHttp.Status <> 200 Then
        WScript.echo "Listing Meters has failed"
        WScript.Quit 1
    end if

    ASPPostJSON = CStr(objXmlHttp.ResponseText)

    Set objXmlHttp = Nothing

    'return the response from the API server
    set x = ParseJson(ASPPostJSON)
    set GetMeters = x

End Function

Function GetVirtualMeters(MeterId)

    'declare a variable
    Dim objXmlHttp

    Set objXmlHttp = CreateObject("Microsoft.XMLHTTP")

    'If the API needs userName and Password authentication then pass the values here
    objXmlHttp.Open "GET", baseUrl+"acquisition/meter/"+CStr(MeterId)+"/virtual-meter/list", False
    objXmlHttp.SetRequestHeader "Content-Type", "application/json"
    objXmlHttp.SetRequestHeader "User-Agent", "ASP/3.0"
    objXmlHttp.SetRequestHeader "Authorization", "Bearer "+token

    objXmlHttp.Send

    If objXmlHttp.Status <> 200 Then
        WScript.echo "Listing Virtual Meter has failed"
        WScript.Quit 1
    end if

    ASPPostJSON = CStr(objXmlHttp.ResponseText)

    Set objXmlHttp = Nothing

    'return the response from the API server
    set x = ParseJson(ASPPostJSON)
    set GetVirtualMeters = x

End Function

Function GetAttributes(VirtualMeterId)

    'declare a variable
    Dim objXmlHttp

    Set objXmlHttp = CreateObject("Microsoft.XMLHTTP")

    'If the API needs userName and Password authentication then pass the values here
    objXmlHttp.Open "GET", baseUrl+"acquisition/virtual-meter/"+CStr(VirtualMeterId), False
    objXmlHttp.SetRequestHeader "Content-Type", "application/json"
    objXmlHttp.SetRequestHeader "User-Agent", "ASP/3.0"
    objXmlHttp.SetRequestHeader "Authorization", "Bearer "+token

    objXmlHttp.Send

    If objXmlHttp.Status <> 200 Then
        WScript.echo "Listing Attributes has failed"
        WScript.Quit 1
    end if

    ASPPostJSON = CStr(objXmlHttp.ResponseText)

    Set objXmlHttp = Nothing

    'return the response from the API server
    set x = ParseJson(ASPPostJSON)
    set GetAttributes = x

End Function

'call the function and pass the API URL
token = Authenticate()
set meters = GetMeters(COMMUNICATION_PATH_ID)

For i=0 To meters.Length-1
    meter_id = eval("meters.[" & i & "].id")
    meter_name = eval("meters.[" & i & "].name")
    wscript.echo "Meter: "+meter_name

    set virtual_meters = GetVirtualMeters(meter_id)
    For j=0 To virtual_meters.Length-1
        vm_id = eval("virtual_meters.[" & i & "].id")
        vm_name = eval("virtual_meters.[" & i & "].name")
        wscript.echo "    Virtual Meter: "+vm_name

        set attribute_object = GetAttributes(vm_id)
        set attributes = attribute_object.attributes

        For k=0 To attributes.Length-1
            attr_id = eval("attributes.[" & k & "].id")
            attr_value = eval("attributes.[" & k & "].value")
            if IsNull(attr_value) Then
                attr_value = ""
            End If
            wscript.echo "        "+attr_id+": "+CStr(attr_value)
        Next
    Next
Next
