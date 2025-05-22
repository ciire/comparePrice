// src/Components/Search/Search.jsx
import { useState } from 'react';
import './Search.css'; // You can style as needed

const Search = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const res = await fetch(`http://localhost:5000/api/search?search=${encodeURIComponent(searchTerm)}`);
      const data = await res.json();
      if (res.ok) {
        setResults(data);
      } else {
        setError(data.error || 'Search failed.');
      }
    } catch (err) {
      setError('Network error or backend not responding.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h1>Search Products</h1>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search eBay..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {results?.ebay?.length > 0 && (
        <div className="results">
          {results.ebay.map((item, idx) => (
            <div key={idx} className="result-card">
              {item.image && <img src={item.image} alt={item.title} />}
              <h3>{item.title}</h3>
              <p>${item.price.toFixed(2)}</p>
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                View on eBay
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Search;
