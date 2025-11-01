// /send_me_mvp/frontend/src/components/OnboardingFlow.jsx - קוד מתוקן
import React, { useState, useContext, useEffect } from 'react';
import useApi from '../hooks/useApi';
import { UserContext } from '../App';
import { useNavigate } from 'react-router-dom';

function OnboardingFlow() {
    const { user, setUser } = useContext(UserContext);
    const { loading, error, callApi, api } = useApi();
    const navigate = useNavigate();
    
    // אתחול flowStep ל-0 (או null). נשתמש ב-useEffect כדי להחליט על שלב 2.
    const [flowStep, setFlowStep] = useState(0); 
    const [resumeFile, setResumeFile] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({}); // {q_id: value}

    // בדיקת סטטוס המשתמש והגדרת flowStep
    useEffect(() => {
        if (user && user.onboarding_complete) {
            setFlowStep(2); // אם כבר הושלם
        } else if (user) {
            setFlowStep(0); // אם לא הושלם, התחל משלב 0
        }
    }, [user]); // רץ רק כשהמשתמש נטען או משתנה

    // --- מצב 2: הושלם ---
    if (flowStep === 2) {
        return <div className="screen-container">
            <h2>האונבורדינג הושלם!</h2>
            <p>הפרופיל שלך מוכן. ניתן לעבור למסך ההגשות.</p>
            <button onClick={() => navigate('/chat')}>עבור להגשה</button>
        </div>
    }

    // מניעת המשך רינדור אם המשתמש לא נטען או flowStep עדיין 0
    if (!user || flowStep === null) {
         return <div className="loading-screen">טוען נתוני אונבורדינג...</div>;
    }


    // --- שלב 0: העלאת קורות חיים ---
    const handleResumeUpload = async (e) => {
        e.preventDefault();
        
        if (!resumeFile) return alert("אנא בחר קובץ קורות חיים.");

        try {
            // 1. יצירת FormData (נדרש להעלאת קבצים)
            const formData = new FormData();
            formData.append('user_id', user.user_id);
            formData.append('resume_file', resumeFile);

            // 2. קריאה עם Headers מותאמים (Content-Type: multipart/form-data)
            // השתמש ב-api.post כיוון שצריך לשלוח FormData
            const response = await api.post('/onboarding/resume', formData, {
                headers: {
                    // Axios קובע אוטומטית 'multipart/form-data' עם גבול (boundary) מתאים
                    // לכן אין צורך להגדיר כאן Content-Type ידנית, אך נשאיר את הפורמט כבסיס.
                }
            });
            
            // 3. עדכון ה-State והמשך לזרימה הבאה
            // חשוב: response.profile מכיל את נתוני המשתמש המעודכנים (כולל שם, מייל וכו')
            setUser(response.profile); 
            setQuestions(response.questions.questions);
            setFlowStep(1); // מעבר לשלב השאלות

        } catch (e) {
            // אם יש שגיאת רשת או 4xx/5xx מה-Backend, השתמש ב-error מה-Hook
            const errorMessage = error || "שגיאה בפירוק קורות החיים ע\"י ה-AI.";
            console.error("שגיאת העלאת קו\"ח:", e);
            alert(errorMessage);
        }
    };
    
    if (flowStep === 0) {
        return (
            <div className="screen-container">
                <h2>שלב 1: העלאת קורות חיים</h2>
                <p>אנו נשתמש בקורות החיים שלך כדי לפרק את הנתונים ולייצר שאלות מיקוד.</p>
                <form onSubmit={handleResumeUpload}>
                    <input 
                        type="file" 
                        accept=".pdf" 
                        onChange={(e) => setResumeFile(e.target.files[0])} 
                        required 
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'מפרק קו"ח...' : 'העלה והמשך'}
                    </button>
                    {/* השתמש ב-error המגיע מה-Hook */}
                    {error && <div className="error">{error}</div>} 
                </form>
            </div>
        );
    }

    // --- שלב 1: שאלות מיקוד ---
    const handleAnswerChange = (qId, value) => {
        // qId הוא תוכן השאלה (q.q)
        setAnswers(prev => ({ ...prev, [qId]: value }));
    };

    const handleFocusSubmit = async () => {
        if (Object.keys(answers).length !== questions.length) {
            alert("אנא ענה על כל שאלות המיקוד.");
            return;
        }

        try {
            await callApi('post', '/onboarding/focus-questions', {
                user_id: user.user_id,
                answers: answers
            });
            
            // עדכון גלובלי והעברה ל-Chat
            setUser(prev => ({ ...prev, onboarding_complete: true }));
            navigate('/chat');
            
        } catch (e) {
            alert(error || "שגיאה בשמירת התשובות.");
        }
    };
    
    return (
        <div className="screen-container">
            <h2>שלב 2: שאלות מיקוד</h2>
            <p>ה-AI יצר עבורך שאלות מותאמות אישית. ענה עליהן כדי להתאים את המענה העתידי.</p>
            
            {questions.map((q, index) => (
                <div key={index} className="question-block" style={{ marginBottom: '20px', border: '1px solid #ddd', padding: '15px', borderRadius: '4px' }}>
                    <h4>{q.q}</h4>
                    {q.options.map((opt, optIndex) => (
                        <div key={optIndex} style={{ display: 'block', margin: '10px 0' }}>
                            <input
                                type="radio"
                                id={`q-${index}-opt-${optIndex}`}
                                name={`question-${index}`}
                                value={opt.value}
                                checked={answers[q.q] === opt.value} // משווה את התשובה שנבחרה
                                onChange={() => handleAnswerChange(q.q, opt.value)}
                            />
                            <label htmlFor={`q-${index}-opt-${optIndex}`} style={{ marginRight: '10px' }}>{opt.text}</label>
                        </div>
                    ))}
                </div>
            ))}
            
            <button onClick={handleFocusSubmit} disabled={loading || Object.keys(answers).length !== questions.length}>
                {loading ? 'שומר...' : 'סיים אונבורדינג'}
            </button>
            {error && <div className="error">{error}</div>}
        </div>
    );
}

export default OnboardingFlow;