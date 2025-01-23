import os
from typing import Dict
from dotenv import load_dotenv
import anthropic
import requests

load_dotenv()

def extract_overall_assessment(review) -> str:
    """Extract the Overall Assessment section from the review"""
    # Handle both string and TextBlock formats
    if isinstance(review, str):
        text = review
    else:
        text = review[0].text if review else ""
    
    lines = text.split('\n')
    assessment = []
    in_assessment = False
    
    for line in lines:
        if line.startswith('## Overall Assessment'):
            in_assessment = True
            continue
        elif line.startswith('## '):
            in_assessment = False
        elif in_assessment and line.strip():
            assessment.append(line.strip())
    
    return '\n'.join(assessment)

def post_pr_comment(owner: str, repo: str, pr_number: int, comment: str) -> None:
    """Post a comment on the GitHub PR"""
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    data = {"body": comment}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

def get_github_pr(owner: str, repo: str, pr_number: int) -> Dict:
    """Fetch PR content from GitHub"""
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    pr_response = requests.get(base_url, headers=headers)
    pr_data = pr_response.json()
    
    # Get PR files
    files_response = requests.get(f"{base_url}/files", headers=headers)
    files_data = files_response.json()
    
    return {
        "title": pr_data["title"],
        "description": pr_data["body"],
        "files": files_data
    }

def create_review(title: str, description: str, changes: str) -> str:
    """Create a code review using Anthropic's Claude"""
    
    # Load SQL guidelines
    with open("../store_md_to_pgvector/sql-code-layout.md", "r") as f:
        sql_guidelines = f.read()
    
    # Create prompt
    prompt = f"""You are a SQL code reviewer. Review the following PR changes according to our SQL guidelines.
    
    SQL Guidelines:
    {sql_guidelines}
    
    PR Title: {title}
    PR Description: {description}
    
    Changes to review:
    {changes}
    
    Please provide a detailed review that covers:
    1. Adherence to SQL code layout guidelines
    2. Potential issues or bugs
    3. Suggestions for improvements
    4. Any violations of our SQL standards
    
    Format your response as:
    ## Overall Assessment
    [High-level summary]
    
    ## Guideline Compliance
    [Specific points about adherence to guidelines]
    
    ## Issues Found
    [List any issues]
    
    ## Recommendations
    [Specific suggestions for improvement]
    """
    
    # Create client
    client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Get review
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text if isinstance(message.content, list) else message.content

def main(owner: str, repo: str, pr_number: int):
    """Main function to review a PR"""
    
    # Get PR content
    pr_content = get_github_pr(owner, repo, pr_number)
    
    # Extract file changes
    changes = []
    for file in pr_content["files"]:
        changes.append(f"File: {file['filename']}\n{file['patch']}")
    changes_text = "\n\n".join(changes)
    
    # Get review
    review = create_review(
        title=pr_content["title"],
        description=pr_content["description"],
        changes=changes_text
    )
    
    print(review)
    
    # Post full review as a PR comment
    if review:
        comment = "## Code Review\n\n" + review
        post_pr_comment(owner, repo, pr_number, comment)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Review GitHub PR')
    parser.add_argument('owner', help='Repository owner')
    parser.add_argument('repo', help='Repository name')
    parser.add_argument('pr_number', type=int, help='PR number')
    
    args = parser.parse_args()
    main(args.owner, args.repo, args.pr_number)
