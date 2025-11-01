// /send_me_mvp/frontend/src/components/ChatInterface.jsx
import React, { useState, useContext } from 'react';
import useApi from '../hooks/useApi';
import { UserContext } from '../App';
import { useNavigate } from 'react-router-dom';

function ChatInterface() {
    const { user } = useContext(UserContext);
    const { loading, error, callApi } = useApi();
    const navigate = useNavigate();

    // מצבים לשלבים השונים
    const [step, setStep] = useState(0); // 0: קלט מודעה, 1: עריכת טקסט, 2: סיום
    const [adContent, setAdContent] = useState('');
    const [contentType, setContentType] = useState('text');
    const [jobData, setJobData] = useState(null); // JobData מה-Backend
    const [generatedParagraph, setGeneratedParagraph] = useState('');
    const [finalSubmissionText, setFinalSubmissionText] = useState('');

    const handleIngest = async (e) => {
        e.preventDefault();
        if (!adContent) return alert("אנא הכנס תוכן מודעה.");
        
        try {
            const response = await callApi('post', '/chat/ingest', {
                user_id: user.user_id,
                content: adContent,
                content_type: contentType
            });
            
            setJobData(response);
            setStep(1); // מעבר לשלב גנרציה
            
            // גנרציה אוטומטית של פסקה לאחר האינג'סט
            const paragraphResponse = await callApi('post', '/chat/generate/paragraph', response, {
                'X-User-ID': user.user_id // העברת user_id ב-Header (אלגנטי יותר)
            });
            
            setGeneratedParagraph(paragraphResponse.paragraph);
            setFinalSubmissionText(paragraphResponse.paragraph);

        } catch (e) {
            console.error("שגיאת קליטת מודעה:", e);
        }
    };
    
    const handleSubmitEmail = async () => {
        if (!jobData || !finalSubmissionText) return alert("חסר טקסט או נתוני משרה.");
        
        try {
            // ה-submission_id יגיע מ-jobData (אחרי שה-DB יצר אותו) - נשתמש ב-UUID מדומה לצורך MVP
            const mockSubmissionId = "mock-uuid-12345"; 

            await callApi('post', '/chat/submit/email', null, {
                'X-User-ID': user.user_id,
                'Content-Type': 'application/x-www-form-urlencoded' // נדרש ל-Form data
            });

            // במקום Form data, נשתמש ב-api instance לטובת FormData:
            const formData = new FormData();
            formData.append('submission_id', mockSubmissionId); 
            formData.append('final_text', finalSubmissionText); 
            formData.append('user_id', user.user_id); 

             await api.post('/chat/submit/email', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            alert("המייל נשלח בהצלחה!");
            setStep(2); // מעבר לסיום
            
        } catch (e) {
             alert(error || "שגיאה בשליחת המייל.");
        }
    };

    // --- שלב 0: קלט מודעה ---
    if (step === 0) {
        return (
            <div className="screen-container chat-interface">
                <h2>הגשת מועמדות חדשה</h2>
                <form onSubmit={handleIngest}>
                    <label>
                        <input
                            type="radio"
                            value="text"
                            checked={contentType === 'text'}
                            onChange={() => setContentType('text')}
                        /> טקסט גולמי
                    </label>
                    <label style={{ marginRight: '15px' }}>
                        <input
                            type="radio"
                            value="image_url"
                            checked={contentType === 'image_url'}
                            onChange={() => setContentType('image_url')}
                        /> קישור לתמונה
                    </label>

                    <textarea
                        rows="6"
                        placeholder={contentType === 'text' ? "הדבק את טקסט המודעה..." : "הדבק URL של תמונת מודעה..."}
                        value={adContent}
                        onChange={(e) => setAdContent(e.target.value)}
                        required
                    />

                    <button type="submit" disabled={loading}>
                        {loading ? 'מפרק מודעה...' : 'בצע ניתוח מודעה'}
                    </button>
                    {error && <div className="error">{error}</div>}
                </form>
            </div>
        );
    }
    
    // --- שלב 1: עריכת פסקה ושליחה ---
    if (step === 1) {
        return (
            <div className="screen-container chat-edit">
                <h2>עריכת טקסט הגשה</h2>
                <p>ה-AI יצר פסקה מותאמת אישית: {jobData.job_title} ({jobData.target_email})</p>
                <div style={{ border: '1px dashed #4CAF50', padding: '15px', marginBottom: '20px' }}>
                    <p><strong>דרישות המשרה:</strong> {jobData.requirements.join(', ')}</p>
                </div>

                <label htmlFor="submissionText">ערוך את טקסט הפתיחה של המייל:</label>
                <textarea
                    id="submissionText"
                    rows="8"
                    value={finalSubmissionText}
                    onChange={(e) => setFinalSubmissionText(e.target.value)}
                    dir="rtl"
                />
                
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
                    <button onClick={() => setStep(0)} style={{ backgroundColor: '#aaa' }}>חזור</button>
                    <button onClick={handleSubmitEmail} disabled={loading || !finalSubmissionText}>
                        {loading ? 'שולח...' : 'שלח מייל'}
                    </button>
                </div>
                {error && <div className="error">{error}</div>}
            </div>
        );
    }

    // --- שלב 2: סיום ---
    return (
        <div className="screen-container">
            <h2>🎉 ההגשה נשלחה!</h2>
            <p>המועמדות נשלחה בהצלחה ל-**{jobData.target_email}**.</p>
            <button onClick={() => navigate('/history')}>צפה בהיסטוריה</button>
            <button onClick={() => setStep(0)} style={{ backgroundColor: '#aaa', marginRight: '10px' }}>הגשה חדשה</button>
        </div>
    )
}

export default ChatInterface;