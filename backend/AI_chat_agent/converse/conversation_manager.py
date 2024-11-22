import os
import json
import sys

from datetime import datetime
from AIChatAgent import AIChatAgent
from prompts import summarize, helpful_role

# Contains the Conversation Manager module's logic
class ConversationManager:
    def __init__(self, conversation_id=None, role=helpful_role):
        """
        Initialize the Conversation Manager.

        Args:
            conversation_id (str): The ID of the conversation.
            role (str): The role of the assistant.

        Returns:
            ConversationManager: An instance of the ConversationManager class.
        """
        # Client setup.
        self.agent = AIChatAgent()
        self.conversations_folder = "conversations"
        self.conversation_history = [
                {"role": "system", "content": role}
            ]
        self.conversation_id = conversation_id
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
        Save conversation to conversation_history_path.

        Raises:
            FileNotFoundError: If the conversation history file does not exist.
        """
        try:
            with open(self.conversation_history_path, "w") as f:
                json.dump(self.conversation_history, f, indent=4)
        except FileNotFoundError:
            print(f"File {self.conversation_history_path} not found.")

    def load_conversation(self):
        """
        Load conversation from existing file.

        Raises:
            FileNotFoundError: If the conversation history file does not exist.
            json.JSONDecodeError: If the conversation history file is not a valid JSON.
        """
        try:
            selected_file = self.conversation_history_path
            with open(selected_file, "r") as f:
                loaded_history = json.load(f)
                self.conversation_history.clear()
                self.conversation_history.extend(loaded_history)
        except FileNotFoundError:
            print(f"File {selected_file} not found.")
        except json.JSONDecodeError as e:
            print(f"Failed to parse conversation history: {e}")

    def send_message(self, message):
        """
        Send a message to the chat agent and return the response.

        Args:
            message (str): The message to send.

        Returns:
            str: The response from the chat agent.
        """
        if not message.strip():
            print("Message cannot be empty.")
            return None

        # Prune history if needed:
        self.prune_conversation()

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Get assistant's response and add it to conversation history
        response = self.agent.send_llm_message(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response})

        # Save updated conversation history to file
        self.save_conversation()
        
        return response
    
    def prune_conversation(self, trigger_size=20, limit=250):
        """
        Prune the conversation to a certain size.

        Triggers a data-limit check when conversation is over 20 messages.
        Prunes if data of conversation is above limit (what data format?).

        If the conversation exceeds the maximum size, it removes half of the conversation and summarizes it.
        """
        if len(self.conversation_history) > trigger_size:
            with open(self.conversation_history_path, 'r') as f:
                data = json.load(f)
                mem_size = sys.getsizeof(data)
                if mem_size > limit:
                    half_size = len(self.conversation_history) // 2
                    summary_history = self.conversation_history[:half_size]
                    summary_content = self._summarize_conversation(summary_history)
                    self.conversation_history = [self.conversation_history[0]] + [
                        {"role": "assistant", "content": summary_content}
                    ] + self.conversation_history[half_size:]
                    self.save_conversation()
                else:
                    print(f"\n\n\nSize only {mem_size}. \nPruning uneccesary")

    def _summarize_conversation(self,history):
        """
        Summarize a list of conversation messages.

        Args: 
            history {a:1, b:2 ...}
        
        Use the LLM-model itself to generate a summary based on history.
        """
        history.append({"role": "user", "content":  summarize})
        
        try:
            summary = self.agent.send_llm_message(history)
            #print("***Pruning Summary:***\n\n\n" + summary + "\n\n\n")
        except Exception as e:
            print(f"Failed to send message: {e}\nUsing fallback pruning...")
            #TODO: Implement fallback pruning.
            return None # self._fallback_summarize_conversation(history) Skip this for now...
        return summary
    
    def _fallback_summarize_conversation(self, history):
        """
        Summarize a list of conversation messages.

        It extracts the first 50 characters of each message and joins them together with a space to form a summary.
        """
        summary = []
        for message in history:
            if message["role"] != "assistant":
                summary.append(message["content"][:50])
        return " ".join(summary)

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
    
    running = True
    def on_press(key):
        global running
        if key == keyboard.Key.esc:
            # Set running to False to exit the loop
            running = False
            return False  # Stop the listener
    
    
    # Start the listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
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