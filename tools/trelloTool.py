import requests
from datetime import datetime, timedelta

def get_trello_tasks_due_soon(api_key, token):
    url = f"https://api.trello.com/1/members/me/cards?key={api_key}&token={token}"
    cards = requests.get(url).json()
    cutoff = datetime.now(datetime.timezone.utc) + timedelta(hours=48)
    due_tasks = [c for c in cards if 'due' in c and c['due'] and datetime.fromisoformat(c['due'].replace('Z','')) <= cutoff]
    return "\n".join([c['name'] for c in due_tasks])