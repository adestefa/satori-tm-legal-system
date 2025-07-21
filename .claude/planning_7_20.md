# Plan to backup user files we process to github and delete off our Lindoe servers for saftey and performance
read `/Users/corelogic/satori-dev/TM/.claude/github_plan.md`

# plan to refactor github_plan.md to make it more maintainable and easier to understand
read `/Users/corelogic/satori-dev/TM/.claude/github_plan_refactor.md`

Now think about how github plan will help us improve output directories across all services to make it more maintainable and easier to understand
All output files should be stored in a single directory and should be named in a way that makes it easy to identify the case and the type of file it is

Part of that is ensuring we have a consistent naming convention for all files and this integrates with the upload service we now have that replaces the icloud sync service as we cannot connect to icloud directly as all the publishe modules are unsupported by apple And we do not want to buy a $100 Apple Developer account to use the icloud API at this time. our Go adapter service can use the file upload endpoints to connect directly to the mac os and get user permissions to run directly read from the local icloud system sync folder the go app can read and write to achiving the same results by getting around connecting to iscyn service over internet. 

# How we replaced iCloud sync with a standalone file upload system that allows users to upload ZIP files containing case folders. The system will extract these files directly into the `test-data/sync-test-cases/` directory for immediate processing by the existing Tiger-Monkey pipeline.
read `/Users/corelogic/satori-dev/TM/.claude/upload_service_doc.md`
