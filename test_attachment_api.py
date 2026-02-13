import requests
import os
import sys

# Setup
base_url = "http://127.0.0.1:8000"
username = "admin"
password = "password"

print("Starting test...", flush=True)

try:
    # Login
    session = requests.Session()
    print(f"Logging in to {base_url}...", flush=True)
    response = session.post(f"{base_url}/v1/auth/login/", json={"username": username, "password": password})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}", flush=True)
        sys.exit(1)
    print("Login successful", flush=True)

    # Get Project ID
    response = session.get(f"{base_url}/v1/projects")
    if response.status_code != 200:
        print(f"Get projects failed: {response.text}", flush=True)
        sys.exit(1)
    
    # Get CSRF Token
    csrf_token = session.cookies.get('csrftoken')
    if csrf_token:
        session.headers.update({'X-CSRFToken': csrf_token})
    else:
        print("Warning: CSRF token not found in cookies", flush=True)

    projects_data = response.json()
    
    if isinstance(projects_data, dict) and "results" in projects_data:
        projects = projects_data["results"]
    elif isinstance(projects_data, list):
        projects = projects_data
    else:
        print(f"Unexpected projects format: {projects_data}", flush=True)
        sys.exit(1)

    if not projects:
        print("No projects found. Please create one first.", flush=True)
        sys.exit(1)
    project_id = projects[0]["id"]
    print(f"Using Project ID: {project_id}", flush=True)

    # 1. Upload Attachment
    print("Uploading attachment...", flush=True)
    with open("test_attachment.txt", "w") as f:
        f.write("This is a test attachment content.")

    with open("test_attachment.txt", 'rb') as f_upload:
        files = {'file': f_upload}
        response = session.post(f"{base_url}/v1/projects/{project_id}/attachments", files=files)
    
    if response.status_code != 201:
        print(f"Upload failed: {response.status_code} {response.text}", flush=True)
    else:
        print("Upload successful", flush=True)
        attachment = response.json()
        attachment_id = attachment["id"]
        print(f"Attachment ID: {attachment_id}", flush=True)

        # 2. List Attachments
        print("Listing attachments...", flush=True)
        response = session.get(f"{base_url}/v1/projects/{project_id}/attachments")
        if response.status_code != 200:
            print(f"List failed: {response.text}", flush=True)
        else:
            attachments = response.json()
            print(f"Attachments: {len(attachments)}", flush=True)
            print(attachments, flush=True)

        # 3. Delete Attachment
        print(f"Deleting attachment {attachment_id}...", flush=True)
        response = session.delete(f"{base_url}/v1/projects/{project_id}/attachments/{attachment_id}")
        if response.status_code != 204:
            print(f"Delete failed: {response.text}", flush=True)
        else:
            print("Delete successful", flush=True)

except Exception as e:
    print(f"An error occurred: {e}", flush=True)
    sys.exit(1)

finally:
    # Cleanup
    if os.path.exists("test_attachment.txt"):
        os.remove("test_attachment.txt")
