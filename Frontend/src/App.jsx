// /send_me_mvp/frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';

// ייבוא קומפוננטות
import AuthScreen from './components/AuthScreen';
import OnboardingFlow from './components/OnboardingFlow';
import ChatInterface from './components/ChatInterface';
import HistoryTable from './components/HistoryTable';

// מצב משתמש גלובלי
const UserContext = React.createContext(null);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // 1. טעינת נתונים שמורים (Auth)
  useEffect(() => {
    // ב-MVP: ניסיון לטעון user_id מה-localStorage
    const storedUser = localStorage.getItem('user_data');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // 2. פונקציית כניסה/יציאה גלובלית
  const loginUser = (userData) => {
    localStorage.setItem('user_data', JSON.stringify(userData));
    setUser(userData);
    
    // ניווט לאחר כניסה
    if (!userData.onboarding_complete) {
      navigate('/onboarding');
    } else {
      navigate('/chat');
    }
  };

  const logoutUser = () => {
    localStorage.removeItem('user_data');
    setUser(null);
    navigate('/');
  };

  if (loading) {
    return <div className="loading-screen">...טוען</div>;
  }

  // הגדרת נתיבים
  return (
    <UserContext.Provider value={{ user, loginUser, logoutUser, setUser }}>
      <div className="app-container">
        <header className="app-header">
          <h1>Send_Me 🚀</h1>
          {user && <button onClick={logoutUser} className="logout-btn">יציאה</button>}
        </header>
        <main className="app-content">
          <Routes>
            <Route path="/" element={user ? <ChatInterface /> : <AuthScreen />} />
            <Route path="/auth" element={<AuthScreen />} />
            
            {/* נתיבים מאובטחים: רק אם המשתמש מחובר */}
            <Route path="/onboarding" element={user ? <OnboardingFlow /> : <AuthScreen />} />
            <Route path="/chat" element={user ? <ChatInterface /> : <AuthScreen />} />
            <Route path="/history" element={user ? <HistoryTable /> : <AuthScreen />} />
            
            <Route path="*" element={<h1>404 - עמוד לא נמצא</h1>} />
          </Routes>
        </main>
      </div>
    </UserContext.Provider>
  );
}

export default App;
export { UserContext };