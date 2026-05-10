import json
import time
import datetime
import pickle
import numpy as np
import pandas as pd
from kafka import KafkaConsumer

def parse_iso_time(iso_str):
    """ממיר מחרוזת ISO לאובייקט datetime בצורה בטוחה"""
    if iso_str.endswith('Z'):
        iso_str = iso_str[:-1]
    return datetime.datetime.fromisoformat(iso_str)

def main():
    print("Loading models and scaler for real-time inference...")
    try:
        scaler = pickle.load(open('scaler.pkl', 'rb'))
        model_logistic = pickle.load(open('model_logistic.pkl', 'rb'))
        model_svm = pickle.load(open('model_svm.pkl', 'rb'))
        model_rf = pickle.load(open('model_rf.pkl', 'rb'))
    except Exception as e:
        print(f"Error loading pickle files: {e}")
        print("Please ensure train_models.py ran successfully.")
        return

    # רשימת 57 התכונות הנדרשות לשליפה מתוך ההודעה
    words = [
        'make', 'address', 'all', '3d', 'our', 'over', 'remove', 'internet',
        'order', 'mail', 'receive', 'will', 'people', 'report', 'addresses',
        'free', 'business', 'email', 'you', 'credit', 'your', 'font', '000',
        'money', 'hp', 'hpl', 'george', '650', 'lab', 'labs', 'telnet', '857',
        'data', '415', '85', 'technology', '1999', 'parts', 'pm', 'direct',
        'cs', 'meeting', 'original', 'project', 're', 'edu', 'table', 'conference'
    ]
    chars = [';', '(', '[', '!', '$', '#']
    
    feature_cols = [f"word_freq_{w}" for w in words] + [f"char_freq_{c}" for c in chars] + [
        "capital_run_length_average", "capital_run_length_longest", "capital_run_length_total"
    ]

    print("Connecting to Kafka Consumer...")
    consumer = KafkaConsumer(
        'email-stream',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    log_file_path = 'console.consumer.txt'
    alerts_file_path = 'alerts.txt'
    csv_log_path = 'consumer_log.csv' # עותק נוח לדוח ה-HTML
    
    f_log = open(log_file_path, 'w', encoding='utf-8')
    f_alerts = open(alerts_file_path, 'w', encoding='utf-8')
    f_csv = open(csv_log_path, 'w', encoding='utf-8')
    
    # כתיבת כותרות בדיוק לפי דרישת המטלה
    f_log.write("record_id,timestamp_received,logistic,svm,rf,vote,confidence,true_label\n")
    f_alerts.write("record_id,timestamp_alert,kafka_transit_ms,inference_ms,end2end_ms,confidence\n")
    f_csv.write("record_id,vote,confidence,logistic,svm,rf\n")

    print("\nListening for emails... (Press Ctrl+C to stop)")
    count = 0
    
    # רשימות לשמירת זמנים לצורך חישוב מדדי סיום
    transit_times, inference_times, e2e_times = [], [], []

    try:
        for message in consumer:
            # t2: זמן קבלה מדויק
            t2_dt = datetime.datetime.now()
            t2_iso = t2_dt.isoformat()
            
            msg = message.value
            record_id = msg.get('record_id', f'UNKNOWN_{count}')
            t1_iso = msg.get('timestamp_sent')
            true_label = msg.get('label', '')
            if true_label == '':
                true_label = '?'

            # 1. חישוב Kafka Transit Time (t2 - t1)
            t1_dt = parse_iso_time(t1_iso)
            kafka_transit_ms = (t2_dt - t1_dt).total_seconds() * 1000.0
            transit_times.append(kafka_transit_ms)

            # הכנת הנתונים למודל
            raw_features = [float(msg.get(col, 0.0)) for col in feature_cols]
            X_input = np.array(raw_features).reshape(1, -1)
            X_scaled = scaler.transform(X_input)

            # 2. הרצת המודלים ומדידת זמן חישוב (Inference)
            inf_start = time.time()
            
            pred_logistic = int(model_logistic.predict(X_scaled)[0])
            pred_svm = int(model_svm.predict(X_scaled)[0])
            pred_rf = int(model_rf.predict(X_scaled)[0])
            
            # שליפת הסתברויות לחישוב ביטחון (Confidence)
            prob_logistic = model_logistic.predict_proba(X_scaled)[0][1]
            prob_svm = model_svm.predict_proba(X_scaled)[0][1]
            prob_rf = model_rf.predict_proba(X_scaled)[0][1]
            
            inf_end = time.time()
            inference_ms = (inf_end - inf_start) * 1000.0
            inference_times.append(inference_ms)

            # הצבעת רוב וחישוב ביטחון ממוצע
            votes = pred_logistic + pred_svm + pred_rf
            vote = 1 if votes >= 2 else 0
            confidence = (prob_logistic + prob_svm + prob_rf) / 3.0

            # t3: זמן התראה/סיום
            t3_dt = datetime.datetime.now()
            t3_iso = t3_dt.isoformat()
            
            # 3. חישוב End-to-End Time (t3 - t1)
            end2end_ms = (t3_dt - t1_dt).total_seconds() * 1000.0
            e2e_times.append(end2end_ms)

            # כתיבה לקובץ הלוג המרכזי (console.consumer.txt)
            # פורמט ביטחון: 0.9712
            conf_str = f"{confidence:.4f}"
            f_log.write(f"{record_id},{t2_iso},{pred_logistic},{pred_svm},{pred_rf},{vote},{conf_str},{true_label}\n")
            f_csv.write(f"{record_id},{vote},{conf_str},{pred_logistic},{pred_svm},{pred_rf}\n")

            # כתיבה לקובץ ההתראות (alerts.txt) רק אם הוחלט שזה ספאם
            if vote == 1:
                f_alerts.write(f"{record_id},{t3_iso},{kafka_transit_ms:.2f},{inference_ms:.2f},{end2end_ms:.2f},{conf_str}\n")

            count += 1
            if count % 500 == 0:
                print(f"Processed {count} messages... Last E2E time: {end2end_ms:.2f}ms")
                f_log.flush()
                f_alerts.flush()
                f_csv.flush()

    except KeyboardInterrupt:
        print("\nStopping consumer processing...")

    finally:
        f_log.close()
        f_alerts.close()
        f_csv.close()
        
        # הדפסת מדדי זמנים מסכמים לתיעוד ב-README
        if len(transit_times) > 0:
            print("\n" + "="*50)
            print("סיכום מדדי זמני תגובה (במילישניות):")
            print("="*50)
            metrics = {
                'Kafka Transit': transit_times,
                'Inference': inference_times,
                'End-to-End': e2e_times
            }
            for name, values in metrics.items():
                print(f"--- {name} ---")
                print(f"  Minimum : {np.min(values):.2f} ms")
                print(f"  Median  : {np.median(values):.2f} ms")
                print(f"  p95     : {np.percentile(values, 95):.2f} ms")
                print(f"  Maximum : {np.max(values):.2f} ms")
            print("="*50)
            print(f"Output files generated: {log_file_path}, {alerts_file_path}")

if __name__ == '__main__':
    main()