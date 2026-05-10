import pandas as pd
import numpy as np

def color_row(row):
    """פונקציית הצביעה המגדירה את צבעי הרקע לפי דרישות המטלה"""
    vote = row.get('vote')
    label = row.get('label')
    
    # טיפול ברשומות ללא תגית (unlabeled מברקלי)
    if pd.isna(label):
        if vote == 1:
            return ['background-color:#FF4444;color:white'] * len(row)
        return [''] * len(row)
        
    # ספאם אמיתי שזוהה כספאם -> אדום
    if vote == 1 and label == 1:
        return ['background-color:#FF4444;color:white'] * len(row)
    # מייל תקין שסווג בטעות כספאם (False Positive) -> כתום
    elif vote == 1 and label == 0:
        return ['background-color:#FFA500;color:white'] * len(row)
        
    return [''] * len(row)

def main():
    print("Loading data files for HTML report generation...")

    # הגדרות תצוגה כלליות המונעות חיתוך ב-DataFrame הרגיל
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    
    # הגדרות ספציפיות לאובייקט ה-Styler המונעות חיתוך שורות ועמודות
    pd.set_option('styler.render.max_rows', None)
    pd.set_option('styler.render.max_columns', None)
    
    # === התיקון הבטוח: שימוש במספר שלם עצום (מיליארד) במקום None ===
    pd.set_option('styler.render.max_elements', 999999999)
    # =================================================================

    try:
        master = pd.read_csv('emails_master.csv')
        cons = pd.read_csv('consumer_log.csv')
    except FileNotFoundError as e:
        print(f"Error: Could not find required CSV files. {e}")
        return

    # המרת עמודת הביטחון למספר עשרוני לצורך פירמוט תקין באחוזים
    cons['confidence'] = cons['confidence'].astype(float)

    # מיזוג טבלת המקור עם תוצאות הצרכן
    merged = master.merge(
        cons[['record_id', 'vote', 'confidence', 'logistic', 'svm', 'rf']],
        on='record_id', 
        how='left'
    )

    # --- חישוב נתונים סטטיסטיים מדויקים עבור קובץ ה-README ---
    labeled_df = merged[merged['label'].notna()]
    total_fps = labeled_df[(labeled_df['vote'] == 1) & (labeled_df['label'] == 0)]
    
    log_fps = len(labeled_df[(labeled_df['logistic'] == 1) & (labeled_df['label'] == 0)])
    svm_fps = len(labeled_df[(labeled_df['svm'] == 1) & (labeled_df['label'] == 0)])
    rf_fps = len(labeled_df[(labeled_df['rf'] == 1) & (labeled_df['label'] == 0)])
    
    print("\n" + "="*60)
    print("📊 נתונים סטטיסטיים מדויקים לניתוח ב-README.md:")
    print(f"סה\"כ טעויות False Positive במערכת (הצבעת רוב): {len(total_fps)}")
    print(f"  - טעויות False Positive של Logistic Regression: {log_fps}")
    print(f"  - טעויות False Positive של SVM: {svm_fps}")
    print(f"  - טעויות False Positive של Random Forest: {rf_fps}")
    print("="*60 + "\n")

    # סידור העמודות כך שעמודות הסיווג והתוצאה יופיעו בהתחלה ויהיו נוחות לקריאה
    all_cols = list(merged.columns)
    first_cols = ['record_id', 'source', 'label', 'vote', 'confidence', 'logistic', 'svm', 'rf']
    remaining_cols = [c for c in all_cols if c not in first_cols]
    display_df = merged[first_cols + remaining_cols]

    print("Generating full_report.html (Applying colors: Red=SPAM, Orange=FP)...")
    
    # יצירת אובייקט העיצוב (Styler) ופירמוט אחוזים
    styled = (display_df.style
              .apply(color_row, axis=1)
              .format({'confidence': '{:.1%}'}, na_rep='N/A'))
              
    # קריאה נקייה ובטוחה לייצוא הקובץ המלא ללא שום חיתוך
    styled.to_html('full_report.html')

    print("✅ Successfully generated 'full_report.html'!")
    print("ניתן לפתוח את הקובץ בדפדפן ולצפות בטבלה הצבעונית המלאה.")

if __name__ == '__main__':
    main()