from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
#from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os

# --- Initialize LangChain Agent ---
#model = ChatOpenAI(
# ANTHROPIC_API_KEY must be loaded into env variables
model = ChatAnthropic(
    api_key=os.environ['ANTHROPIC_API_KEY'],
    model="claude-haiku-4-5-20251001",
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

# --- LangChain Tools ---
@tool("TrelloTasksDueSoon", description="Fetch Trello tasks due in the next 48 hours")
def trello_search() -> str:
    return get_trello_tasks_due_soon("YOUR_TRELLO_API_KEY", "YOUR_TRELLO_TOKEN")

# API Key must be loaded into env variables
@tool("JiraTasksDueSoon", description="Fetch Jira tasks due in the next 48 hours")
def jira_search() -> str:
    return get_jira_tasks_due_soon("https://nice-ce-cxone-prod.atlassian.net/jira", "dallin.henderson@nice.com", os.environ['JIRA_API_KEY'])

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

tools = [trello_search, jira_search]
system_prompt="You are a helpful assistant. Always begin responses with a greeting. Always end responses with a recommendation for what tasks to work on first."               # FIXME
agent = create_agent(
                     model, 
                     tools=tools, 
                     middleware=[handle_tool_errors],   
                     #agent="zero-shot-react-description",
                     system_prompt=system_prompt
                     #verbose=True
)

# --- Trello Tool Task ---
def get_trello_tasks_due_soon(api_key, token):
    url = f"https://api.trello.com/1/members/me/cards?key={api_key}&token={token}"
    cards = requests.get(url).json()
    cutoff = datetime.utcnow() + timedelta(hours=48)
    due_tasks = [c for c in cards if 'due' in c and c['due'] and datetime.fromisoformat(c['due'].replace('Z','')) <= cutoff]
    return "\n".join([c['name'] for c in due_tasks])

# --- Jira Tool Task ---
def get_jira_tasks_due_soon(base_url, email, api_token):
    cutoff_date = (datetime.now(datetime.timezone.utc) + timedelta(hours=48)).strftime('%Y-%m-%d')
    jql = f"assignee = currentUser() AND (due <= {cutoff_date} OR due is EMPTY) ORDER BY due ASC"
    url = f"{base_url}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_token), params={"jql": jql})
    issues = response.json()['issues']
    return "\n".join([i['fields']['summary'] for i in issues])

def invokeAgent():
    prompt = "Please summarize all of my tasks due in the next 48 hours from Jira only." #"Please summarize all of my tasks due in the next 48 hours from Trello and Jira."
    response = agent.invoke({"input": prompt})
    return response["output"]

#def __main__():
response = invokeAgent()
with open('agent_response.txt', 'w') as file:
    file.write("Agent Response:" + response)
    #print("Agent Response:")
    #print(response)

def lambda_handler(event, context):
    response=invokeAgent()
    return {
        "statusCode": 200,
        "body": response
    }
