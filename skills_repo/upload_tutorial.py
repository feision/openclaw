#!/usr/bin/env python3
"""
Upload GitHub workflow tutorial to GitHub repository
"""

import urllib.request
import json
import os
import base64
import sys

def github_request(endpoint, method='GET', data=None):
    """Make request directly to GitHub API"""
    url = f"https://api.github.com/{endpoint}"
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {os.environ["GITHUB_TOKEN"]}')
    req.add_header('User-Agent', 'OpenClaw-GitHub-Tutorial')
    if data:
        req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req)
        return json.load(response)
    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        if e.headers.get('Content-Type') == 'application/json':
            try:
                error_body = json.load(e)
                print(f"Error details: {error_body}")
            except:
                pass
        raise
    except Exception as e:
        print(f"Request failed: {e}")
        raise

def check_repository_exists(owner, repo_name):
    """Check if repository already exists"""
    try:
        github_request(f'repos/{owner}/{repo_name}')
        return True
    except urllib.request.HTTPError as e:
        if e.code == 404:
            return False
        else:
            raise

def create_repository(repo_name, description):
    """Create a GitHub repository"""
    repo_data = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": False  # Don't auto-init to avoid duplicate README
    }
    
    result = github_request('user/repos', 'POST', json.dumps(repo_data).encode())
    print(f"Repository created: {result['full_name']}")
    print(f"URL: {result['html_url']}")
    return result

def upload_file(owner, repo, file_path, content, message):
    """Upload a file to GitHub repository"""
    encoded_content = base64.b64encode(content.encode()).decode()
    
    upload_data = {
        "message": message,
        "content": encoded_content,
        "branch": "main"
    }
    
    try:
        result = github_request(f'repos/{owner}/{repo}/contents/{file_path}', 
                              'PUT', json.dumps(upload_data).encode())
        print(f"✓ Uploaded: {file_path}")
        return result
    except urllib.request.HTTPError as e:
        if e.code == 422:
            # Try to update existing file
            print(f"File {file_path} may already exist")
            return None
        else:
            raise

def upload_directory(owner, repo, local_path):
    """Upload all files in a directory"""
    import os
    for filename in os.listdir(local_path):
        file_path = os.path.join(local_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.md') or filename.endswith('.py'):
            with open(file_path, 'r') as f:
                content = f.read()
            
            upload_file(owner, repo, filename, content, f"Add {filename}")

def main():
    """Upload GitHub workflow tutorial to GitHub"""
    
    # Set GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN environment variable is not set")
        print("Please set it before running:")
        print("export GITHUB_TOKEN='your_github_token'")
        return
    
    print(f"Using GitHub token: {token[:10]}...")
    
    # Get user info
    user = github_request('user')
    owner = user["login"]
    print(f"Authenticated as: {owner}")
    
    # Check if repository exists
    repo_name = "openclaw-github-workflow-skills"
    
    if check_repository_exists(owner, repo_name):
        print(f"Repository already exists: {owner}/{repo_name}")
    else:
        # Create repository
        description = "OpenClaw GitHub Workflow Tutorial - Complete guide for AI assistants to use GitHub APIs"
        repo = create_repository(repo_name, description)
        print(f"Created repository: {repo['html_url']}")
    
    # Upload tutorial files
    tutorial_path = "/root/.openclaw/workspace/tutorials/github-workflow"
    
    print("\nUploading tutorial files:")
    upload_directory(owner, repo_name, tutorial_path)
    
    # Upload example scripts
    scripts_path = "/root/.openclaw/workspace/tutorials/github-workflow/example_scripts"
    if os.path.exists(scripts_path):
        for filename in os.listdir(scripts_path):
            file_path = os.path.join(scripts_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                upload_file(owner, repo_name, f"example_scripts/{filename}", content, f"Add example script {filename}")
    
    print("\n=== Upload Complete ===")
    print(f"Repository: https://github.com/{owner}/{repo_name}")
    
    # Add README
    readme_content = """# OpenClaw GitHub Workflow Skills

## Complete Tutorial for Using GitHub APIs with OpenClaw

This repository contains a comprehensive tutorial for AI assistants and developers to use GitHub APIs with OpenClaw.

### Contents

- **README.md** - Complete GitHub workflow guide
- **QUICK_START.md** - 5-minute quick start guide  
- **USER_CASES.md** - Practical use cases and examples
- **SUMMARY.md** - Skills and tools summary
- **AVAILABLE_SKILLS.md** - List of GitHub-related skills in OpenClaw
- **COMPLETE_TUTORIAL.md** - Complete tutorial summary
- **SETUP_GUIDE.md** - Setup and configuration guide
- **example_scripts/** - Example scripts for automation

### Quick Start

1. Install OpenClaw GitHub skills:
```bash
skillhub install github
skillhub install github-api
```

2. Set up authentication:
```bash
export MATON_API_KEY="your_maton_api_key"
export GITHUB_TOKEN="your_github_token"
```

3. Use the automation scripts:
```bash
python3 example_scripts/github_automation.py
```

### Features

- Complete GitHub API integration
- Maton Gateway authentication flow
- Example scripts for automation
- User case studies
- Available skills catalog
- Troubleshooting guides

### Repository Structure

```
├── README.md              # Main documentation
├── QUICK_START.md         # Quick setup guide
├── USER_CASES.md          # Practical examples
├── SUMMARY.md            # Skills summary
├── AVAILABLE_SKILLS.md   # Skill catalog
├── COMPLETE_TUTORIAL.md  # Complete tutorial
├── SETUP_GUIDE.md        # Setup guide
└── example_scripts/
    ├── github_automation.py   # Basic automation
    ├── test_connection.py     # Connection testing
    ├── advanced_automation.py # Advanced automation
```

### Created by

This tutorial was automatically created by OpenClaw AI assistant using GitHub API integration.

### License

MIT License"""
    
    upload_file(owner, repo_name, "README.md", readme_content, "Add repository README")

if __name__ == "__main__":
    main()