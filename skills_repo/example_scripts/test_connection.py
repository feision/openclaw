#!/usr/bin/env python3
"""
Test GitHub connection through Maton Gateway

This script helps troubleshoot GitHub API connections
"""

import urllib.request
import json
import os
import sys

def test_api_key():
    """Test if API key is valid"""
    print("Testing API key...")
    
    req = urllib.request.Request('https://ctrl.maton.ai/connections')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    
    try:
        response = urllib.request.urlopen(req)
        connections = json.load(response)
        print(f"✓ API key is valid")
        print(f"Found {len(connections)} connections")
        
        # Check for GitHub connections
        github_connections = [c for c in connections if c.get('app') == 'github']
        if github_connections:
            print(f"✓ Found GitHub connections")
            for conn in github_connections:
                print(f"  - Connection ID: {conn['connection_id']}")
                print(f"    Status: {conn['status']}")
        else:
            print("✗ No GitHub connections found")
            print("Create a GitHub connection first:")
            print("https://ctrl.maton.ai/connections?app=github")
        
        return True
    except Exception as e:
        print(f"✗ API key test failed: {e}")
        return False

def test_github_connection():
    """Test GitHub API connection"""
    print("\nTesting GitHub connection...")
    
    req = urllib.request.Request('https://gateway.maton.ai/github/user')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    
    try:
        response = urllib.request.urlopen(req)
        user_info = json.load(response)
        print(f"✓ GitHub connection successful")
        print(f"Authenticated as: {user_info['login']}")
        print(f"Name: {user_info.get('name', 'Unknown')}")
        print(f"Email: {user_info.get('email', 'Unknown')}")
        return True
    except Exception as e:
        print(f"✗ GitHub connection failed: {e}")
        return False

def create_github_connection():
    """Create a new GitHub connection"""
    print("\nCreating GitHub connection...")
    
    data = json.dumps({'app': 'github'}).encode()
    req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req)
        result = json.load(response)
        
        print(f"✓ Connection created")
        print(f"Connection ID: {result['connection']['connection_id']}")
        print(f"Status: {result['connection']['status']}")
        print(f"URL for OAuth: {result['connection']['url']}")
        
        print("\nPlease open this URL in a browser to complete GitHub authorization:")
        print(result['connection']['url'])
        
        return result['connection']
    except Exception as e:
        print(f"✗ Connection creation failed: {e}")
        return None

def test_rate_limit():
    """Check GitHub API rate limits"""
    print("\nChecking rate limits...")
    
    req = urllib.request.Request('https://gateway.maton.ai/github/rate_limit')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    
    try:
        response = urllib.request.urlopen(req)
        rate_info = json.load(response)
        
        core = rate_info['resources']['core']
        print(f"✓ Rate limit info:")
        print(f"  Core API:")
        print(f"    Limit: {core['limit']}")
        print(f"    Remaining: {core['remaining']}")
        print(f"    Reset time: {core['reset']}")
        
        search = rate_info['resources'].get('search', {'limit': 30, 'remaining': 30})
        print(f"  Search API:")
        print(f"    Limit: {search['limit']}")
        print(f"    Remaining: {search['remaining']}")
        
        return True
    except Exception as e:
        print(f"✗ Rate limit check failed: {e}")
        return False

def main():
    """Main troubleshooting routine"""
    api_key = os.environ.get("MATON_API_KEY")
    
    if not api_key:
        print("ERROR: MATON_API_KEY environment variable is not set")
        print("Please set it before running:")
        print("export MATON_API_KEY='your_api_key'")
        return
    
    print(f"Using API key: {api_key[:10]}...")
    
    # Test API key
    api_key_valid = test_api_key()
    
    if not api_key_valid:
        print("\nAPI key is invalid. Please check:")
        print("1. Get API key from https://maton.ai/settings")
        print("2. Set MATON_API_KEY environment variable")
        return
    
    # Test GitHub connection
    github_valid = test_github_connection()
    
    if not github_valid:
        print("\nNo GitHub connection found.")
        connection = create_github_connection()
        
        if connection:
            print("\nAfter completing OAuth authorization, run this test again.")
        return
    
    # Test rate limits
    test_rate_limit()
    
    print("\n=== Summary ===")
    print("✓ API key valid")
    print("✓ GitHub connection established")
    print("✓ Rate limits checked")
    print("\nEverything is working correctly!")
    
    # Additional tests
    print("\nAdditional tests:")
    
    # List repositories
    try:
        req = urllib.request.Request('https://gateway.maton.ai/github/user/repos?per_page=5')
        req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
        repos = json.load(urllib.request.urlopen(req))
        print(f"✓ Can list repositories: {len(repos)} found")
    except Exception as e:
        print(f"✗ Repository listing failed: {e}")
    
    # Check permissions
    print("\nTo verify permissions, try creating a test repository:")
    print("python3 <<'EOF'")
    print("import urllib.request, json, os")
    print("data = json.dumps({'name': 'test-repo', 'description': 'Test', 'private': False}).encode()")
    print("req = urllib.request.Request('https://gateway.maton.ai/github/user/repos', data=data, method='POST')")
    print("req.add_header('Authorization', f'Bearer {os.environ[\"MATON_API_KEY\"]}')")
    print("req.add_header('Content-Type', 'application/json')")
    print("response = urllib.request.urlopen(req)")
    print("print(json.dumps(json.load(response), indent=2))")
    print("EOF")

if __name__ == "__main__":
    main()