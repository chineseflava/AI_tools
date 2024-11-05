import os
import groq
import json

from dotenv import load_dotenv
from datetime import datetime

# Contains the Conversation Manager module's logic
class ConversationManager:
    def __init__(self, conversation_id=None, role="You are a helpful assistant"):
        """
        Initialize the Conversation Manager.
        """
        # Client setup.
        load_dotenv()
        API_KEY = os.getenv("GROQ_API_KEY")
        self.groq_client = groq.Groq(api_key=API_KEY)

        self.conversations_folder = "conversations"
        self.conversation_history = [
                {"role": "system", "content": role}
            ]
        if conversation_id:
            self.conversation_history_path = os.path.join(self.conversations_folder, conversation_id)
            self.load_conversation()
        else:
            # Create a timestamped file name for the conversation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"conversation_{timestamp}.json"
            self.conversation_history_path = os.path.join("conversations", file_name)
            self.save_conversation()
        
    def save_conversation(self):
        """
        Save conversation to conversation_history_path-
        """
        with open(self.conversation_history_path, "w") as f:
            json.dump(self.conversation_history, f, indent=4)

    def load_conversation(self):
        """
        Load conversation from existing file
        """
        selected_file = self.conversation_history_path
        with open(selected_file, "r") as f:
            loaded_history = json.load(f)
            self.conversation_history.clear()
            self.conversation_history.extend(loaded_history)

    def send_message(self, message):
        """
        Send a message to the Groq client and return the response.

        Args:
            message (str): The message to send.
            conversation_id (int): The ID of the conversation.

        Returns:
            str: The response from the Groq client.
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        # Send the entire conversation history to maintain context
        chat_completion = self.groq_client.chat.completions.create(
            messages=self.conversation_history,
            model="llama-3.1-70b-versatile",  # Ensure this model exists
            stream=False,
        )

        # Get assistant's response and add it to conversation history
        response = chat_completion.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Save updated conversation history to file
        self.save_conversation()
        
        return response
    

def create_conversation_manager():
    """
    Create a Conversation Manager instance.

    Returns:
        ConversationManager: A Conversation Manager instance.
    """
    folder_path = "conversations"
    files = os.listdir(folder_path)
    json_files = [f for f in files if f.endswith(".json")]

    # Display available conversations
    if not json_files:
        print("No saved conversations found. Starting a new conversation.")
        return ConversationManager()
    
    print("Available conversations:")
    for i, file in enumerate(json_files):
        print(f"{i+1}. {file}")

    # Prompt user to select a conversation
    choice = int(input("Select a conversation to load (enter number): ")) - 1
    if choice < 0 or choice >= len(json_files):
        print("Invalid selection. Starting a new conversation.")
        return ConversationManager()

    conversation_id = json_files[choice]
    print(f"Loaded conversation from {json_files[choice]}")
    return ConversationManager(conversation_id)


if __name__ == "__main__":
    # Testing:
    from pynput import keyboard
    def on_press(key):
        global running
        if key == keyboard.Key.esc:
            # Set running to False to exit the loop
            running = False
            return False  # Stop the listener
    
    # Start the listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    running = True
    conversation_manager = create_conversation_manager()

    while running:
        message = input("+----+\nYou: ")
        if not running: # Check if ESC was pressed to break the loop
            print("Exiting program...")
            break
        response = conversation_manager.send_message(message)
        print("Assistant:", response)

    # Stop the listener when exiting
    listener.stop()
    listener.join()
