# Dockerfile מתוקן עבור Frontend על Cloud Run

# שלב 1: בנייה
FROM node:20-alpine as builder
WORKDIR /app

# העתקת package files
COPY package*.json ./

# התקנת dependencies
RUN npm ci

# העתקת כל הקבצים
COPY . .

# בנייה עם משתנה סביבה לנתיב ה-Backend
# חשוב: השתמש ב-URL הציבורי של ה-Backend Service ב-Cloud Run
ARG VITE_BACKEND_URL=https://sendmebackend-893805209951.us-central1.run.app
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# בניית האפליקציה
RUN npm run build

# שלב 2: הרצה עם Nginx
FROM nginx:alpine

# העתקת קובץ nginx config מותאם ל-Cloud Run
COPY nginx.conf /etc/nginx/conf.d/default.conf

# העתקת הקבצים הבנויים
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run משתמש בפורט 8080 כברירת מחדל
EXPOSE 8080

# הפעלת nginx
CMD ["nginx", "-g", "daemon off;"]
