import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

def get_jira_tasks_due_soon(base_url, email, api_token):
    cutoff_date = (datetime.now(datetime.timezone.utc) + timedelta(hours=48)).strftime('%Y-%m-%d')
    jql = f"assignee = currentUser() AND (due <= {cutoff_date} OR due is EMPTY) ORDER BY due ASC"
    url = f"{base_url}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_token), params={"jql": jql})
    issues = response.json()['issues']
    return "\n".join([i['fields']['summary'] for i in issues])