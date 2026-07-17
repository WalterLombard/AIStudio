Set WshShell = CreateObject("WScript.Shell")
' Launch the underlying batch script silently to preserve environment checks
WshShell.Run "cmd.exe /c cd /d C:\Projectsai && launch_video_engine.bat", 0, False
Set WshShell = Nothing