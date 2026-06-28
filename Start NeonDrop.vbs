Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
codexPy = shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

cmd = "cmd /c cd /d """ & appDir & """ && " & _
      "(python app.py || py app.py || """ & codexPy & """ app.py)"

shell.Run cmd, 0, False
