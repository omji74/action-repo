import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [logs, setLogs] = useState([]);

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:5000/events"); // Change if needed
      setLogs(res.data.reverse());
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>GitHub Events</h1>
      <ul>
        {logs.map((log, idx) => (
          <li key={idx}>{log.message}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
