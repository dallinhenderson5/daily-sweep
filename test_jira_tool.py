"""
Test file for testing the get_jira_tasks_due_soon function in isolation.
"""
import os
from tools.jiraTool import get_jira_tasks_due_soon

def test_jira_tasks():
    """Test the Jira tasks function with production parameters."""
    try:
        result = get_jira_tasks_due_soon(
            "https://nice-ce-cxone-prod.atlassian.net",
            "dallin.henderson@nice.com",
            os.environ['JIRA_API_TOKEN']
        )
        print("Success! Jira tasks retrieved:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        result = result
        print(f"Error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")

if __name__ == "__main__":
    test_jira_tasks()
