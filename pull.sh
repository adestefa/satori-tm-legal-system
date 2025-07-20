echo "Pulling from main..."

git pull origin main

cd dashboard
echo "restarting dashboard..."
./restart.sh

