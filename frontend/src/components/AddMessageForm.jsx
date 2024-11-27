import React, { useState } from 'react';

const AddMessageForm = ({ addMessage }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (message) {
      addMessage(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Enter message"
      />
      <button type="submit">Add Message</button>
    </form>
  );
};

export default AddMessageForm;