# /send_me_mvp/frontend/Dockerfile.frontend

# ------------------------------------
# שלב 1: בנייה (Build Stage) - משתמש ב-Nodejs
# ------------------------------------
FROM node:20-alpine as builder
WORKDIR /app

# העתקת קבצי התלויות
COPY package*.json ./

# התקנת תלויות
RUN npm install

# העתקת קוד המקור והקונפיגורציה של Vite
COPY . .
# פקודת בניית הפרודקשן של Vite (יוצרת את תיקיית 'dist')
RUN npm run build

# ------------------------------------
# שלב 2: הרצה (Runtime Stage) - משתמש ב-Nginx קל
# ------------------------------------
FROM nginx:alpine

# העתקת קובץ קונפיגורציית Nginx שלנו
COPY nginx.conf /etc/nginx/conf.d/default.conf

# העתקת קבצי ה-Build מתיקיית 'dist' לתיקיית ההגשה של Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx מקשיב לפורט 80
EXPOSE 80