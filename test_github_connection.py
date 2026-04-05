#!/usr/bin/env python3
import urllib.request, json, os

api_key = os.environ.get('MATON_API_KEY', 'JfvJasDZxkryUxti4nTuqChJLQyxtSyQoEwjmtdSU3T92j2TyrDW1L1KmCEvvb52MBnAM0TjrCD7fZi2xEDb_9TqkjOfV_3tuy0')

req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {api_key}')
try:
    response = urllib.request.urlopen(req)
    user = json.load(response)
    print(f"✅ Connected to GitHub as: {user['login']}")
    print(f"   Name: {user.get('name', 'N/A')}")
    print(f"   Repos: {user['public_repos']} public, {user['total_private_repos']} private")
except Exception as e:
    print(f"❌ Connection failed: {e}")
