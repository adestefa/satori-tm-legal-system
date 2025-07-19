-- AppleScript to run the iSync adapter in a new Terminal window

-- Get the path to the directory containing this script
set scriptPath to POSIX path of (path to me)
set scriptDir to do shell script "dirname " & quoted form of scriptPath

-- The command to run in the new terminal window
-- This will change to the script's directory and then execute run.sh
set commandToRun to "cd " & quoted form of scriptDir & " && ./run.sh"

-- Open Terminal and run the command
tell application "Terminal"
	activate
	do script commandToRun
end tell
