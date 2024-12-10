import os
import groq
import requests
from intent_templates import helpful_role

from dotenv import load_dotenv

class AIChatAgent:
    def __init__(self, name="assistant", role=helpful_role, model="llama-3.3-70b-versatile"):
        self.name = name
        self.role = role
        self.model = model
        
        # Client setup.
        load_dotenv()
        API_KEY = os.getenv("GROQ_API_KEY")
        self.groq_client = groq.Groq(api_key=API_KEY)

    def send_llm_message(self,messages):
        """
        Send a message to the Groq client and return the response.

        Args:
            message (str): The message to send.

        Returns:
            str: The response from the Groq client.

        Raises:
            requests.exceptions.RequestException: If the request to the Groq client fails.
            json.JSONDecodeError: If the response from the Groq client is not a valid JSON.
        """
        try:
            # Send the entire conversation history to maintain context
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=self.model,  
                stream=False,
            )
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message: {e}")
            return None
        except groq.GroqError as e:
            print(f"A GroqError occured: {e}")
            return None

        try:
            # Get assistant's response and add it to conversation history
            response = chat_completion.choices[0].message.content
        except (AttributeError, IndexError) as e:
            print(f"Failed to get response: {e}")
            return None
        
        return response