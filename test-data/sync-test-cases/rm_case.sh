
echo "Clearing case.."

# Run commands in a subshell to avoid changing the main script's directory
(cd ../../scripts && sh clear_case.sh $1)

echo "removing $1"
# This now runs in your original directory as intended
rm -rf $1





