import os
import asyncio
from dotenv import load_dotenv
from .client_ai import ClientAI
from .agent import Agent

load_dotenv()

client_ai = ClientAI(
    api_key=os.getenv("UNIFIE_API_KEY"),
    base_url=os.getenv("UNIFIE_API_URL")
)

agent = Agent()

async def main():
    # Chat loop
    while True:
        user_input = input("You: ").strip()

        # Validations
        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            print("Goodbye!")
            break
        
        # Add our message to the history
        agent.messages.append({"role": "user", "content": user_input})
        
        while True:
            response = await client_ai.chat_completions_create(
                model="moonshot-MBZUAI-IFM/K2-Think",
                messages=agent.messages
            )

            response = agent.process_response(response)

            if not response:
                break


if __name__ == "__main__":
    asyncio.run(main())