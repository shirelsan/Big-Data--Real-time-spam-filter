import csv
import json
import time
import datetime
from kafka import KafkaProducer

def main():
    print("Initializing Kafka Producer...")
    # הגדרת היצרן עם קידוד JSON
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    input_file = 'emails_master.csv'
    output_log = 'console.producer.txt'
    
    print(f"Reading from {input_file} and streaming to 'email-stream' topic...")
    
    with open(output_log, 'w', encoding='utf-8') as log_file:
        # כתיבת כותרות הלוג בדיוק לפי דרישת המטלה
        log_file.write("record_id,timestamp_sent,true_label,source\n")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                # לקיחת זמן שליחה מדויק
                t1 = datetime.datetime.now().isoformat()
                
                # הרכבת ההודעה
                msg = {**row, 'timestamp_sent': t1}
                
                # ניתוב למחיצות (Partitions) לפי המקור
                partition = {'uci': 0, 'berkeley': 1}.get(row.get('source'), 2)
                
                # שליחה ל-Kafka
                producer.send('email-stream', value=msg, partition=partition)
                
                # כתיבה ללוג המקומי
                true_label = row.get('label', '')
                if true_label == '':
                    true_label = '?'
                    
                log_file.write(f"{row['record_id']},{t1},{true_label},{row.get('source', '')}\n")
                
                count += 1
                # השהיה של 50 מילישניות בין הודעה להודעה (לפי ההנחיות)
                time.sleep(0.05)
                
                if count % 500 == 0:
                    print(f"Sent {count} messages...")
                    producer.flush()
                    
            producer.flush()
            print(f"\nFinished streaming {count} messages successfully!")
            print(f"Producer log saved to {output_log}.")

if __name__ == '__main__':
    main()