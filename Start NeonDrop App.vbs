Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
codexPy = shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
appFile = appDir & "\NeonDrop App.pyw"

cmd = "cmd /c cd /d """ & appDir & """ && " & _
      "(pythonw """ & appFile & """ || python """ & appFile & """ || pyw """ & appFile & """ || py """ & appFile & """ || """ & codexPy & """ """ & appFile & """)"

shell.Run cmd, 0, False
