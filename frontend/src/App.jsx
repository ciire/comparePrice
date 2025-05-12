import { useState } from 'react';
import SearchBar from './Components/SearchBar/SearchBar';
import './App.css';

const App = () => {
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async (searchTerm) => {
  try {
    console.log("Searching for:", searchTerm)
    const response = await fetch(
      `http://localhost:5000/api/search?search=${encodeURIComponent(searchTerm)}`
    );
    console.log("Raw response:", response)
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    console.log("Received data:", data)
    setResults(data.ebay || []);  // Access the ebay array or fallback to empty array
    setError(null);
  } catch (err) {
    setError(err.message);
    setResults([]);
    console.error('Search error:', err);
  }
};

  return (
    <div className="app-container">
      <h1>eBay Product Search</h1>
      
      <SearchBar onSearch={handleSearch} />
      
      {error && <div className="error-message">{error}</div>}

      <div className="results-container">
        {results.map((product, index) => (
          <div key={index} className="product-card">
            {/* Product Image */}
            {product.image && (
              <div className="product-image-container">
                <img 
                  src={product.image} 
                  alt={product.title}
                  className="product-image"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/300x300?text=No+Image';
                  }}
                />
              </div>
            )}
            
            {/* Product Info */}
            <h3>{product.title}</h3>
            <p>Price: {product.price ? `$${product.price.toFixed(2)}` : 'Price not available'}</p>
            {/* Added eBay product link */}
            <a 
              href={product.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="ebay-link"
            >
              View on eBay
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;