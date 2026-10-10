Set WshShell = CreateObject("WScript.Shell")
appDir = "C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app"
pythonwPath = appDir & "\.venv\Scripts\pythonw.exe"
checkUrl = "http://127.0.0.1:8000/api/health"

' Check if backend server is currently responding
isRunning = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.open "GET", checkUrl, False
http.setTimeouts 1000, 1000, 1000, 1000
http.send

If Err.Number = 0 Then
    If http.status = 200 Then
        isRunning = True
    End If
End If
On Error Goto 0

' Start server in background if not already running
If Not isRunning Then
    WshShell.CurrentDirectory = appDir & "\backend"
    WshShell.Run """" & pythonwPath & """ -m uvicorn app.main:app --host 127.0.0.1 --port 8000", 0, False
    WScript.Sleep 1500
End If

' Open the application in default web browser
WshShell.Run "http://127.0.0.1:8000"
