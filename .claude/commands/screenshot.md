
<ROLE>

You are a automated browser agent who will open the browser.

**SCREENSHOT SAVE FOLDER**/Users/corelogic/satori-dev/TM/outputs/screenshots

Steps:
1. navigate to the url provided by the user in the TEST_URL variable.
2. if the page does not load save a file called **SCREENSHOT SAVE FOLDER**failed.png and alert the user so then can check the browser console for errors and fix them.
3. Take a screenshot of the page and save it **SCREENSHOT SAVE FOLDER**screen_<date>_<time>_<version>.png
4. alert the user by using the speak tool when the test is over with a 10 word summary short message of the state.
5. after you save the screenshot move it to **SCREENSHOT SAVE FOLDER**

</ROLE>

<TEST_URL>
$ARGUMENTS
</TEST_URL>




<TOOL_INSTRUCTIONS>
# Playwright Browser Automation Tools Documentation

This document provides comprehensive documentation for the Playwright browser automation tools available in Claude Code.

## Overview

Playwright tools enable full browser automation including navigation, interaction, screenshots, and testing. These tools are prefixed with `mcp__playwright__browser_` and provide programmatic control over web browsers.

## Core Capabilities

### Navigation & Page Control

#### `mcp__playwright__browser_navigate`
Navigate to any URL.
```
Parameters:
- url (required): The URL to navigate to
```

#### `mcp__playwright__browser_navigate_back`
Go back to the previous page in browser history.
```
Parameters: None
```

#### `mcp__playwright__browser_navigate_forward`
Go forward to the next page in browser history.
```
Parameters: None
```

#### `mcp__playwright__browser_close`
Close the current browser page.
```
Parameters: None
```

#### `mcp__playwright__browser_resize`
Resize the browser window to specific dimensions.
```
Parameters:
- width (required): Width of browser window in pixels
- height (required): Height of browser window in pixels
```

### Screenshots & Visual Capture

#### `mcp__playwright__browser_take_screenshot`
Capture screenshots of the entire page or specific elements.
```
Parameters:
- element (optional): Human-readable description of element to screenshot
- ref (optional): Exact element reference from page snapshot
- filename (optional): Custom filename for screenshot
- raw (optional): Return PNG format instead of JPEG (default: false)

Note: If element is provided, ref must also be provided
```

#### `mcp__playwright__browser_snapshot`
Capture accessibility snapshot of the current page. This is often better than screenshots for analysis as it provides structured data about page elements.
```
Parameters: None
```

### Element Interaction

#### `mcp__playwright__browser_click`
Click on web page elements.
```
Parameters:
- element (required): Human-readable description of element to click
- ref (required): Exact element reference from page snapshot
```

#### `mcp__playwright__browser_type`
Type text into editable elements like input fields.
```
Parameters:
- element (required): Human-readable description of target element
- ref (required): Exact element reference from page snapshot
- text (required): Text to type into the element
- slowly (optional): Type one character at a time (default: false)
- submit (optional): Press Enter after typing (default: false)
```

#### `mcp__playwright__browser_hover`
Hover mouse over an element to trigger hover effects.
```
Parameters:
- element (required): Human-readable description of element
- ref (required): Exact element reference from page snapshot
```

#### `mcp__playwright__browser_drag`
Perform drag and drop operations between elements.
```
Parameters:
- startElement (required): Human-readable description of source element
- startRef (required): Exact source element reference
- endElement (required): Human-readable description of target element
- endRef (required): Exact target element reference
```

#### `mcp__playwright__browser_select_option`
Select options from dropdown menus.
```
Parameters:
- element (required): Human-readable description of dropdown
- ref (required): Exact element reference from page snapshot
- values (required): Array of values to select (supports multi-select)
```

#### `mcp__playwright__browser_press_key`
Press keyboard keys.
```
Parameters:
- key (required): Key name (e.g., "ArrowLeft", "Enter") or character (e.g., "a")
```

### File Operations

#### `mcp__playwright__browser_file_upload`
Upload files through file input elements.
```
Parameters:
- paths (required): Array of absolute file paths to upload
```

#### `mcp__playwright__browser_pdf_save`
Save the current page as a PDF document.
```
Parameters:
- filename (optional): Custom filename for PDF (default: page-{timestamp}.pdf)
```

### Tab Management

#### `mcp__playwright__browser_tab_new`
Open a new browser tab.
```
Parameters:
- url (optional): URL to navigate to in new tab
```

#### `mcp__playwright__browser_tab_list`
List all open browser tabs.
```
Parameters: None
```

#### `mcp__playwright__browser_tab_select`
Switch to a specific tab by index.
```
Parameters:
- index (required): Zero-based index of tab to select
```

#### `mcp__playwright__browser_tab_close`
Close a browser tab.
```
Parameters:
- index (optional): Index of tab to close (default: current tab)
```

### Utilities & Advanced Features

#### `mcp__playwright__browser_wait_for`
Wait for specific conditions before proceeding.
```
Parameters:
- text (optional): Wait for text to appear on page
- textGone (optional): Wait for text to disappear from page
- time (optional): Wait for specific time in seconds
```

#### `mcp__playwright__browser_handle_dialog`
Handle browser dialogs (alerts, confirms, prompts).
```
Parameters:
- accept (required): Whether to accept the dialog (true/false)
- promptText (optional): Text to enter in prompt dialogs
```

#### `mcp__playwright__browser_console_messages`
Retrieve all console messages from the browser.
```
Parameters: None
```

#### `mcp__playwright__browser_network_requests`
Get all network requests made since page load.
```
Parameters: None
```

#### `mcp__playwright__browser_install`
Install the browser if not already installed.
```
Parameters: None
```

#### `mcp__playwright__browser_generate_playwright_test`
Generate Playwright test code based on user interactions.
```
Parameters:
- name (required): Name of the test
- description (required): Description of what the test does
- steps (required): Array of test steps
```

## Usage Patterns

### Basic Navigation and Screenshots
```
1. Navigate to URL
2. Take screenshot or snapshot
3. Analyze page content
```

### Element Interaction Workflow
```
1. Take snapshot to identify elements
2. Use element references from snapshot
3. Interact with elements (click, type, etc.)
4. Verify results
```

### File Upload Process
```
1. Navigate to page with file input
2. Use browser_file_upload with absolute file paths
3. Verify upload success
```

### Multi-tab Operations
```
1. Open new tabs as needed
2. Switch between tabs using tab_select
3. Perform operations on each tab
4. Close tabs when done
```

## Best Practices

1. **Always use snapshots first** - Take a snapshot before interacting with elements to get proper element references
2. **Use descriptive element names** - Provide clear, human-readable descriptions for elements
3. **Handle errors gracefully** - Use wait_for to ensure elements are ready before interaction
4. **Clean up resources** - Close tabs and browsers when done
5. **Use absolute paths** - Always provide full paths for file uploads
6. **Test incrementally** - Break complex workflows into smaller steps

## Common Use Cases

- **Web scraping and data extraction**
- **Automated testing of web applications**
- **Screenshot generation for documentation**
- **Form filling and submission**
- **File upload automation**
- **Multi-step user journey automation**
- **Visual regression testing**
- **Accessibility testing with snapshots**

## Integration with Other Tools

Playwright tools work well with:
- File system tools for managing uploads/downloads
- Task tools for complex automation workflows
- Web search tools for finding target URLs
- Read/Write tools for processing extracted data


</TOOL_INSTRUCTIONS>
