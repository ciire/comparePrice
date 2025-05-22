// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/Loginpage';
import SignupPage from './pages/SignupPage';
import Search from './Features/Search/Search';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} /> 
        <Route path="/search" element={<Search />} />
      </Routes>
    </Router>
  );
};

export default App;
