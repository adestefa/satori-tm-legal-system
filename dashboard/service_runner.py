# dashboard/service_runner.py
import subprocess
import os
import asyncio
import threading
import time
from datetime import datetime

# Get the absolute path of the project root by going up two directories
# from this file's location (dashboard/service_runner.py -> dashboard/ -> TM/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

TIGER_SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'tiger', 'run.sh')
MONKEY_SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'monkey', 'run.sh')

def write_manifest_entry(case_path: str, filename: str, status: str, start_time: str = None, 
                        end_time: str = None, file_size: int = None, processing_time: int = None, 
                        error_message: str = None):
    """
    Write a processing entry to the manifest file.
    Format: filename|status|start_time|end_time|file_size|processing_time_ms|error_message
    """
    manifest_path = os.path.join(case_path, 'processing_manifest.txt')
    
    # Convert None values to 'null' for consistency
    def format_value(value):
        return 'null' if value is None else str(value)
    
    entry = f"{filename}|{status}|{format_value(start_time)}|{format_value(end_time)}|{format_value(file_size)}|{format_value(processing_time)}|{format_value(error_message)}\n"
    
    print(f"📝 MANIFEST: Writing entry - {filename}: {status}")
    
    try:
        with open(manifest_path, 'a') as f:
            f.write(entry)
    except Exception as e:
        print(f"❌ MANIFEST: Error writing entry: {e}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes, return 0 if file doesn't exist"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def clear_manifest(case_path: str):
    """Clear the manifest file at the start of processing"""
    manifest_path = os.path.join(case_path, 'processing_manifest.txt')
    try:
        if os.path.exists(manifest_path):
            os.remove(manifest_path)
            print(f"📝 MANIFEST: Cleared existing manifest")
    except Exception as e:
        print(f"❌ MANIFEST: Error clearing manifest: {e}")

def _broadcast_file_event(data_manager, case_id: str, event_type: str, file_name: str, error: str = None):
    """Helper function to broadcast file processing events via WebSocket"""
    try:
        # Import here to avoid circular imports
        from .main import connection_manager
        
        event_data = {
            'type': event_type,
            'case_id': case_id,
            'file_name': file_name,
            'timestamp': os.path.getmtime(os.path.join(PROJECT_ROOT, 'test-data', 'sync-test-cases', case_id, file_name)) if os.path.exists(os.path.join(PROJECT_ROOT, 'test-data', 'sync-test-cases', case_id, file_name)) else None
        }
        
        if error:
            event_data['error'] = error
        
        # Broadcast in a separate thread to avoid blocking
        def broadcast_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(connection_manager.broadcast_event(event_data))
                loop.close()
            except Exception as e:
                print(f"Failed to broadcast file event: {e}")
        
        thread = threading.Thread(target=broadcast_in_thread)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"Error broadcasting file event: {e}")

