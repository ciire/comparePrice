// src/Pages/LoginPage.jsx
import { useNavigate } from 'react-router-dom';
import Login from '../Features/Login/Login';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleLogin = (email, password) => {
    if (email && password) {
      // In real apps, call authService.login(email, password)
      navigate('/search');
    } else {
      alert('Please enter email and password.');
    }
  };

  return <Login onSubmit={handleLogin} />;
};

export default LoginPage;
