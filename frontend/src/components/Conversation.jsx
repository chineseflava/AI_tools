import React, { useEffect, useState } from 'react';
import AddMessageForm from './AddMessageForm';
import api from '../api';

const MessageList = () => {
  const [conversation, setConversation] = useState([]);

  const fetchConversation = async () => {
    try {
      const response = await api.get('/conversation');
      setConversation(response.data.conversation);
    } catch (error) {
      console.error("Error fetching conversation", error);
    }
  };

  const addMessage = async (messageName) => {
    try {
      await api.post('/conversation', { name: messageName });
      fetchConversation();  // Refresh the list after adding a message
    } catch (error) {
      console.error("Error adding message", error);
    }
  };

  useEffect(() => {
    fetchConversation();
  }, []);

  return (
    <div>
      <h2>Conversation List</h2>
      <ul>
        {conversation.map((message, index) => (
          <li key={index}>{message.name}</li>
        ))}
      </ul>
      <AddMessageForm addMessage={addMessage} />
    </div>
  );
};

export default MessageList;