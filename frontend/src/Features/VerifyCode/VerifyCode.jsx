import { useState } from 'react';

const VerifyCode = ({ email, token, onVerify, message, purpose }) => {
  const [code, setCode] = useState('');
  const [statusMessage, setStatusMessage] = useState(message || '');

  const handleSubmit = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/verifyEmail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          code,
          token,
          purpose, 
        }),
      });

      const data = await res.json();

      if (res.ok && data.status === 'success') {
        setStatusMessage('Verification successful!');
        onVerify(code); // pass data to parent (can include user_id)
      } else {
        setStatusMessage(data.error || 'Verification failed.');
      }
    } catch (err) {
      console.error(err);
      setStatusMessage('Network error. Please try again.');
    }
  };

  return (
    <div className="verification-popup">
      <h2>Enter 6-digit Code</h2>
      <input
        type="text"
        maxLength={6}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="123456"
      />
      <button onClick={handleSubmit}>Verify</button>
      {statusMessage && <p>{statusMessage}</p>}
    </div>
  );
};

export default VerifyCode;
