#!/usr/bin/env python3
"""
Advanced GitHub Automation Examples

More complex workflows for AI assistants and automation systems
"""

import urllib.request
import json
import os
import base64
import sys
import time

class GitHubAutomator:
    """Advanced GitHub automation class"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://gateway.maton.ai/github'
    
    def request(self, endpoint, method='GET', data=None):
        """Make authenticated GitHub request"""
        url = f"{self.base_url}/{endpoint}"
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Authorization', f'Bearer {self.api_key}')
        if data:
            req.add_header('Content-Type', 'application/json')
        
        try:
            response = urllib.request.urlopen(req)
            return json.load(response)
        except urllib.request.HTTPError as e:
            print(f"HTTP Error ({endpoint}): {e.code} - {e.reason}")
            raise
    
    def project_bootstrap(self, project_name, project_files):
        """Bootstrap a complete project with files"""
        print(f"Bootstrapping project: {project_name}")
        
        # Create repository
        repo_data = {
            "name": project_name,
            "description": f"{project_name} - automated project",
            "private": False,
            "auto_init": True
        }
        
        repo = self.request('user/repos', 'POST', json.dumps(repo_data).encode())
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        
        print(f"Repository created: {repo['full_name']}")
        
        # Upload project files
        for file_path, content in project_files.items():
            encoded_content = base64.b64encode(content.encode()).decode()
            upload_data = {
                "message": f"Add {file_path}",
                "content": encoded_content,
                "branch": "main"
            }
            
            self.request(f'repos/{owner}/{repo_name}/contents/{file_path}', 
                        'PUT', json.dumps(upload_data).encode())
            print(f"Uploaded: {file_path}")
        
        # Create initial issues
        initial_issues = [
            {
                "title": "Initial setup complete",
                "body": f"The {project_name} project has been bootstrapped with all required files.",
                "labels": ["setup", "documentation"]
            },
            {
2                "title": "Add project documentation",
                "body": "Complete the project documentation and README.",
                "labels": ["documentation"]
            }
        ]
        
        for issue_data in initial_issues:
            self.request(f'repos/{owner}/{repo_name}/issues', 
                        'POST', json.dumps(issue_data).encode())
        
        print(f"Created {len(initial_issues)} initial issues")
        
        return repo
    
    def sync_file_between_repos(self, source_repo, dest_repo, file_path):
        """Sync a file between two repositories"""
        source_owner, source_name = source_repo.split('/')
        dest_owner, dest_name = dest_repo.split('/')
        
        print(f"Syncing {file_path} from {source_repo} to {dest_repo}")
        
        # Get source file
        source_file = self.request(f'repos/{source_owner}/{source_name}/contents/{file_path}')
        
        # Upload to destination
        upload_data = {
            "message": f"Sync from {source_repo}",
            "content": source_file["content"],
            "branch2": "main"
        }
        
        result = self.request(f'repos/{dest_owner}/{dest_name}/contents/{file_path}', 
                             'PUT', json.dumps(upload_data).encode())
        
        print(f"Sync complete: {file_path}")
        return result
    
    def automated_pr_review(self, owner, repo, pr_number):
        """Automated PR review with AI analysis"""
        print(f"Reviewing PR #{pr_number}")
        
        # Get PR details
        pr = self.request(f'repos/{owner}/{repo}/pulls/{pr_number}')
        
        # Get PR files
        files = self.request(f'repos/{owner}/{repo}/pulls/{pr_number}/files')
        
        # AI analysis simulation
        review_text = self.ai_analysis(files, pr)
        
        # Post review comment
        comment_data = {
            "body": review_text,
            "event": "COMMENT"
        }
        
        review = self.request(f'repos/{owner}/{repo}/pulls/{pr_number}/reviews', 
                             'POST', json.dumps(comment_data).encode())
        
        print(f"Review posted for PR #{pr_number}")
        return review
    
    def ai_analysis(self, files, pr):
        """Simulate AI analysis of code changes"""
        total_changes = len(files)
        additions = sum(f.get('additions', 0) for f in files)
        deletions = sum(f.get('deletions', 0) for f in files)
        
        # Simple AI simulation
        analysis = f"""
## AI Code Review Analysis

**PR #{pr['number']}: {pr['title']}**

### Summary:
- Files changed: {total_changes}
- Lines added: {additions}
- Lines deleted: {deletions}
- Total changes: {additions + deletions}

