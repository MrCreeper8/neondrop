Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
appFile = appDir & "\NeonDrop App.pyw"

cmd = "cmd /c cd /d """ & appDir & """ && " & _
      "(pythonw """ & appFile & """ || python """ & appFile & """ || pyw -3 """ & appFile & """ || py -3 """ & appFile & """)"

shell.Run cmd, 0, False
