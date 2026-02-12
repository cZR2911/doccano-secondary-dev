import requests
import json
import os
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "password"
PROJECT_NAME = "SmokeTest_Project"
TEST_FILE = "smoke_test_data.csv"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(message, status="INFO"):
    if status == "PASS":
        print(f"{GREEN}[PASS] {message}{RESET}")
    elif status == "FAIL":
        print(f"{RED}[FAIL] {message}{RESET}")
    else:
        print(f"[INFO] {message}")

def create_test_file():
    content = "text,label_positive,label_negative,label_neutral\nThis is a good movie,1,0,0\nThis is bad,0,1,0"
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Created test file: {TEST_FILE}")

def run_test():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    # 1. Login
    try:
        response = session.post(f"{BASE_URL}/v1/auth/login/", json={"username": USERNAME, "password": PASSWORD})
        if response.status_code == 200:
            log("Login successful", "PASS")
            # In some versions, token is in response, or cookie is set. Doccano uses session auth or token.
            # If API returns token (DRF Token/JWT), use it.
            if "key" in response.json():
                 session.headers.update({"Authorization": f"Token {response.json()['key']}"})
            
            # Handle CSRF
            if 'csrftoken' in session.cookies:
                session.headers.update({'X-CSRFToken': session.cookies['csrftoken']})
            else:
                # Sometimes it's in a specific cookie name or needs to be fetched
                pass
        else:
            log(f"Login failed: {response.text}", "FAIL")
            return
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return

    # 2. Cleanup existing project if exists
    resp = session.get(f"{BASE_URL}/v1/projects")
    if resp.status_code != 200:
        log(f"Get projects failed: {resp.status_code} {resp.text[:200]}", "FAIL")
        return
    try:
        projects = resp.json()
    except json.JSONDecodeError:
        log(f"Get projects returned non-JSON: {resp.text[:200]}", "FAIL")
        return
    # Handle pagination
    if isinstance(projects, dict) and 'results' in projects:
        project_list = projects['results']
    else:
        project_list = projects

    for p in project_list:
        if p['name'] == PROJECT_NAME:
            session.delete(f"{BASE_URL}/v1/projects/{p['id']}")
            log(f"Cleaned up existing project: {p['name']}")

    # 3. Create Project (Sequence Labeling)
    payload = {
        "name": PROJECT_NAME,
        "description": "Automated smoke test project",
        "project_type": "SequenceLabeling",
        "resourcetype": "SequenceLabelingProject"
    }
    response = session.post(f"{BASE_URL}/v1/projects", json=payload)
    if response.status_code == 201:
        project_id = response.json()['id']
        log(f"Project created (ID: {project_id})", "PASS")
    else:
        # Try to extract title
        import re
        title = "Unknown Error"
        match = re.search(r'<title>(.*?)</title>', response.text, re.DOTALL)
        if match:
            title = match.group(1).strip()
        log(f"Project creation failed: {response.status_code} {title}", "FAIL")
        return

    # 4. Import Data
    # We need to simulate the file upload.
    # The API endpoint is usually /v1/projects/{id}/upload
    # Params: file, format, column_data (text_column), column_label (label_column)
    # Based on user requirement: "Default first row columns as labels"
    
    # Wait a bit for project to be ready (if async)
    time.sleep(1)

    # 4.1 Upload to FilePond
    upload_id = None
    with open(TEST_FILE, "rb") as f:
        files = {'filepond': f} # FilePond expects 'filepond' key usually? Or 'file'? DRF-FilePond uses 'filepond' by default configuration often.
        # Let's check DRF FilePond docs or settings. Usually 'filepond'.
        # But if not configured, maybe 'file'.
        # Let's try 'filepond' first.
        # FilePond response is text/plain usually, so we need to accept that
        headers = {"Accept": "*/*", "X-CSRFToken": session.cookies.get('csrftoken', '')}
        if "Authorization" in session.headers:
            headers["Authorization"] = session.headers["Authorization"]
            
        fp_resp = session.post(f"{BASE_URL}/v1/fp/process/", files=files, headers=headers)
        if fp_resp.status_code == 200:
            upload_id = fp_resp.text.strip()
            log(f"FilePond upload success: {upload_id}", "PASS")
        else:
            log(f"FilePond upload failed: {fp_resp.status_code} {fp_resp.text[:200]}", "FAIL")
            # Try with 'file' key if 'filepond' fails?
            # return
            
    if not upload_id:
        return

    # 4.2 Import Data
    data = {
        'uploadIds': [upload_id],
        'format': 'CSV',
        'task': 'SequenceLabeling',
        'column_data': 'text', 
        'column_label': 'label_positive,label_negative,label_neutral', 
    }
    
    # Note: request.data in DRF handles JSON. So we send JSON.
    response = session.post(f"{BASE_URL}/v1/projects/{project_id}/upload", json=data)

    # If upload is async (Celery), it returns task_id
    if response.status_code in [200, 201, 202]:
        task_id = response.json().get('task_id')
        log(f"Import started (Task ID: {task_id})", "PASS")
        
        # Poll for completion
        if task_id:
            for _ in range(10):
                time.sleep(2)
                # Check task status if there's an endpoint, or just check project data
                # Assuming we just wait for now
                pass
    else:
            # Try to extract title
            import re
            title = "Unknown Error"
            match = re.search(r'<title>(.*?)</title>', response.text, re.DOTALL)
            if match:
                title = match.group(1).strip()
            else:
                title = response.text[:500]
            log(f"Import failed: {response.status_code} {title}", "FAIL")
            return

    # Wait for Celery to process
    log("Waiting for background processing...")
    time.sleep(5)

    # 5. Verify Label Types (Should match headers)
    # For SequenceLabeling, the endpoint is likely span-types
    endpoint = "span-types" if payload['project_type'] == "SequenceLabeling" else "category-types"
    
    response = session.get(f"{BASE_URL}/v1/projects/{project_id}/{endpoint}")
    
    try:
        labels = response.json()
    except Exception as e:
        log(f"Get labels failed (JSON error): {response.status_code} {response.text[:200]}", "FAIL")
        return
        
    # Pagination
    if isinstance(labels, dict) and 'results' in labels:
        labels = labels['results']
    
    label_names = sorted([l['text'] for l in labels])
    expected_labels = sorted(['label_positive', 'label_negative', 'label_neutral'])
    
    if label_names == expected_labels:
        log(f"Label Types verification: {label_names}", "PASS")
    else:
        log(f"Label Types mismatch. Expected {expected_labels}, got {label_names}", "FAIL")

    # 6. Verify Examples (Should have no annotations)
    response = session.get(f"{BASE_URL}/v1/projects/{project_id}/examples")
    examples = response.json()
    if isinstance(examples, dict) and 'results' in examples:
        examples = examples['results']
    
    if len(examples) == 2:
        log(f"Example count verification: {len(examples)}", "PASS")
    else:
        log(f"Example count mismatch: {len(examples)}", "FAIL")

    # Check annotations
    has_annotations = False
    for ex in examples:
        # Fetch details to get annotations if not in list
        detail = session.get(f"{BASE_URL}/v1/projects/{project_id}/examples/{ex['id']}").json()
        if detail.get('annotations') or detail.get('entities'): # SequenceLabeling uses 'entities' usually? No, API usually 'annotations' or type specific
            # Let's check generic 'annotations' or specific list
            # For SequenceLabeling, it might be at /examples/{id}/spans or similar, but detail view usually has it.
            # If 'annotations' key exists and is not empty.
            if detail.get('annotations'): 
                has_annotations = True
                log(f"Example {ex['id']} has annotations: {detail['annotations']}", "FAIL")
                break
    
    if not has_annotations:
        log("No auto-annotations verification", "PASS")

    # 7. Cleanup
    session.delete(f"{BASE_URL}/v1/projects/{project_id}")
    log("Cleanup: Project deleted")

if __name__ == "__main__":
    create_test_file()
    run_test()
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
