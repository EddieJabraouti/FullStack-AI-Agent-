#file that will contain all the tools the agent needs such as: 
# Database, Looking up a specific user info, creating a new user, shceedule a meeting, etc.

from livekit.agents import llm

class AssistantFnc(llm.FunctionContext): 
    def __init__(self):
        super().__init__()