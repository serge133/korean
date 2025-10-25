#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
import pandas as pd
import os
import json
import argparse

class KoreanMnemonicsManager:
    def __init__(self, csv_path='exports/korean_mnemonics.csv'):
        self.csv_path = csv_path
        self.columns = ['Korean Word', 'Romanization', 'Meaning', 'Mnemonic', 'Visual', 'Notes']
        self.df = self._load_or_create_dataframe()

    def _load_or_create_dataframe(self):
        if os.path.exists(self.csv_path):
            return pd.read_csv(self.csv_path)
        else:
            return pd.DataFrame(columns=self.columns)

    def add_mnemonic(self, korean_word, romanization, meaning, mnemonic, visual, notes):
        if self._is_duplicate(korean_word):
            print(f"'{korean_word}' already exists. Skipping.")
            return False
        new_entry = pd.DataFrame([[korean_word, romanization, meaning, mnemonic, visual, notes if notes else '']], columns=self.columns)
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self._save_dataframe()
        print(f"Added: {korean_word}")
        return True

    def bulk_add_from_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for entry in data:
            self.add_mnemonic(**entry)

    def bulk_add_from_csv(self, csv_path):
        new_data = pd.read_csv(csv_path)
        for _, row in new_data.iterrows():
            self.add_mnemonic(**row.to_dict())

    def _is_duplicate(self, korean_word):
        return korean_word in self.df['Korean Word'].values

    def _save_dataframe(self):
        self.df.to_csv(self.csv_path, index=False)

    def export_to_anki_csv(self, anki_csv_path='korean_mnemonics_for_anki.csv', reverse=False):
        # Make a copy of the DataFrame and fill NaN values with empty strings
        anki_df = self.df.copy().fillna('')
        if reverse:
            anki_df['Front'] = anki_df['Meaning']
            anki_df['Back'] = (
                "Korean: " + anki_df['Korean Word'] + " (" + anki_df['Romanization'] + ")\n\n" +
                "Mnemonic: " + anki_df['Mnemonic'] + "\n\n" +
                "Visual: " + anki_df['Visual'] + "\n\n" +
                "Notes: " + anki_df['Notes']
            )
        else:
            anki_df['Front'] = anki_df['Korean Word']
            anki_df['Back'] = (
                "Romanization" + anki_df['Romanization'] + "\n\n",
                "Meaning: " + anki_df['Meaning'] + "\n\n" +
                "Mnemonic: " + anki_df['Mnemonic'] + "\n\n" +
                "Visual: " + anki_df['Visual'] + "\n\n" +
                "Notes: " + anki_df['Notes']
            )
        anki_df = anki_df[['Front', 'Back']]
        anki_df.to_csv(anki_csv_path, index=False)
        print(f"Exported to {anki_csv_path} {'(reversed)' if reverse else ''}.")

    def recall_mnemonic(self, word, case_sensitive=False):
        """
        Recall and print mnemonics matching the subtext in Korean or English.
        Set case_sensitive=True for case-sensitive matching.
        """
        korean_matches = self.df[self.df['Korean Word'].str.contains(word, case=case_sensitive, na=False)]
        english_matches = self.df[self.df['Meaning'].str.contains(word, case=case_sensitive, na=False)]

        if korean_matches.empty and english_matches.empty:
            print(f"No mnemonics found containing '{word}'.")
            return

        matches = pd.concat([korean_matches, english_matches]).drop_duplicates()

        for _, row in matches.iterrows():
            print(f"For '{row['Korean Word']} ({row['Romanization']})', the Korean word for '{row['Meaning']}', here’s a mnemonic:\n")
            print(f"'{row['Mnemonic']}'\n")
            print(f"{row['Visual']}\n")
            print(f"{row['Notes']}\n")

    def show_all(self):
        print(self.df)

def main():
    # Prerequisites 
    if not os.path.isdir("exports"):
        os.mkdir("exports")
    if not os.path.isdir("imports"):
        os.mkdir("imports")
    
    parser = argparse.ArgumentParser(description="Manage Korean mnemonics.")
    parser.add_argument('--recall', help="Recall a mnemonic by Korean or English word.")
    parser.add_argument('--export', action='store_true', help="Export to Anki CSV.")
    parser.add_argument('--english_first', action='store_true', help="Reverse card order (English → Korean).")
    parser.add_argument('--import_json', help="Import mnemonics from a JSON file.")
    parser.add_argument('--import_csv', help="Import mnemonics from a CSV file.")
    args = parser.parse_args()

    manager = KoreanMnemonicsManager()

    if args.recall:
        manager.recall_mnemonic(args.recall)
    if args.export:
        manager.export_to_anki_csv(reverse=args.english_first)
    if args.import_json:
        manager.bulk_add_from_json(args.import_json)
    if args.import_csv:
        manager.bulk_add_from_csv(args.import_csv)

if __name__ == "__main__":
    main()
