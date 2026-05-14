# Real time spam filter - targil 5
** ID1: 322328824 Student Name: Shirel Bodenheimer 
** ID2: [תעודת זהות 2] Student Name: Tehillah Ben David

** team: team-spam-fighters

** date: 14/05/2026

## 2. הוראות הפעלה ושחזור התרגיל
מערכת זו מממשת פייפליין מלא לזיהוי ספאם בזמן אמת באמצעות Apache Kafka ושלושה מסווגים הפועלים במקביל תחת מנגנון הצבעת רוב (Majority Vote).

### סדר הרצת הקבצים לשחזור מלא:
1. **הכנת סביבת העבודה והנתונים:**
   יש לוודא שקובץ `train.csv` (מתוך מערך הנתונים של Berkeley DS100) נמצא בתיקיית הפרויקט המקומית. לאחר מכן, יש לפתוח מסוף (Terminal) ולהריץ את סקריפט שילוב הנתונים:
   ```bash
   python integrate.py