def run_tiger_extraction(case_path: str, output_dir: str, data_manager=None, case_id: str = None) -> str:
    """
    Runs the Tiger service's hydrated-json command with manifest-based file processing tracking.
    Returns the path to the generated JSON file.
    Writes processing progress to processing_manifest.txt in the case directory.
    """
    if not os.path.exists(TIGER_SCRIPT_PATH):
        raise FileNotFoundError(f"Tiger script not found at: {TIGER_SCRIPT_PATH}")

    # Clear any existing manifest
    clear_manifest(case_path)

    # Get list of files to process and write initial manifest entries
    files_to_process = []
    if os.path.exists(case_path):
        for file in os.listdir(case_path):
            if file.endswith(('.pdf', '.docx', '.txt')) and not file.startswith('.'):
                files_to_process.append(file)
    
    # Write initial processing entries with timestamps and file sizes
    start_time = datetime.now().isoformat()
    for file_name in files_to_process:
        file_path = os.path.join(case_path, file_name)
        file_size = get_file_size(file_path)
        write_manifest_entry(case_path, file_name, 'processing', start_time, 
                           file_size=file_size)

    # Record overall processing start time
    overall_start_time = time.time()

    command = [
        TIGER_SCRIPT_PATH,
        'hydrated-json',
        case_path,
        '-o',
        output_dir
    ]
    
    print(f"🐅 TIGER: Running command: {' '.join(command)}")
    
    result = subprocess.run(command, capture_output=True, text=True)

    # Calculate overall processing time
    overall_processing_time = int((time.time() - overall_start_time) * 1000)  # Convert to ms
    end_time = datetime.now().isoformat()

    if result.returncode != 0:
        print("🐅 TIGER: Error running Tiger:")
        print(result.stderr)
        
        # Write error entries for all files
        for file_name in files_to_process:
            write_manifest_entry(case_path, file_name, 'error', start_time, end_time,
                               processing_time=overall_processing_time, 
                               error_message=str(result.stderr))
        
        raise Exception(f"Tiger service failed with exit code {result.returncode}")

    print("🐅 TIGER: Tiger service ran successfully.")
    print(result.stdout)

    # Write success entries for all files
    for file_name in files_to_process:
        file_path = os.path.join(case_path, file_name)
        file_size = get_file_size(file_path)
        write_manifest_entry(case_path, file_name, 'success', start_time, end_time,
                           file_size=file_size, processing_time=overall_processing_time)

    # Write the overall case status to the manifest
    write_manifest_entry(case_path, 'CASE_STATUS', 'PENDING_REVIEW')

    # Find the generated JSON file in the output directory
    for file in os.listdir(output_dir):
        if file.endswith('.json'):
            return os.path.join(output_dir, file)
            
    raise FileNotFoundError("Could not find the generated JSON file from Tiger.")

def run_monkey_generation(json_path: str, output_dir: str, data_manager=None, case_id: str = None) -> str:
    """
    Runs the Monkey service's build-complaint command.
    Returns the path to the generated complaint HTML file.
    """
    if not os.path.exists(MONKEY_SCRIPT_PATH):
        raise FileNotFoundError(f"Monkey script not found at: {MONKEY_SCRIPT_PATH}")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Input JSON file not found at: {json_path}")

    # Define a predictable output path for the complaint
    complaint_filename = f"complaint_{case_id}.html"
    complaint_output_path = os.path.join(output_dir, complaint_filename)

    # Run the Monkey service with PDF generation
    cmd = [MONKEY_SCRIPT_PATH, 'build-complaint', json_path, '-o', complaint_output_path, '--with-pdf']
    
    print(f"Running command: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(MONKEY_SCRIPT_PATH)
    )

    if result.returncode != 0:
        raise RuntimeError(f"Monkey service failed: {result.stderr}")

    print(result.stdout)

    # Write the final case status to the manifest
    case_path = os.path.join(PROJECT_ROOT, 'test-data', 'sync-test-cases', case_id)
    write_manifest_entry(case_path, 'CASE_STATUS', 'COMPLETE')

    if os.path.exists(complaint_output_path):
        return complaint_output_path
            
    raise FileNotFoundError("Could not find the generated complaint file from Monkey.")

def run_summons_generation(json_path: str, output_dir: str, data_manager=None, case_id: str = None) -> list:
    """
    Runs the Monkey service's summons generation.
    Returns a list of paths to the generated summons HTML files.
    """
    if not os.path.exists(MONKEY_SCRIPT_PATH):
        raise FileNotFoundError(f"Monkey script not found at: {MONKEY_SCRIPT_PATH}")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Input JSON file not found at: {json_path}")

    # Create summons output directory
    summons_output_dir = os.path.join(output_dir, "summons")
    os.makedirs(summons_output_dir, exist_ok=True)

    # Run the Monkey service for summons generation
    cmd = [MONKEY_SCRIPT_PATH, 'generate-summons', json_path, '-o', summons_output_dir]
    
    print(f"Running summons command: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(MONKEY_SCRIPT_PATH)
    )

    if result.returncode != 0:
        raise RuntimeError(f"Monkey summons generation failed: {result.stderr}")

    print(result.stdout)

    # Find generated summons files
    if os.path.exists(summons_output_dir):
        summons_files = [os.path.join(summons_output_dir, f) 
                        for f in os.listdir(summons_output_dir) 
                        if f.endswith('.html')]
        
        if summons_files:
            print(f"Generated {len(summons_files)} summons files: {[os.path.basename(f) for f in summons_files]}")
            return summons_files
            
    raise FileNotFoundError("Could not find any generated summons files from Monkey.")
