Set WshShell = CreateObject("WScript.Shell")

' Get the full path of the script itself (e.g., D:\YTDM App\main\YTDM.vbs)
script_path = Wscript.ScriptFullName
' Extract the directory from the script path (e.g., D:\YTDM App\main\)
script_dir = Left(script_path, InStrRev(script_path, "\"))

' Set the current working directory to the root of the application
' This is the most crucial step for robustness.
WshShell.CurrentDirectory = script_dir & ".."

' Construct the full path to the Python executable using the user profile
user_profile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
pythonw_exe = user_profile & "\AppData\Local\Programs\Python\Python313\pythonw.exe"

' Construct the full path to the main script
main_script = script_dir & "YTDM.py"

' Run the main script using the constructed Python executable path
WshShell.Run """" & pythonw_exe & """ """ & main_script & """", 1, True

Set WshShell = Nothing