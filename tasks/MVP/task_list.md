# MVP TASK LIST

**ORDER OF OPERATIONS**
1. Execute tasks in the follow order, check them off as you go. 
2. Before you start a task take a scripts/backup.sh "<version>, "<checkpoint description>". to save current state so you can roll back any changes easily
3. After a task, capture what you did, the code changes and the expected results in this file: `/Users/corelogic/satori-dev/TM/tasks/MVP/work_history.md`
4. Remember proper testing and docs: `/Users/corelogic/satori-dev/TM/0_how_to_test.md`  and `/Users/corelogic/satori-dev/TM/dashboard/CLAUDE.md`


--

# DEFECTS

--

**TASKS**


# SETTINGS
1. [ ] Allow the Lawyer (admin) to add and remove users from the dashboard. They will be user accounts that can access the dashboard via their email address. Create a new page that will be a tab off the settings page that lets him add users by email address and generate a password. An email is sent to the user with link to enter the dashboard and create a password. 
2. [ ] This page lets the lawyer see the list of users. who has been invited and not accepted, who has accepted with date and the last time they signed in. it does not need to be that elaborate, just a simple list of users for now. the logs can come later.
3. [ ] Profile in the top right corner of the app should reflect the user's name and email address of who is signed in.
4. [ ] Only accounts flagged admin can access the setting page and the User Management tab. 



--