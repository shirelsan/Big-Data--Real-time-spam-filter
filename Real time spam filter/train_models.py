import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import time

def main():
    print("Loading emails_master.csv...")
    try:
        master_df = pd.read_csv('emails_master.csv')
    except FileNotFoundError:
        print("Error: emails_master.csv not found. Please run integrate.py first.")
        return

    # סינון רשומות ללא תגית (מוודא שאנחנו מאמנים רק על מידע מסומן)
    trainable_df = master_df[master_df['label'].notna()].copy()
    print(f"Total labeled records available for training/testing: {len(trainable_df)}")

    # שליפת 57 עמודות התכונות בדיוק לפי הסכמה של UCI
    FEATURE_COLS = [c for c in master_df.columns if c.startswith(('word_freq_', 'char_freq_', 'capital_'))]
    
    X = trainable_df[FEATURE_COLS].values
    y = trainable_df['label'].values.astype(int)

    # פיצול ל-70% אימון ו-30% בדיקה (Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )
    print(f"Training set size: {len(X_train)} | Testing set size: {len(X_test)}")

    # נרמול הנתונים
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # שמירת המנרמל לקובץ pkl (קריטי לצרכן בזמן אמת)
    pickle.dump(scaler, open('scaler.pkl', 'wb'))
    print("Saved scaler to scaler.pkl")

    # הגדרת המודלים בדיוק לפי דרישות המטלה
    models = {
        'logistic': LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        'svm': SVC(kernel='rbf', C=1.0, probability=True, random_state=42),
        'rf': RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42)
    }

    results_table = []

    # אימון, מדידת זמנים, הערכה ושמירה
    for name, model in models.items():
        print(f"\nTraining {name.upper()}...")
        
        # מדידת זמן אימון
        start_time = time.time()
        model.fit(X_train_s, y_train)
        train_time = time.time() - start_time
        
        # חיזוי על סט הבדיקה
        y_pred = model.predict(X_test_s)
        
        # חישוב מדדים עבור מחלקת הספאם (1)
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, pos_label=1, average='binary')
        
        print(f"=== {name.upper()} RESULTS ===")
        print(classification_report(y_test, y_pred, target_names=['ham', 'spam']))
        
        # שמירת המודל לקובץ דחוס
        filename = f'model_{name}.pkl'
        pickle.dump(model, open(filename, 'wb'))
        print(f"Saved {name.upper()} to {filename}")
        
        # התאמת שמות לתצוגה בטבלה
        model_display_name = {
            'logistic': 'Logistic Regression',
            'svm': 'SVM (RBF)',
            'rf': 'Random Forest'
        }[name]
        
        # שמירת הנתונים לטבלה המסכמת
        results_table.append({
            'מסווג': model_display_name,
            'Accuracy': f"{acc:.4f}",
            'Precision (spam)': f"{precision:.4f}",
            'Recall (spam)': f"{recall:.4f}",
            'F1 (spam)': f"{f1:.4f}",
            'זמן אימון': f"{train_time:.2f}s"
        })

    # הדפסת הטבלה המסכמת להעתיק ל-README.md
    print("\n" + "="*80)
    print("טבלת השוואת מסווגים (להעתיק לקובץ README.md):")
    print("="*80)
    results_df = pd.DataFrame(results_table)
    # סידור העמודות בדיוק לפי המבוקש במטלה
    results_df = results_df[['מסווג', 'Accuracy', 'Precision (spam)', 'Recall (spam)', 'F1 (spam)', 'זמן אימון']]
    print(results_df.to_string(index=False))
    print("="*80)

if __name__ == '__main__':
    main()