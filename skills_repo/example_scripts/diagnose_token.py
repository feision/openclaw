#!/usr/bin/env python3
"""
GitHub Token Diagnostic Tool

Diagnose GitHub Token and Maton Gateway issues
"""

import urllib.request
import json
import os
import sys

def test_github_token(token):
    """Test GitHub Token"""
    print("Testing GitHub Token...")
    
    req = urllib.request.Request('https://api.github.com/user')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'OpenClaw-Diagnosis')
    
    try:
        response = urllib.request.urlopen(req)
        user = json.load(response)
        print(f"✓ GitHub Token is valid")
        print(f"Authenticated as: {user['login']}")
        print(f"Name: {user.get('name', 'Not set')}")
        return True
    except Exception as e:
        print(f"✗ GitHub Token is invalid: {e}")
        return False

def test_maton_api_key(api_key):
    """Test Maton API Key"""
    print("\nTesting Maton API Key...")
    
    req = urllib.request.Request('https://ctrl.maton.ai/connections')
    req.add_header('Authorization', f'Bearer {api_key}')
    
    try:
        response = urllib.request.urlopen(req)
        connections = json.load(response)
        print(f"✓ Maton API Key is valid")
        print(f"Found {len(connections)} connections")
        
        github_connections = [c for c in connections if c.get('app') == 'github']
        if github_connections:
            print(f"✓ GitHub connection found:")
            for conn in github_connections:
                print(f"  - ID: {conn['connection_id']}")
                print(f"    Status: {conn['status']}")
                if conn['status'] == 'ACTIVE':
                    return True
        else:
            print(f"✗ No GitHub connections found")
            return False
    except Exception as e:
        print(f"✗ Maton API Key is invalid: {e}")
        return False

def create_maton_github_connection(api_key):
    """Create GitHub connection in Maton"""
    print("\nCreating GitHub connection in Maton...")
    
    data = json.dumps({'app': 'github'}).encode()
    req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {api_key}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req)
        result = json.load(response)
        print(f"✓ Connection created")
        print(f"Connection ID: {result['connection']['connection_id']}")
        print(f"Status: {result['connection']['status']}")
        print(f"Authorization URL: {result['connection']['url']}")
        print("\nPlease open this URL in a browser to authorize GitHub:")
        print(result['connection']['url'])
        return result['connection']
    except Exception as e:
        print(f"✗ Connection creation failed: {e}")
        return None

def test_github_api_access(token):
    """Test GitHub API access"""
    print("\nTesting GitHub API access...")
    
    # Test repository creation
    repo_data = {
        "name": "test-repo-diagnostic",
        "description": "Diagnostic test repository",
        "private": False,
        "auto_init": False
    }
    
    data = json.dumps(repo_data).encode()
    req = urllib.request.Request('https://api.github.com/user/repos', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'OpenClaw-Diagnosis')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req)
        repo = json.load(response)
        print(f"✓ GitHub repository creation successful")
        print(f"Repository: {repo['full_name']}")
        print(f"Permissions: OK")
        
        # Delete test repository
        delete_req = urllib.request.Request(f'https://api.github.com/repos/{repo["full_name"]}', method='DELETE')
        delete_req.add_header('Authorization', f'Bearer {token}')
        delete_req.add_header('User-Agent', 'OpenClaw-Diagnosis')
        urllib.request.urlopen(delete_req)
        print(f"✓ Test repository deleted")
        
        return True
    except Exception as e:
        print(f"✗ GitHub API access failed: {e}")
        if e.code == 403:
            print("Token may lack 'repo' permission")
        return False

def test_maton_gateway_access(api_key):
    """Test Maton Gateway access"""
    print("\nTesting Maton Gateway access...")
    
    req = urllib.request.Request('https://gateway.maton.ai/github/user')
    req.add_header('Authorization', f'Bearer {api_key}')
    
    try:
        response = urllib.request.urlopen(req)
        user = json.load(response)
        print(f"✓ Maton Gateway access successful")
        print(f"Authenticated as: {user['login']}")
        return True
    except Exception as e:
        print(f"✗ Maton Gateway access failed: {e}")
        return False

def diagnose_all():
    """Diagnose all authentication methods"""
    github_token = os.environ.get("GITHUB_TOKEN")
    maton_key = os.environ.get("MATON_API_KEY")
    
    print("=== GitHub Authentication Diagnosis ===")
    
    if github_token:
        print(f"GitHub Token found: {github_token[:10]}...")
        
        # Test GitHub Token
        gh_valid = test_github_token(github_token)
        
        if gh_valid:
            gh_access = test_github_api_access(github_token)
        else:
            gh_access = False
        
        print(f"GitHub Token status: {(gh_valid and gh_access)}")
    else:
        print("✗ GitHub Token not found (GITHUB_TOKEN environment variable)")
    
    if maton_key:
        print(f"\nMaton API Key found: {maton_key[:10]}...")
        
        # Test Maton API Key
        maton_valid = test_maton_api_key(maton_key)
        
        if maton_valid:
            maton_gateway = test_maton_gateway_access(maton_key)
        else:
            # Try to create connection
            connection = create_maton_github_connection(maton_key)
            if connection:
                maton_gateway = False  # Still need to authorize
            else:
                maton_gateway = False
        
        print(f"Maton Gateway status: {(maton_valid and maton_gateway)}")
    else:
        print("✗ Maton API Key not found (MATON_API_KEY environment variable)")
    
    print("\n=== Diagnosis Summary ===")
    
    if github_token and gh_valid and gh_access:
        print("✓ GitHub Token authentication working")
        print("Recommended: Use GitHub Token directly")
        print("Example: https://api.github.com/user")
    
    if maton_key and maton_valid and maton_gateway:
        print("✓ Maton Gateway authentication working")
        print("Recommended: Use Maton Gateway")
        print("Example: https://gateway.maton.ai/github/user")
    
    if not github_token and not maton_key:
        print("✗ No authentication methods available")
        print("Solution:")
        print("1. Set GITHUB_TOKEN environment variable")
        print("2. Set MATON_API_KEY environment variable")
    
    print("\n=== Next Steps ===")
    print("1. Update environment variables if needed")
    print("2. Run connection tests")
    print("3. Try example scripts")

def main():
    """Main diagnostic routine"""
    print("GitHub Token Diagnostic Tool")
    print("Diagnosing GitHub Token and Maton Gateway issues")
    
    # Check environment variables
    github_token = os.environ.get("GITHUB_TOKEN")
    maton_key = os.environ.get("MATON_API_KEY")
    
    if not github_token and not maton_key:
        print("ERROR: No authentication tokens found")
        print("Set environment variables:")
        print("export GITHUB_TOKEN='your_github_token'")
        print("export MATON_API_KEY='your_maton_api_key'")
        return
    
    diagnose_all()

if __name__ == "__main__":
    main()