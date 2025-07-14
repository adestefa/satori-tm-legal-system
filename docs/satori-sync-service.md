# Satori Sync Service: Information Architecture

This document outlines the information architecture of the dashboard's data synchronization and delivery service. It details how case data is read from the file system, stored, updated, and delivered to the frontend to be "painted" on the dashboard view.

## Core Principle: In-Memory Database

The service operates on a core principle of using an **in-memory database**. This means that for the lifetime of the server process, all information about the state of the case files is held in the server's RAM within a Python object. There is no external database file or on-disk cache; the file system itself is the single source of truth.

## Information Flow

The flow of data from the file system to the user's screen follows four distinct steps:

### 1. Source of Truth: The Monitored Directory

-   **Location:** `TM/test-data/sync-test-cases/`
-   **Role:** This directory is the ground truth for the application. The server is configured to monitor this specific path. Each subdirectory within this location is considered a unique "case".

### 2. Data Storage & Management: The `DataManager`

-   **File:** `dashboard/data_manager.py`
-   **Mechanism:** This module contains the `DataManager` class, which is the heart of the in-memory database.
-   **Process:**
    1.  When the server starts, a single instance of `DataManager` is created.
    2.  This instance has a property, `self.cases`, which is a standard Python list.
    3.  The `scan_cases()` method is called on startup. It walks the monitored directory, creates a structured `Case` object (defined in `models.py`) for each folder, and populates the `self.cases` list.
    4.  This list of `Case` objects persists in memory as long as the server is running.

### 3. Real-Time Updates: The `FileWatcher`

-   **File:** `dashboard/file_watcher.py`
-   **Mechanism:** To ensure the dashboard is always current, a `watchdog` observer runs in a background thread.
-   **Process:**
    1.  The `watchdog` library efficiently listens for any file system event (file creation, deletion, modification) within the monitored directory and its subdirectories.
    2.  When an event is detected, it triggers a callback function.
    3.  This callback function simply calls the `data_manager.scan_cases()` method again.
    4.  The `scan_cases()` method re-scans the entire directory and overwrites the `self.cases` list with a fresh, up-to-date representation of the file system. This ensures the in-memory database is always synchronized with the ground truth.

### 4. Data Delivery: The FastAPI

-   **File:** `dashboard/main.py`
-   **Mechanism:** The FastAPI application exposes the in-memory data to the frontend via a simple API.
-   **Process:**
    1.  The dashboard's JavaScript, running in the user's browser, is on a timer. Every few seconds, it makes a `GET` request to the `/api/cases` endpoint.
    2.  When the server receives this request, the endpoint function executes.
    3.  This function accesses the `DataManager` instance and returns the current contents of its `self.cases` list.
    4.  FastAPI automatically serializes this Python list of `Case` objects into a JSON array, which is sent back to the browser.
    5.  The browser's JavaScript receives this JSON and "paints" the dashboard view, re-rendering the case cards with the latest information.

## Diagram of Information Flow

```
[File System: sync-test-cases/]
        │
        │ 1. User or external process
        │    modifies a file.
        ▼
[Watchdog Listener (Background Thread)]
        │
        │ 2. Detects file system event.
        ▼
[DataManager.scan_cases()]
        │
        │ 3. Re-scans directory and updates
        │    the in-memory list of Case objects.
        ▼
[In-Memory Database (Python list: data_manager.cases)]
        │
        │ 5. FastAPI reads from this list.
        ▼
[GET /api/cases Endpoint]
        │
        │ 6. Serializes list to JSON and sends response.
        ▼
[Browser (JavaScript)]
        ^
        │ 4. Periodically polls the API endpoint.
        │ 7. Receives JSON and re-renders the UI.

```
