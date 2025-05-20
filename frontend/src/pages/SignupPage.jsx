import { useNavigate } from 'react-router-dom';
import Signup from '../Features/Signup/Signup'; // Create this form

const SignupPage = () => {
  const navigate = useNavigate();

  const handleSignup = async (email, password) => {
    if (!email || !password) {
      alert('Please enter email and password.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Signup failed');
        return;
      }

      alert('Signup successful! You can now log in.');
      navigate('/'); 
    } catch (error) {
      console.error('Signup error:', error);
      alert('An error occurred during signup.');
    }
  };

  return <Signup onSubmit={handleSignup} />;
};

export default SignupPage;
