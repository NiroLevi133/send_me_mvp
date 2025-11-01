// /send_me_mvp/frontend/vite.config.js
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// משתמשים בפונקציה כדי שנוכל לטעון את משתני הסביבה
export default defineConfig(({ mode }) => {
  // טעינת משתני הסביבה הרלוונטיים (כמו VITE_BACKEND_URL)
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      // הגדרת פורט פיתוח מקומי
      port: 3000,
      host: true
    },
    define: {
      // חשיפת משתני הסביבה שנקבעו ב-docker-compose
      'process.env.VITE_BACKEND_URL': JSON.stringify(env.VITE_BACKEND_URL),
    }
  }
});