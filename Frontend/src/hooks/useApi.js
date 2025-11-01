// /send_me_mvp/frontend/src/hooks/useApi.js
import { useState, useCallback, useMemo } from 'react';
import axios from 'axios';

// קריאת משתנה הסביבה שהוגדר ב-vite.config.js וב-docker-compose
const API_BASE_URL = process.env.VITE_BACKEND_URL; 

/**
 * Hook מותאם אישית לטיפול ב-API Calls.
 * מטפל ב-Loading State, שגיאות, ומשתמש ב-Axios.
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // יצירת מופע Axios
  const api = useMemo(() => axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
      'Content-Type': 'application/json',
    },
  }), []);

  /**
   * פונקציה גנרית לביצוע קריאות API.
   * @param {string} method - 'get', 'post', 'put'
   * @param {string} url - ה-endpoint (לדוגמה: '/auth/phone')
   * @param {object} data - גוף הבקשה
   */
  const callApi = useCallback(async (method, url, data = null, customHeaders = {}) => {
    setLoading(true);
    setError(null);

    try {
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
      const errorMessage = err.response?.data?.detail || err.message || "שגיאה לא ידועה";
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
  };
};

export default useApi;