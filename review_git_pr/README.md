# GitHub PR SQL Code Reviewer

An automated code review tool that analyzes SQL code changes in GitHub Pull Requests using Claude AI. The tool checks for adherence to SQL guidelines, potential issues, and provides recommendations.

## Features

- Fetches PR content from GitHub API
- Reviews SQL code changes against provided guidelines
- Generates comprehensive code reviews with:
  - Overall Assessment
  - Guideline Compliance
  - Issues Found
  - Recommendations
- Automatically posts the overall assessment as a comment on the PR

## Prerequisites

- Python 3.11 or higher
- GitHub Personal Access Token with repo access
- Anthropic API Key (for Claude)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following environment variables:
```
GITHUB_TOKEN=your_github_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

Run the script with the following arguments:
```bash
python review_pr.py <owner> <repo> <pr_number>
```

Where:
- `owner`: GitHub repository owner/organization
- `repo`: Repository name
- `pr_number`: Pull request number to review

Example:
```bash
python review_pr.py elnaz-deriv documents 1
```

## Output

The tool provides two types of output:

1. Console Output: A detailed review including:
   - Overall Assessment
   - Guideline Compliance
   - Issues Found
   - Recommendations

2. GitHub PR Comment: Automatically posts the Overall Assessment section as a comment on the PR for quick feedback.

## SQL Guidelines

The tool uses SQL guidelines stored in `../store_md_to_pgvector/sql-code-layout.md` as the basis for its code review. These guidelines define the standards that the code changes are evaluated against.

## Error Handling

- Validates GitHub API responses
- Handles both string and structured responses from Claude
- Provides clear error messages for missing or invalid environment variables

## Dependencies

See `requirements.txt` for the full list of dependencies:
- anthropic: For AI-powered code review
- python-dotenv: For environment variable management
- requests: For GitHub API interactions
