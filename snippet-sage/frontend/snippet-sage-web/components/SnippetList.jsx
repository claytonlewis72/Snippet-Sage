import { useState, useEffect } from 'react';

function SnippetList() {
  const [snippets, setSnippets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/snippets')
      .then(res => {
        if (!res.ok) throw new Error('Failed to load snippets');
        return res.json();
      })
      .then(data => {
        setSnippets(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading snippets…</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {snippets.map(snippet => (
        <li key={snippet.id}>
          <h3>{snippet.title}</h3>
          <pre><code>{snippet.code}</code></pre>
          <small>{snippet.language}</small>
        </li>
      ))}
    </ul>
  );
}

export default SnippetList;