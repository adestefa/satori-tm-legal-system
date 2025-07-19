-- AppleScript to run Satori Secure File Sync in LOCAL mode

-- Get the path to the directory containing this script
set scriptPath to POSIX path of (path to me)
set scriptDir to do shell script "dirname " & quoted form of scriptPath

-- The command to run in the new terminal window
set commandToRun to "cd " & quoted form of scriptDir & " && ./run.sh local"

-- Open Terminal and run the command
tell application "Terminal"
	activate
	do script commandToRun
end tell