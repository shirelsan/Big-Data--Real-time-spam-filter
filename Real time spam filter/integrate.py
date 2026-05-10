import os
import re
import pandas as pd
import numpy as np
from ucimlrepo import fetch_ucirepo

def get_uci_feature_names():
    """Returns the exact 57 feature names defined by the UCI Spambase schema."""
    words = [
        'make', 'address', 'all', '3d', 'our', 'over', 'remove', 'internet',
        'order', 'mail', 'receive', 'will', 'people', 'report', 'addresses',
        'free', 'business', 'email', 'you', 'credit', 'your', 'font', '000',
        'money', 'hp', 'hpl', 'george', '650', 'lab', 'labs', 'telnet', '857',
        'data', '415', '85', 'technology', '1999', 'parts', 'pm', 'direct',
        'cs', 'meeting', 'original', 'project', 're', 'edu', 'table', 'conference'
    ]
    chars = [';', '(', '[', '!', '$', '#']
    
    feature_names = [f"word_freq_{w}" for w in words]
    feature_names += [f"char_freq_{c}" for c in chars]
    feature_names += [
        "capital_run_length_average",
        "capital_run_length_longest",
        "capital_run_length_total"
    ]
    return feature_names, words, chars

def extract_features_from_text(text, words, chars):
    """Extracts the 57 UCI schema features from a raw text email."""
    if not isinstance(text, str):
        text = ""
        
    features = []
    total_words = len(re.findall(r'\b\w+\b', text))
    total_chars = len(text)
    
    text_lower = text.lower()
    for w in words:
        if total_words > 0:
            count = len(re.findall(r'\b' + re.escape(w) + r'\b', text_lower))
            freq = (count / total_words) * 100.0
        else:
            freq = 0.0
        features.append(freq)
        
    for c in chars:
        if total_chars > 0:
            count = text.count(c)
            freq = (count / total_chars) * 100.0
        else:
            freq = 0.0
        features.append(freq)
        
    cap_runs = re.findall(r'[A-Z]+', text)
    if cap_runs:
        run_lengths = [len(r) for r in cap_runs]
        features.append(np.mean(run_lengths))
        features.append(max(run_lengths))
        features.append(sum(run_lengths))
    else:
        features.append(0.0)
        features.append(0.0)
        features.append(0.0)
        
    return features

def main():
    print("Fetching UCI Spambase dataset...")
    spambase = fetch_ucirepo(id=94)
    uci_df = pd.concat([spambase.data.features, spambase.data.targets], axis=1)
    uci_df['source'] = 'uci'
    
    feature_names, words, chars = get_uci_feature_names()
    rename_map = dict(zip(uci_df.columns[:-2], feature_names))
    uci_df = uci_df.rename(columns=rename_map).rename(columns={'Class': 'label'})
    print(f"UCI dataset fetched: {len(uci_df)} records.")

    # Processing DATA100 (Berkeley) directly from train.csv
    berkeley_csv = 'train.csv'
    print(f"Processing Berkeley dataset from {berkeley_csv}...")
    
    records = []
    if os.path.exists(berkeley_csv):
        b_df = pd.read_csv(berkeley_csv)
        # Combine subject and email body if both exist
        for idx, row in b_df.iterrows():
            subj = str(row['subject']) if pd.notna(row['subject']) else ""
            body = str(row['email']) if pd.notna(row['email']) else ""
            full_text = subj + " " + body
            
            feats = extract_features_from_text(full_text, words, chars)
            rec = dict(zip(feature_names, feats))
            rec['label'] = int(row['spam']) if pd.notna(row['spam']) else None
            rec['source'] = 'berkeley'
            records.append(rec)
            
        berkeley_df = pd.DataFrame(records)
        print(f"Berkeley dataset processed: {len(berkeley_df)} records.")
    else:
        print(f"Warning: {berkeley_csv} not found. Please place it in the directory.")
        berkeley_df = pd.DataFrame(columns=feature_names + ['label', 'source'])

    master_df = pd.concat([uci_df, berkeley_df], ignore_index=True)
    master_df.insert(0, 'record_id', [f"REC_{i}" for i in range(len(master_df))])
    
    master_df.to_csv('emails_master.csv', index=False)
    print(f"\nIntegration complete! Saved to emails_master.csv. Total rows: {len(master_df)}")

if __name__ == '__main__':
    main()