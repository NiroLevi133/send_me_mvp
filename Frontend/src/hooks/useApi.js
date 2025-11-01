// /send_me_mvp/frontend/src/hooks/useApi.js
import { useState, useCallback, useMemo } from 'react';
import axios from 'axios';

// קריאת משתנה הסביבה או שימוש ב-URL של ה-Backend Service
// חשוב: ב-Production, השתמש ב-URL המלא של ה-Backend Service
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'https://sendmebackend-893805209951.us-central1.run.app';

console.log('API Base URL:', API_BASE_URL); // לצורך debug

/**
 * Hook מותאם אישית לטיפול ב-API Calls.
 * מטפל ב-Loading State, שגיאות, ומשתמש ב-Axios.
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // יצירת מופע Axios
  const api = useMemo(() => {
    const instance = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds timeout
    });

    // Interceptor לטיפול בשגיאות
    instance.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        if (error.response) {
          // השרת החזיר תגובה עם קוד שגיאה
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        } else if (error.request) {
          // הבקשה נשלחה אבל לא התקבלה תגובה
          console.error('No response received:', error.request);
        } else {
          // משהו אחר קרה
          console.error('Error message:', error.message);
        }
        return Promise.reject(error);
      }
    );

    return instance;
  }, []);

  /**
   * פונקציה גנרית לביצוע קריאות API.
   * @param {string} method - 'get', 'post', 'put'
   * @param {string} url - ה-endpoint (לדוגמה: '/auth/phone')
   * @param {object} data - גוף הבקשה
   * @param {object} customHeaders - headers נוספים
   */
  const callApi = useCallback(async (method, url, data = null, customHeaders = {}) => {
    setLoading(true);
    setError(null);

    try {
      console.log(`Making ${method.toUpperCase()} request to: ${url}`);
      
      const response = await api({
        method: method.toLowerCase(),
        url,
        data: data,
        headers: customHeaders,
      });
      
      setLoading(false);
      return response.data;
    } catch (err) {
      setLoading(false);
      
      let errorMessage = "שגיאה לא ידועה";
      
      if (err.response) {
        // השרת החזיר שגיאה
        errorMessage = err.response.data?.detail || err.response.data?.message || `שגיאת שרת: ${err.response.status}`;
      } else if (err.request) {
        // הבקשה נשלחה אך לא התקבלה תגובה
        errorMessage = "אין תגובה מהשרת. ייתכן שיש בעיית חיבור.";
      } else {
        // שגיאה אחרת
        errorMessage = err.message || "שגיאה בביצוע הבקשה";
      }
      
      setError(errorMessage);
      console.error(`API Error on ${url}:`, errorMessage);
      throw err; // זורק את השגיאה הלאה לטיפול בקומפוננטה
    }
  }, [api]);

  return {
    loading,
    error,
    callApi,
    api, // חשוף את Axios Instance עבור טיפול מורכב (כמו העלאת קבצים)
    apiBaseUrl: API_BASE_URL // חשוף את ה-URL לצורך debug
  };
};

export default useApi;