# MVP TASK LIST

**ORDER OF OPERATIONS**
1. Execute tasks in the follow order, check them off as you go. 
2. Before you start a task take a scripts/backup.sh "<version>, "<checkpoint description>". to save current state so you can roll back any changes easily
3. After a task, capture what you did, the code changes and the expected results in this file: `/Users/corelogic/satori-dev/TM/tasks/MVP/task_list_diff.md`
4. Remember proper testing and docs: `/Users/corelogic/satori-dev/TM/.claude/memories/0_how_to_test.md`  and `/Users/corelogic/satori-dev/TM/dashboard/CLAUDE.md`


--

# DEFECTS
1. [x] Dashboard, user clicks New Cases, Rodriguez appears as expected, but is missing the CTA button. **RESOLVED:** Fixed polling interference with filter state. 10-second polling was resetting display styles applied by filters. 
2. [ ] Complaint Document after generation has wrong foramtting. all titles are shown left aligned without bold and line breaks. The edit view has perfect formatting. please copy that and makes sure the display view has the same formatting. 
3. [ ] Sync notifications are shown at the bottom of the page when I change my isync password it should show in the sync service section. . Make sure NO OTHER messages are shown at the bottom of the page please.
--

**TASKS**

# SYNC
1. [x] Move the sync error message notification section from the bottom of the page to the sync service section. **COMPLETED:** Added showSyncMessage() function to display sync notifications within iCloud Integration section.



--

# DASHBOARD

1. [x] Change "Review & Generate Packet" to just "Review Case" **COMPLETED:** Updated button text across all themes and backend code. 
2. [x] On the dashboard, upgrade the file list to use a Scrollable Frame with Zebra Striping This is the best solution. Placing the file list inside a fixed-height, scrollable container is crucial for scalability. It keeps the overall card size consistent and tidy, whether there are 3 files or 30. Instead of numbering each file (which can add clutter), simply add a count to the list's title. This is cleaner and gives the user the same at-a-glance information. Add File Type Icons: Placing a small icon for PDF, TXT, or DOCX next to each filename provides instant visual context about the file type, which can be very helpful. **COMPLETED:** Implemented scrollable container (120px height), zebra striping, professional SVG file type icons, and file count in header.
3. [ ] 


--

# SETTINGS
1. [ ] Allow the Lawyer (admin) to add and remove users from the dashboard. They will be user accounts that can access the dashboard via their email address. We will send them a OTC to verify it is them and then save their password and allow them to login to the dashboard. Create a new page that will be a tab off the settings page that lets him add users by email address then send them a OTC to verify it is them and then save their password and allow them to login to the dashboard. This page lets the lawyer see the list of users and their roles and permissions. who has been invited and not accepted, who has accepted with date and the last time they signed in with their macro action logs. it does not need to be that elaborate, just a simple list of users and their roles and permissions for now. the logs can come later.
2. [ ] Profile in the top right corner of the app should reflect the user's name and email address of who is signed in.
3. [ ] Only accounts flagged admin can access the setting page and the User Management tab. 



--

# HEADLESS V8 PDF FILE PRINTER
1. [ ] as per our plan, python-based pdf modules are inconsistent and unreliable. we will use headless v8 to print pdf files. we will do this by installing v8 in a container, then feed it the generated HTML files (compaint forms and summons html files) and then have it render them, then print as pdf which we will save to the case folder. As the HTML files are created usign tailwind, we have full acces to match any legal document down to the pixel and we can rely on v8 engine to print it as pdf perfectly. 

--

# ICLOUD SYNC

1. [x] implement iCloud sync functionality using the credentials stored in settings. This will sync case files bidirectionally between the dashboard and the law firm's iCloud account. **COMPLETED:** Full iCloud sync implementation with pyicloud integration, settings UI, API endpoints, and sync manager.
2. [ ] Create icloud test cases and health check of the serivce.
3. [ ] Make the icloud isync code a reusable service we can use in other projects. make configuration a json file


--