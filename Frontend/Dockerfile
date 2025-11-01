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
# השורה הזו מתקנת את בעיית index.html
COPY public/index.html .

# הגדרה הכרחית לנתיב ה-API בזמן הבנייה
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

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