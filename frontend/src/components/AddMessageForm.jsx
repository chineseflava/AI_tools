import React, { useState } from 'react';

const AddMessageForm = ({ addMessage }) => {
  const [messageName, setMessageName] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (messageName) {
      addMessage(messageName);
      setMessageName('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={messageName}
        onChange={(e) => setMessageName(e.target.value)}
        placeholder="Enter message"
      />
      <button type="submit">Add Message</button>
    </form>
  );
};

export default AddMessageForm;