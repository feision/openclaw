#!/usr/bin/env python3
"""
OpenClaw GitHub Automation Examples

This script demonstrates various GitHub automation workflows using the Maton Gateway API.

Before running:
1. Set MATON_API_KEY environment variable
2. Complete GitHub OAuth authorization via Maton Ctrl panel
"""

import urllib.request
import json
import os
import base64
import sys

def github_request(url, method='GET', data=None, headers=None):
    """Make authenticated request to GitHub API via Maton Gateway"""
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    if data:
        req.add_header('Content-Type', 'application/json')
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    try:
        response = urllib.request.urlopen(req)
        return json.load(response)
    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        if e.headers.get('Content-Type') == 'application/json':
            error_body = json.load(e)
            print(f"Error details: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

def create_repository(name, description, private=False):
    """Create a new GitHub repository"""
    repo_data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": True
    }
    
    result = github_request('https://gateway.maton.ai/github/user/repos', 'POST', 
                           json.dumps(repo_data).encode())
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
    
    result = github_request(f'https://gateway.maton.ai/github/repos/{owner}/{repo}/contents/{file_path}', 
                          'PUT', json.dumps(upload_data).encode())
    print(f"File uploaded: {file_path}")
    return result

def create_issue(owner, repo, title, body, labels=None, assignees=None):
    """Create a GitHub issue"""
    issue_data = {
        "title": title,
        "body": body
    }
    
    if labels:
        issue_data["labels"] = labels
    if assignees:
        issue_data["assignees"] = assignees
    
    result = github_request(f'https://gateway.maton.ai/github/repos/{owner}/{repo}/issues', 
                          'POST', json.dumps(issue_data).encode())
    print(f"Issue created: #{result['number']}")
    print(f"URL: {result['html_url']}")
    return result

def create_pull_request(owner, repo, title, body, head, base):
    """Create a pull request"""
    pr_data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    
    result = github_request(f'https://gateway.maton.ai/github/repos/{owner}/{repo}/pulls', 
                          'POST', json.dumps(pr_data).encode())
    print(f"Pull request created: #{result['number']}")
    print(f"URL: {result['html_url']}")
    return result

def list_repositories(page=1, per_page=20):
    """List user repositories"""
    result = github_request(f'https://gateway.maton.ai/github/user/repos?page={page}&per_page={per_page}')
    print(f"Found {len(result)} repositories:")
    for repo in result:
        print(f"- {repo['full_name']}: {repo['description']}")
    return result

def get_user_info():
    """Get authenticated user information"""
    result = github_request('https://gateway.maton.ai/github/user')
    print(f"Authenticated as: {result['login']}")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    return result

def main():
    """Main example workflow"""
    
    # 1. Verify authentication
    user = get_user_info()
    
    # 2. List existing repositories
    repositories = list_repositories()
    
    # 3. Create a new repository
    repo = create_repository("openclaw-test-project", "A test project created by OpenClaw automation")
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    
    # 4. Upload files
    upload_file(owner, repo_name, "README.md", "# Test Project\n\nCreated by OpenClaw automation", "Add README")
    upload_file(owner, repo_name, ".gitignore", "*.log\n*.tmp\n*.env\n", "Add .gitignore")
    upload_file(owner, repo_name, "LICENSE", "MIT License\n", "Add LICENSE")
    
    # 5. Create an issue
    issue = create_issue(owner, repo_name, "Test Issue", "This is a test issue created by automation", ["test"])
    
    # 6. Create a pull request example
    print("\nNote: Pull request creation requires an existing branch.")
    print("First create a branch via commits or fork workflows.")
    
    # 7. Display summary
    print("\n=== Summary ===")
    print(f"User: {user['login']}")
    print(f"Repository created: {repo['full_name']}")
    print(f"Issue created: #{issue['number']}")
    
if __name__ == "__main__":
    # Check if API key is set
    api_key = os.environ.get("MATON_API_KEY")
    if not api_key:
        print("ERROR: MATON_API_KEY environment variable is not set")
        print("Please set it before running:")
        print("export MATON_API_KEY='your_api_key'")
        sys.exit(1)
    
    main()