# Real time spam filter - targil 5
 ## 1. פרטי הקבוצה:

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

 פלט צפוי: יצירת קובץ אחיד בשם emails_master.csv המכיל בדיוק 12,949 רשומות ו-60 עמודות (מזהה ייחודי, 57 תכונות, תגית ומקור).
 
  2. **אימון שלושת המסווגים (Offline Training):**
    ```bash
    python train_models.py

פלט צפוי: טעינת הרשומות המסומנות מתוך קובץ המאסטר, ביצוע פיצול מרובד (Stratified Split) ל-70% אימון ו-30% בדיקה, נרמול התכונות בעזרת StandardScaler, ושמירת ארבעה קבצי אובייקט מחושבים בפורמט Pickle:

* אובייקט המנרמל: scaler.pkl

* ממודל רגרסיה לוגיסטית: model_logistic.pkl

* מודל מכונות וקטורים תומכים: model_svm.pkl

* מודל יער אקראי: model_rf.pkl
  
בנוסף, הסקריפט מדפיס למסך את דוחות הסיווג (Classification Reports) ואת טבלת מדדי הביצועים להשוואה.

  3. **הפעלת תשתית זרימת הנתונים (Apache Kafka):**
      
 בסביבת Windows, יש לפתוח שלושה חלונות שורת פקודה (CMD) נפרדים, לנווט בכולם לתיקיית ההתקנה של Kafka (לדוגמה C:\kafka), ולהריץ את הפקודות הבאות לפי 
 הסדר:
 1. חלון 1 (הפעלת שרת Zookeeper):
 
`.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties`

 2. חלון 2 (הפעלת שרת Kafka Broker):
 
`.\bin\windows\kafka-server-start.bat .\config\server.properties`

3.  חלון 3 (יצירת נושא ההזרמה עם 3 מחיצות):

`.\bin\windows\kafka-topics.bat --create --topic email-stream --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1`

 (יש לוודא קבלת פלט הצלחה: Created topic email-stream.)

4. **הזרמה וסיווג בזמן אמת (Online Real-Time Processing):**

יש לפתוח שני מסופי פייתון במקביל בתיקיית הפרויקט (למשל באמצעות פיצול מסופים ב-VS Code):

*במסוף הראשון, מפעילים את הצרכן (Consumer) המאזין בזמן אמת:
`python consumer.py`

*במסוף השני, מפעילים את היצרן (Producer) המשדר את הודעות הדוא"ל:
`python producer.py`
היצרן קורא את emails_master.csv שורה אחר שורה, מנתב כל הודעה למחיצה (Partition) המתאימה לפי המקור (0 ל-UCI, 1 ל-Berkeley, 2 לבלתי מסומנות), ומשדר בהשהיה של 50 מילישניות בין הודעה להודעה.

**סיום ההרצה:** לאחר שהיצרן מסיים לשדר את כל 12,949 ההודעות וכותב את הלוג console.producer.txt, יש לגשת לחלון הצרכן וללחוץ על השילוב Ctrl + C. לחיצה זו תסיים את תהליך ההאזנה בצורה בטוחה, תסגור את קבצי הפלט (console.consumer.txt, alerts.txt, consumer_log.csv) ותדפיס למסך את סיכום סטטיסטיקות זמני התגובה.
