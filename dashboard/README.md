# TM Project Dashboard

This directory contains a standalone FastAPI application that provides a web-based dashboard for managing cases within the TM project.

## Architecture

The dashboard is composed of a Python backend and a JavaScript frontend, with a clear separation of concerns.

### Backend

- **Framework:** FastAPI
- **Language:** Python
- **Core Components:**
    - `main.py`: The main FastAPI application file. It serves the frontend, handles API requests, and manages the application lifecycle.
    - `data_manager.py`: A class responsible for scanning the case file directory and maintaining an in-memory list of case objects.
    - `file_watcher.py`: Uses the `watchdog` library to monitor the case directory for real-time changes (creations, modifications, deletions) and updates the `DataManager`.
    - `models.py`: Contains the Pydantic data models (`Case`, `FileMetadata`, `CaseStatus`) that define the structure of the application's data, ensuring type safety and consistency.

### Frontend

- **Frameworks:** Vanilla JavaScript and Tailwind CSS.
- **Structure:** The frontend is architected to support multiple, self-contained themes.
    - `static/themes/`: This directory holds a subdirectory for each available theme (e.g., `light`, `dark`).
    - Each theme directory contains its own `index.html`, `css`, and `js` assets.
- **JavaScript Modules:**
    - `api.js`: Handles all communication with the backend API.
    - `ui.js`: Responsible for all DOM manipulation, such as rendering the case cards.
    - `eventHandlers.js`: Manages user interactions, like button clicks.
    - `main.js`: The main entry point that orchestrates the frontend application.

## How to Run

Lifecycle scripts are provided for easy management of the server.

1.  **Start the server:**
    ```bash
    ./dashboard/start.sh
    ```
    This script will:
    - Install all Python and Node.js dependencies.
    - Build the necessary CSS files.
    - Start the FastAPI server and the Tailwind CSS watcher in the background.

2.  **Stop the server:**
    ```bash
    ./dashboard/stop.sh
    ```
    This script will read the process IDs from a `.pids` file and terminate the running services.

3.  **Restart the server:**
    ```bash
    ./dashboard/restart.sh
    ```

## Available Themes

The application supports multiple themes, which can be selected via a query parameter.

-   **Light Theme (Default):** `http://127.0.0.1:8000` or `http://127.0.0.1:8000/?theme=light`
-   **Dark Theme:** `http://127.0.0.1:8000/?theme=dark`

## API Endpoints

The backend exposes a simple RESTful API.

-   `GET /api/cases`: Retrieves a list of all detected cases.
-   `POST /api/cases/{case_id}/process`: Triggers the processing for a specific case.
-   `POST /api/refresh`: Manually forces a re-scan of the case directory.

## Next Steps

-   **Full Tiger/Monkey Integration:** Connect the "Process" and "Generate" buttons to the actual Tiger and Monkey service CLIs.
-   **Error Handling:** Improve error display on the frontend when API calls fail.
-   **State Management:** Implement more robust state management on the frontend to avoid full re-renders on every poll.
-   **User Authentication:** Add a login layer to secure the dashboard.
-   **Database Integration:** Replace the in-memory case list with a persistent database (e.g., SQLite or PostgreSQL) to maintain state across server restarts.

## Screenshot Utility

This project includes a command-line utility to take screenshots of web pages using Playwright.

-   **To take a screenshot:**
    ```bash
    ./dashboard/screenshot.sh <URL> <output_path.png>
    ```
-   **Example:**
    ```bash
    ./dashboard/screenshot.sh http://127.0.0.1:8000 screenshots/dashboard.png
    ```
    *(Ensure the server is running before taking a screenshot of the dashboard.)*


## Real-Time Updates & Testing

The dashboard is configured to monitor the `TM/test-data/sync-test-cases/` directory for any changes.

To test the real-time update functionality:
1.  Start the dashboard with `./dashboard/start.sh`.
2.  In your file explorer, make changes to the `TM/test-data/sync-test-cases/` directory. You can add, delete, or modify files and folders.
3.  Observe the dashboard UI, which should automatically update to reflect the changes within a few seconds.

