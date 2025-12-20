import os
import sys
import io

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
from dotenv import load_dotenv
from .client_ai import ClientAI
from .agent import Agent
from . import console_ui

load_dotenv()

client_ai = ClientAI(
    api_key=os.getenv("UNIFIE_API_KEY"),
    base_url=os.getenv("UNIFIE_API_URL"),
    timeout=120.0
)

agent = Agent()

async def main():
    # Show welcome banner
    console_ui.display_welcome()
    
    # Chat loop
    while True:
        user_input = console_ui.prompt_user()

        # Validations
        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            console_ui.display_goodbye()
            break
        
        # Display user message
        console_ui.display_user_message(user_input)
        
        # Add message to history
        agent.messages.append({"role": "user", "content": user_input})
        
        while True:
            # Show thinking spinner while waiting for response
            with console_ui.ThinkingSpinner():
                response = await client_ai.chat_completions_create(
                    model="moonshot-MBZUAI-IFM/K2-Think",
                    messages=agent.messages
                )

            result = await agent.process_response(response)

            if not result:
                break


if __name__ == "__main__":
    asyncio.run(main())