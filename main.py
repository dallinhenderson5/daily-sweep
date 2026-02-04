from urllib import response
import json
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from tools.trelloTool import get_trello_tasks_due_soon
from tools.jiraTool import get_jira_tasks_due_soon
from agent_wrapper import AgentWrapper
import os

def main():
    agent_wrapper = AgentWrapper(initialize_agent())
    
    response = agent_wrapper.invoke_agent("Please summarize all of my tasks due in the next 48 hours from Jira only.")
    
    # Convert response to JSON-serializable format
    response_data = []
    for msg in response:
        response_data.append({
            "type": type(msg).__name__,
            "content": msg.content
        })
    
    # Serialize to JSON string
    response_json = json.dumps(response_data, indent=2)
    
    # Write to file and print
    with open('agent_response.txt', 'w') as file:
        file.write(response_json)
    print(response_json)

def lambda_handler(event, context):
    agent_wrapper = AgentWrapper(initialize_agent())
    
    response = agent_wrapper.invoke_agent("Please summarize all of my tasks due in the next 48 hours from Jira only.")
    return {
        "statusCode": 200,
        "body": response
    }

def initialize_agent():
    # ANTHROPIC_API_KEY must be loaded into env variables
    model = ChatAnthropic(
        api_key=os.environ['ANTHROPIC_API_KEY'],
        model="claude-haiku-4-5-20251001",
        temperature=0.1,
        max_tokens=1000,
        timeout=30
    )

    tools = [trello_search, jira_search]
    system_prompt="You are a helpful assistant. Always begin responses with a greeting. Always end responses with a recommendation for what tasks to work on first."               # FIXME
    
    agent = create_agent(
                        model, 
                        tools=tools, 
                        middleware=[handle_tool_errors],
                        system_prompt=system_prompt
    )
    return agent
    
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

if __name__ == "__main__":
    main()
