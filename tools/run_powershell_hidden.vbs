Option Explicit
Dim shell, command, i, result
If WScript.Arguments.Count < 1 Then WScript.Quit 64
Set shell = CreateObject("WScript.Shell")
command = """" & shell.ExpandEnvironmentStrings("%SystemRoot%") & "\System32\WindowsPowerShell\v1.0\powershell.exe"" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File"
For i = 0 To WScript.Arguments.Count - 1
    If InStr(WScript.Arguments(i), Chr(34)) > 0 Then WScript.Quit 64
    command = command & " " & Chr(34) & WScript.Arguments(i) & Chr(34)
Next
result = shell.Run(command, 0, True)
WScript.Quit result
