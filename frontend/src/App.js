import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import HomePage from './components/HomePage';
import GamePage from './components/GamePage';

function App() {
  return (
    <Router>
      <Routes>
        {/* Redirect root to English by default */}
        <Route path="/" element={<Navigate to="/en" replace />} />
        
        {/* Language-specific routes */}
        <Route path="/:lang" element={<HomePage />} />
        <Route path="/:lang/game" element={<GamePage />} />
        
        {/* Catch all other routes and redirect to English */}
        <Route path="*" element={<Navigate to="/en" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
