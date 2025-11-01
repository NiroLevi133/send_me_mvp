// /send_me_mvp/frontend/src/components/AuthScreen.jsx
import React, { useState, useContext } from 'react';
import useApi from '../hooks/useApi';
import { UserContext } from '../App';

function AuthScreen() {
    const [phoneNumber, setPhoneNumber] = useState('');
    const { loginUser } = useContext(UserContext);
    const { loading, error, callApi } = useApi();

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!phoneNumber) {
            alert("אנא הכנס מספר טלפון.");
            return;
        }

        try {
            // קריאה ל-Backend API
            const response = await callApi('post', '/auth/phone', { 
                phone_number: phoneNumber 
            });

            // שמירת נתוני המשתמש הגלובליים
            loginUser(response.user);

            // הודעה לפי סוג המשתמש
            const msg = response.is_new_user 
                ? "ברוך הבא! אנא המשך לאונבורדינג." 
                : "שלום שוב! טוען את הפרופיל שלך.";
            
            console.log(msg);

        } catch (e) {
            // השגיאה נשלטת על ידי useApi
            console.error("שגיאת אימות:", error);
        }
    };

    return (
        <div className="screen-container auth-screen">
            <h2>כניסה / הרשמה</h2>
            <p>הכנס את מספר הטלפון שלך כדי להתחיל:</p>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="דוגמה: 05X-XXXXXXX"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    dir="ltr" 
                    required
                />
                
                {error && <div className="error">{error}</div>}
                
                <button type="submit" disabled={loading}>
                    {loading ? 'טוען...' : 'כניסה'}
                </button>
            </form>
        </div>
    );
}

export default AuthScreen;