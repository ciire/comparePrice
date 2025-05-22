import { useState } from 'react';
import './Signup.css';

const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showVerify, setShowVerify] = useState(false);
  const [token, setToken] = useState('');
  const [code, setCode] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok) {
        setToken(data.token); // token from backend
        setShowVerify(true); // show the code input
        setStatusMessage('Verification code sent to your email.');
      } else {
        setStatusMessage(data.error || 'Signup failed.');
      }
    } catch (err) {
      setStatusMessage('Network error. Please try again.');
    }
  };

  const handleCodeSubmit = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/verifyEmail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          code,
          token
        })
      });

      const data = await res.json();

      if (res.ok) {
        setStatusMessage('Email verified successfully!');
        setShowVerify(false);
      } else {
        setStatusMessage(data.error || 'Verification failed.');
      }
    } catch (err) {
      setStatusMessage('Network error. Please try again.');
    }
  };

  return (
    <div className="signup-container">
      <h1>Sign Up</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Sign Up</button>
      </form>

      {statusMessage && <p>{statusMessage}</p>}

      {showVerify && (
        <div className="verification-popup">
          <h2>Enter 6-digit Code</h2>
          <input
            type="text"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456"
          />
          <button onClick={handleCodeSubmit}>Verify</button>
        </div>
      )}
    </div>
  );
};

export default Signup;
