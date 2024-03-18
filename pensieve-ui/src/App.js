import React, { useState } from 'react';

function App() {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = async () => {
    try {
      const currentDate = new Date().toISOString().split('T')[0];
      const dataToSend = `${currentDate},${inputValue}`;

      /*
      const response = await fetch('backend-endpoint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: dataToSend }),
      });
      if (response.ok) {
        // Handle success response
        console.log('Request sent successfully!');
      } else {
        // Handle error response
        console.error('Failed to send request:', response.statusText);
      }
      */

     console.log(dataToSend);
    } catch (error) {
      console.error('Error sending request:', error.message);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>The Pensieve - the magical artifact</h1>
      <textarea
        style={styles.input}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Hey, How are you today..."
      />
      <button style={styles.button} onClick={handleSubmit}>Submit</button>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#f0f0f0',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#333',
  },
  input: {
    width: '80%',
    height: '200px',
    padding: '0.5rem',
    fontSize: '1rem',
    marginBottom: '2rem',
    border: '1px solid #ccc',
    borderRadius: '5px',
  },
  button: {
    padding: '0.8rem 1.5rem',
    fontSize: '1rem',
    fontWeight: 'bold',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
};

export default App;
