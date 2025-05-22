import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Signup from '../Features/Signup/Signup';
import VerifyCode from '../Features/VerifyCode/VerifyCode';

const SignupPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('form'); // 'form' or 'verify'
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');

  const handleSignup = async (emailInput, password) => {
    if (!emailInput || !password) {
      alert('Please enter email and password.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailInput, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Signup failed');
        return;
      }

      setEmail(emailInput);
      setToken(data.token);
      setMessage('Verification code sent to your email.');
      setStep('verify');
    } catch (error) {
      console.error('Signup error:', error);
      alert('An error occurred during signup.');
    }
  };

  const handleVerifySuccess = () => {
    alert('Signup complete and email verified!');
    navigate('/');
  };

  return (
    <>
      {step === 'form' ? (
        <Signup onSignup={handleSignup} />
      ) : (
        <VerifyCode
          email={email}
          token={token}
          message={message}
          purpose="email_verification"
          onVerify={handleVerifySuccess}
        />
      )}
    </>
  );
};

export default SignupPage;
