// /send_me_mvp/frontend/src/components/HistoryTable.jsx
import React, { useEffect, useState, useContext } from 'react';
import useApi from '../hooks/useApi';
import { UserContext } from '../App';

function HistoryTable() {
    const { user } = useContext(UserContext);
    const { loading, error, callApi } = useApi();
    const [submissions, setSubmissions] = useState([]);
    
    const fetchSubmissions = async () => {
        try {
            const response = await callApi('get', `/chat/submissions?user_id=${user.user_id}`);
            setSubmissions(response.submissions || []);
        } catch (e) {
            console.error("שגיאת טעינת היסטוריה:", e);
        }
    };
    
    useEffect(() => {
        if (user) {
            fetchSubmissions();
        }
    }, [user]);

    const formatStatus = (status) => {
        switch(status) {
            case 'sent': return <span style={{ color: 'green', fontWeight: 'bold' }}>נשלח</span>;
            case 'draft': return <span style={{ color: 'blue' }}>טיוטה</span>;
            case 'error': return <span style={{ color: 'red', fontWeight: 'bold' }}>כשלון</span>;
            default: return status;
        }
    }

    if (loading) return <div>טוען היסטוריית הגשות...</div>;
    if (error) return <div className="error">שגיאה בטעינת היסטוריה: {error}</div>;

    return (
        <div className="screen-container history-table">
            <h2>היסטוריית הגשות</h2>
            
            {submissions.length === 0 ? (
                <p>עדיין אין לך הגשות שמורות במערכת.</p>
            ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                    <thead>
                        <tr style={{ borderBottom: '2px solid #333' }}>
                            <th style={{ padding: '10px', textAlign: 'right' }}>תאריך</th>
                            <th style={{ padding: '10px', textAlign: 'right' }}>תפקיד</th>
                            <th style={{ padding: '10px', textAlign: 'right' }}>אימייל</th>
                            <th style={{ padding: '10px', textAlign: 'right' }}>סטטוס</th>
                        </tr>
                    </thead>
                    <tbody>
                        {submissions.map(sub => (
                            <tr key={sub.submission_id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '10px' }}>{new Date(sub.date_submitted).toLocaleDateString('he-IL')}</td>
                                <td style={{ padding: '10px' }}>{sub.job_title}</td>
                                <td style={{ padding: '10px' }}>{sub.target_email}</td>
                                <td style={{ padding: '10px' }}>{formatStatus(sub.status)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            <button onClick={fetchSubmissions} style={{ marginTop: '20px' }}>רענן</button>
        </div>
    );
}

export default HistoryTable;