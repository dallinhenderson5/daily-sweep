from abc import ABC, abstractmethod

class IAgentWrapper(ABC):
    """Interface for agent wrapper classes."""
    
    @abstractmethod
    def get_agent(self):
        """Get the wrapped agent object."""
        pass
    
    @abstractmethod
    def invoke_agent(self, prompt: str) -> str:
        """Invoke the agent with a given prompt."""
        pass


class AgentWrapper(IAgentWrapper):
    """Concrete implementation of IAgentWrapper."""
    
    def __init__(self):
        """Initialize with an agent object."""
        self.agent = self.initialize_agent()
    
    def get_agent(self):
        """Get the wrapped agent object."""
        return self.agent
    
    def invoke_agent(self, prompt: str) -> str:
        """Invoke the agent with a given prompt."""
        response = self.agent.invoke({"input": prompt})
        return response["output"]
    