Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
desktop = shell.SpecialFolders("Desktop")
shortcutPath = desktop & "\NeonDrop.lnk"
targetPath = appDir & "\Start NeonDrop App.vbs"

Set shortcut = shell.CreateShortcut(shortcutPath)
shortcut.TargetPath = targetPath
shortcut.WorkingDirectory = appDir
shortcut.Description = "NeonDrop video downloader"
shortcut.Save

MsgBox "NeonDrop shortcut created on your desktop.", 64, "NeonDrop"
