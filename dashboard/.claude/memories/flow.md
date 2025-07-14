1. Initial Load & State Recovery:
       * When the dashboard starts, the DataManager is initialized. It's given two key paths: the CASE_DIRECTORY (where raw case
         files are) and the OUTPUT_DIR (where processed files are stored).
       * The DataManager scans the CASE_DIRECTORY for case folders. For each folder, it creates a Case object.
       * Crucially, during this creation, it performs state recovery. It checks the OUTPUT_DIR for a corresponding folder for that
         case. If it finds a hydrated.json file, it intelligently infers that the case has already been processed. It then updates
         the Case object's status to PENDING_REVIEW and sets the classified and extracted progress flags to true. This prevents the
          system from "forgetting" progress after a restart.
       * If no output files are found, the case is considered NEW.


   2. Frontend Rendering:
       * The user's browser loads the dashboard's index.html. This file contains a clean container for the case cards, with no
         hardcoded data.
       * JavaScript modules (main.js, ui.js, api.js) are loaded.
       * main.js immediately calls the /api/cases endpoint.
       * While waiting for the API response, ui.js renders a "Loading cases..." state on the screen.


   3. Dynamic Content Display:
       * The FastAPI backend receives the /api/cases request and returns a JSON list of all the Case objects that the DataManager
         has in memory.
       * Once the frontend receives the JSON data, ui.js dynamically renders the case cards on the page, populating them with the
         correct data, status, and progress lights based on the API response.


   4. User-Triggered Processing:
       * The user clicks the "Process Files" button on a case card.
       * eventHandlers.js captures this click event. It correctly identifies the case_id from the data-case-id attribute on the
         button's parent element.
       * An API call is made to POST /api/cases/{case_id}/process.


   5. Backend Processing & State Update:
       * The backend receives the processing request. It uses the service_runner.py to trigger the Tiger service in the
         background.
       * The DataManager immediately updates the in-memory state of the case to PROCESSING.
       * The Tiger service runs, processing the documents and eventually creating a hydrated.json file in the
         dashboard/outputs/{case_id}/ directory.


   6. Real-time Polling and UI Updates:
       * The frontend has a polling mechanism (set up in main.js) that periodically calls the /api/cases endpoint every few
         seconds.
       * On each poll, the frontend gets the latest state of all cases from the DataManager.
       * ui.js then re-renders the case cards with the updated information. This is how the user sees the status change from "New"
         to "Processing" and sees the progress lights turn green as the backend completes its work, without needing to refresh the
         page.


   7. Final State:
       * Once the Tiger service is finished and the hydrated.json is created, the next time the DataManager provides the case
         status (either through polling or a full refresh), it will show the status as PENDING_REVIEW and the classified and
         extracted progress as complete. This state is now persistent because it's based on the existence of the output file.