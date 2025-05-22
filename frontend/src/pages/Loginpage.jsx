import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Login from '../Features/Login/Login';
import VerifyCode from '../Features/VerifyCode/VerifyCode'; // new component

const LoginPage = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState('login'); // 'login' | 'verify'
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [userId, setUserId] = useState('');

  const handleLogin = async (email, password) => {
    if (!email || !password) return alert("Please enter email and password.");

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok) {
        setEmail(email);
        setToken(data.token);
        setUserId(data.user_id);
        setStep('verify');
      } else {
        alert(data.error || "Login failed");
      }
    } catch (err) {
      console.error(err);
      alert("Error during login.");
    }
  };

  const handleVerify = async (code) => {
    try {
      const response = await fetch('http://localhost:5000/api/verifyEmail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          code,
          token,
          purpose: 'login_verification'
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Optionally store session info
        localStorage.setItem('userId', data.user_id);
        navigate('/search');
      } else {
        alert(data.error || "Verification failed");
      }
    } catch (err) {
      console.error(err);
      alert("Error during verification.");
    }
  };

return step === 'login' ? (
    <Login onSubmit={handleLogin} />
  ) : (
    <VerifyCode
      email={email}
      token={token}
      purpose="login_verification"
      onVerify={handleVerify}
    />
  );
}

export default LoginPage;
