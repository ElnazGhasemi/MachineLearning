from langchain_community.tools.tavily_search import TavilySearchResults

import requests
from typing import Any, Callable, List, Dict
import os


def get_pr_content(owner: str, repo: str, pr_number: str) -> Dict:
    """Fetch PR content from GitHub"""

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN environment variable is not set"}
        
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        # print(f"\n{CYAN}Fetching PR #{pr_number} from {owner}/{repo}...{RESET}")
        
        pr_response = requests.get(base_url, headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        files_response = requests.get(f"{base_url}/files", headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        changes = []
        for file in files_data:
            changes.append(f"File: {file['filename']}\n{file['patch']}")
        changes_text = "\n\n".join(changes)
        
        # print(f"{GREEN}Successfully fetched PR data with {len(files_data)} changed files{RESET}")
        return {
            "title": pr_data["title"],
            "description": pr_data["body"],
            "changes_text": changes_text
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching PR from GitHub: {str(e)}"
        # print(f"{RED}{error_msg}{RESET}")
        return {"error": error_msg}
    

def post_review_comment(owner: str, repo: str, pr_number: str, comment: str) -> str:
    """Post a review comment on the GitHub PR"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN environment variable is not set"
        
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    data = {"body": comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return f"Successfully posted comment to PR #{pr_number}"
    except requests.exceptions.RequestException as e:
        return f"Error posting comment to GitHub: {str(e)}"


tools = [TavilySearchResults(max_results=1), get_pr_content, post_review_comment]
