echo "Making connection to Apple and sending auth request..."
curl -X POST http://127.0.0.1:8000/api/icloud/test-connection | jq
