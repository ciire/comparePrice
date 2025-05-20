// src/Components/Login/Login.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom'
import './Login.css'; // If you move the CSS here

const Login = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(email, password);
  };

return (
  <div className="login-container">
    <h1>Login</h1>
    <form onSubmit={handleSubmit}>
      <input 
        type="email" 
        placeholder="Email" 
        value={email}
        onChange={e => setEmail(e.target.value)} 
      />
      <input 
        type="password" 
        placeholder="Password" 
        value={password}
        onChange={e => setPassword(e.target.value)} 
      />
      <button type="submit">Login</button>
    </form>

    {/* Sign-up link */}
    <p className="signup-link">
      Don&apos;t have an account? <Link to="/signup">Sign up</Link>
    </p>
  </div>
  );
};

export default Login;
