from __future__ import annotations
from livekit.agents import ( # Import necessary modules from livekit.agents
    AutoSubscribe, 
    JobContext, 
    WorkerOptions, 
    cli, 
    llm
)

from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from backend.api import AssistantFnc
from backend.prompt import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
import os

load_dotenv() # load in .env file to access environment variables

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL) # Automatically subscribe to all rooms
    await ctx.wait_for_participant() # Wait for a participant to join the room

    model = openai.realtime.RealtimeModel( # Initialize the OpenAI model
        instructions = INSTRUCTIONS, 
        voice = "shimmer", 
        temperature = 0.7,
        modalities = ["text", "audio"],
         # Specify the model to use
    )
    assistant_fnc = AssistantFnc() # Initialize the function context for the assistant
    assistant = MultimodalAgent(model=model, fnc_ctx = assistant_fnc) # Create the multimodal agent variable
    assistant.start(ctx.room) #Start the agent in the room once the participant has joined

    session = model.sessions[0] #creating the intial session for the agent
    session.conversation.item.create( # Create the initial message in the conversation
        llm.ChatMessage(
            role="assistant", 
            content= WELCOME_MESSAGE
        )
    )
    session.response.create() #Create a response to the intial message 

    #DESIGNING THE AGENT DECISION TREE
    @session.on("user_speech_commited")
    def on_user_speech_commited(msg: llm.ChatMessage): # Handle user speech committed event
        if isinstance(msg.content, list): 
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg) 
            #if we are unable to process the image, we will just return the same exact text(x)

        if assistant_fnc.has_car():
            handle_query(msg)
        else: 
            find_profile(msg)
    
    def find_profile(msg: llm.ChatMessage): 
        session.conversation.item.create(
            llm.ChatMessage(
                role="system", 
                content= LOOKUP_VIN_MESSAGE(msg) # Use the LOOKUP_VIN_MESSAGE to prompt for VIN lookup
            )
        )
        session.response.create()
    
    def handle_query(msg: llm.ChatMessage): 
        session.conversation.item.create(
            llm.ChatMessage(
                role="user", 
                content=msg.content
            )
        )
        session.response.create()

if __name__ == "__main__": 
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint)) # Run the application with the specified entrypoint function