### Key Observations:
1. **File Structure**: Changes look organized
2. **Code Quality**: No obvious syntax errors detected
3. **Scope**: Changes are focused on the stated purpose

### Recommendations:
1. Add tests for new functionality
2. Update documentation if required
3. Consider adding changelog entry

**Status**: Ready for human review
"""
        
        return analysis
    
    def issue_auto_triage(self, owner, repo):
        """Automatically triage new issues"""
        print(f"Triage issues for {owner}/{repo}")
        
        # Get recent issues
        issues = self.request(f'repos/{owner}/{repo}/issues?state=open')
        
        for issue in issues:
            issue_number = issue["number"]
            title = issue["title"]
            body = issue["body"]
            
            # Simple triage logic
            if "bug" in title.lower() or "error" in title.lower():
                label = "bug"
                assignee = None
            elif "feature" in title.lower() or "enhancement" in title.lower():
                label = "enhancement"
                assignee = None
            elif "documentation" in title.lower():
                label = "documentation"
                assignee = None
            else:
                label = "triage"
                assignee = None
            
            # Update issue with labels
            if label:
                update_data = {
                    "labels": [label]
                }
                self.request(f'repos/{owner}/{repo}/issues/{issue_number}', 
                            'PATCH', json.dumps(update_data).encode())
                print(f"Issue #{issue_number} labeled as: {label}")
            
            # Add auto-response comment
            comment_data = {
                "body": f"""
Automated triage completed.

**Category**: {label}
**Priority**: Medium

This issue has been automatically categorized. Please provide additional details if needed.
"""
            }
            self.request(f'repos/{owner}/{repo}/issues/{issue_number}/comments', 
                        'POST', json.dumps(comment2_data).encode())
        
        print(f"Triage completed for {len(issues)} issues")
    
    def create_branch(self, owner, repo, branch_name, from_branch="main"):
        """Create a new branch"""
        # First get the SHA of the base branch
        branch_info = self.request(f'repos/{owner}/{repo}/branches/{from_branch}')
        sha = branch_info["commit"]["sha"]
        
        # Create branch reference
        ref_data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha
        }
        
        result = self.request(f'repos/{owner}/{repo}/git/refs', 
                            'POST', json.dumps(ref_data).encode())
        
        print(f"Branch created: {branch_name}")
        return result
    
    def merge_branch(self, owner, repo, base, head):
        """Merge two branches"""
        merge_data = {
            "base": base,
            "head": head,
            "commit_message": f"Merge {head} into {base}"
        }
        
        result = self.request(f'repos/{owner}/{repo}/merges', 
                            'POST', json.dumps(merge_data).encode())
        
        print(f"Merged {head} into {base}")
        return result

def main():
    """Demonstrate advanced automation"""
    
    api_key = os.environ.get("MATON_API_KEY")
    if not api_key:
        print("ERROR: MATON_API_KEY not set")
        sys.exit(1)
    
    automator = GitHubAutomator(api_key)
    
    # Get user info
    user = automator.request('user')
    owner = user["login"]
    
    print(f"Starting automation for user: {owner}")
    
    # Example 1: Project bootstrap
    project_files = {
        "README.md": "# Automated Project\n\nCreated by GitHub automation",
        ".gitignore": "*.log\n*.tmp\n*.env\n",
        "LICENSE": "MIT License",
        "src/main.py": "#!/usr/bin/env python3\nprint('Hello World')",
        "tests/test_main.py": "import unittest\nfrom src.main import main"
    }
    
    repo = automator.project_bootstrap("auto-demo-project", project_files)
    repo_name = repo["name"]
    
    # Example 2: Issue auto-triage
    automator.issue_auto_triage(owner, repo_name)
    
    # Example 3: Create branch
    automator.create_branch(owner2, repo_name, "feature-branch")
    
    # Example 4: Upload to branch
    branch_content = "# Feature Branch Content\n\nAdded via automation"
    encoded_content = base64.b64encode(branch_content.encode()).decode()
    upload_data = {
        "message": "Add feature branch file",
        "content": encoded_content,
        "branch": "feature-branch"
    }
    
    automator.request(f'repos/{owner}/{repo_name}/contents/feature.txt', 
                     'PUT', json.dumps(upload_data).encode())
    
    print("\n=== Advanced Automation Complete ===")
    print(f"Project: {repo['full_name']}")
    print(f"Branches: main, feature-branch")
    print(f"Files: {len(project_files)} uploaded")
    print(f"Issues: auto-triage completed")

if __name__ == "__main__":
    main()