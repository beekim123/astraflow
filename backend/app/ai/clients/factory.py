from app.ai.clients.http_agent_client import HttpAgentClient
from app.ai.contracts.client import AgentClient


def get_agent_client() -> AgentClient:
    return HttpAgentClient()
