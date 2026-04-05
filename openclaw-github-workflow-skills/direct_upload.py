#!/usr/bin/env python3
"""
Direct GitHub API upload without Maton Gateway
"""

import urllib.request
import json
import os
import base64

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
            error_body = json.load(e)
            print(f"Error details: {error_body}")
        raise

def create_repository(repo_name, description):
    """Create a GitHub repository"""
    repo_data = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": True
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
    
    result = github_request(f'repos/{owner}/{repo}/contents/{file_path}', 
                          'PUT', json.dumps(upload_data).encode())
    print(f"File uploaded: {file_path}")
    return result

def upload_directory(owner, repo, local_path):
    """Upload all files in a directory"""
    import os
    for filename in os.listdir(local_path):
        file_path = os.path.join(local_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            upload_file(owner, repo, filename, content, f"Add {filename}")
            print(f"Uploaded {filename}")

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
    print(f"Authenticated as: {user['login']}")
    
    # Create repository
    repo_name = "openclaw-github-workflow-skills"
    description = "OpenClaw GitHub Workflow Tutorial - Complete guide for AI assistants to use GitHub APIs"
    
    repo = create_repository(repo_name, description)
    owner = repo["owner"]["login"]
    
    # Upload tutorial files
    tutorial_path = "/root/.openclaw/workspace/tutorials/github-workflow"
    
    print("\nUploading tutorial files:")
    upload_directory(owner, repo_name, tutorial_path)
    
    # Upload example scripts
    scripts_path = "/root/.openclaw/workspace/tutorials/github-workflow/example_scripts"
    for filename in os.listdir(scripts_path):
        file_path = os.path.join(scripts_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            upload_file(owner2, repo_name, f"example_scripts/{filename}", content, f"Add example script {filename}")
    
    print("\n=== Upload Complete ===")
    print(f"Repository: {repo['html_url']}")
    print(f"Tutorial files uploaded successfully!")
    
    # Add README info
    readme_content = """# OpenClaw GitHub Workflow Skills

This repository contains a comprehensive tutorial for using GitHub APIs with OpenClaw.

## Contents

1. **README.md** - Complete GitHub workflow guide
2. **QUICK_START.md** - 5-minute quick start guide  
3. **USER_CASES.md** - Practical use cases and examples
4. **SUMMARY.md** - Skills and tools summary
5. **AVAILABLE_SKILLS.md** - List of GitHub-related skills in OpenClaw
6. **COMPLETE_TUTORIAL.md** - Complete tutorial summary
7. **SETUP_GUIDE.md** - Setup and configuration guide
8. **example_scripts/** - Example scripts for automation

## How to Use

1. Set GitHub token: `export GITHUB_TOKEN="your_token"`
2. Follow the setup guide in SETUP_GUIDE.md
3. Use the example scripts for automation
4. Explore available skills in OpenClaw

## Skills Included

The tutorial covers:
- github-api (already installed in OpenClaw)
- Other GitHub-related skills available in skillhub/clawhub
- Direct GitHub API integration
- Maton Gateway integration (if configured)

## Created by OpenClaw Assistant

This tutorial was automatically created by OpenClaw AI assistant."""
    
    upload_file(owner, repo_name, "README.md", readme_content, "Add repository README")

if __name__ == "__main__":
    main()