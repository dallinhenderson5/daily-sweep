import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone

def get_jira_tasks_due_soon(base_url, email, api_token):
    cutoff_date = (datetime.now(timezone.utc) + timedelta(hours=48)).strftime('%Y-%m-%d')
    jql = f"assignee = currentUser() AND (due <= {cutoff_date} OR due is EMPTY) ORDER BY due ASC"
    url = f"{base_url}/rest/api/3/jql/match"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = json.dumps( {
        "issueIds": [
            "DE-156221",
            "DE-156222",
            "DE-156223"
        ],
        "jqls": [
            "project = CX_Digital_Engagement",
            "issuetype = Story",
            "summary ~ \"DXW\""
        ]
    } )
    auth=HTTPBasicAuth(email, api_token)
    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)#, params={"jql": jql})
    issues = response.json()['issues']
    return "\n".join([i['fields']['summary'] for i in issues])