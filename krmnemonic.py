#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
import pandas as pd
import numpy as np
import os
import json
import argparse
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
IMPORTS = os.path.join(DIR, "imports")
EXPORTS = os.path.join(DIR, "exports")
EXPORT_FILE_PD = os.path.join(EXPORTS, "korean_mnemonics.csv")

class KoreanMnemonicsManager:
    def __init__(self, csv_path=EXPORT_FILE_PD):
        self.csv_path = csv_path
        self.columns = ['Korean Word', 'Romanization', 'Meaning', 'Mnemonic', 'Visual', 'Notes', 'Timestamp']
        self.df = self._load_or_create_dataframe()
        self.df = self.df.sort_values(by='Timestamp', ascending=True) # Most recent at the end

    def _load_or_create_dataframe(self):
        if os.path.exists(self.csv_path):
            return pd.read_csv(self.csv_path)
        else:
            return pd.DataFrame(columns=self.columns)

    def add_mnemonic(self, korean_word, romanization, meaning, mnemonic, visual, notes, timestamp):
        if self._is_duplicate(korean_word, meaning):
            print(f"'{korean_word}' already exists. Skipping.")
            return False
        new_entry = pd.DataFrame([[korean_word, romanization, meaning, mnemonic, visual, notes if notes else '', timestamp]], columns=self.columns)
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self._save_dataframe()
        print(f"Added: {korean_word}")
        return True

    def bulk_add_from_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        timestamp = data['timestamp']
        mnemonics = data['mnemonics']
        for entry in mnemonics:
            self.add_mnemonic(**entry, timestamp=timestamp)

    def _is_duplicate(self, korean_word, meaning):
        return len(self.df[(self.df['Korean Word'] == korean_word) & (self.df['Meaning'] == meaning)]) > 0

    def _save_dataframe(self):
        self.df.to_csv(self.csv_path, index=False)
    
    def get_recent(self, n: int = 5):
        recent = self.df.tail(n)
        for index, row in recent.iterrows():
            self.recall_mnemonic(row['Korean Word'])

    def export_to_anki_csv(self, anki_csv_path='exports/anki.csv', reverse=False):
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
                "Romanization: " + anki_df['Romanization'] + "\n\n" +
                "Meaning: " + anki_df['Meaning'] + "\n\n" +
                "Mnemonic: " + anki_df['Mnemonic'] + "\n\n" +
                "Visual: " + anki_df['Visual'] + "\n\n" +
                "Notes: " + anki_df['Notes']
            )
        anki_df = anki_df[['Front', 'Back']]
        anki_df.to_csv(anki_csv_path, index=False, header=False)
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
    
    def get_stats(self):
        """Print comprehensive statistics about the mnemonics collection."""
        total_mnemonics = len(self.df)
        unique_korean_words = self.df['Korean Word'].nunique()
        unique_english_meanings = self.df['Meaning'].nunique()
        missing_notes = self.df['Notes'].isna().sum()

        # Initialize stats
        num_study_sessions = 0
        most_recent_date = "N/A"
        std_learning_times = "N/A"
        frequency_per_day = "N/A"
        frequency_per_session = "N/A"
        avg_learning_gap = "N/A"
        top_5_korean_words = "N/A"
        top_5_english_meanings = "N/A"
        learning_trend = "N/A"

        timestamps = self.df['Timestamp'].dropna()
        if not timestamps.empty:
            study_session_timestamps = np.sort(np.unique(timestamps))
            num_study_sessions = len(study_session_timestamps)
            most_recent_timestamp = study_session_timestamps.max()
            oldest_timestamp = study_session_timestamps.min()
            most_recent_date = datetime.fromtimestamp(most_recent_timestamp).strftime('%B %d, %Y at %I:%M:%S %p')

            # Convert timestamps to days since the first entry
            learning_times_days = [(ts - oldest_timestamp) / 86400 for ts in study_session_timestamps]

            # Standard deviation of learning times
            std_learning_times = f"{np.std(learning_times_days):.2f} days"

            # Frequency of added words (words per day)
            total_days = (most_recent_timestamp - oldest_timestamp) / 86400
            frequency_per_day = f"{total_mnemonics / total_days:.2f} words/day" if total_days > 0 else "N/A"
            frequency_per_session = f"{total_mnemonics / num_study_sessions:.2f} words/session" if num_study_sessions > 0 else "N/A"

            # Average gap between learning new words
            avg_time_diff_between_study_session = np.average(np.diff(study_session_timestamps / 86400))

            # Learning trend (words added per week)
            self.df['date'] = pd.to_datetime(self.df['Timestamp'], unit='s')
            words_per_week = self.df.set_index('date').resample('W').size()
            learning_trend = words_per_week.mean()

        stats_str = (
            f"Total Mnemonics: {total_mnemonics}\n"
            f"Korean Words: {unique_korean_words}\n"
            f"English Meanings: {unique_english_meanings}\n"
            f"Number of study sessions: {num_study_sessions}\n"
            f"Average days between consecutive study sessions: {avg_time_diff_between_study_session} Days\n"
            f"Most Recent Date: {most_recent_date}\n"
            f"Standard Deviation of Learning Times: {std_learning_times}\n"
            f"Frequency of Added Words: {frequency_per_day} | {frequency_per_session}\n"
            f"Average Words Added Per Week: {learning_trend:.2f}\n"
        )
        print(stats_str)

        return
        """Print statistics about the mnemonics collection."""
        total_mnemonics = len(self.df)
        unique_korean_words = self.df['Korean Word'].nunique()
        unique_english_meanings = self.df['Meaning'].nunique()
        missing_notes = self.df['Notes'].isna().sum()
        most_recent_timestamp = self.df['Timestamp'].max()
        oldest_timestamp = self.df['Timestamp'].min()


        timestamps = self.df['Timestamp'].dropna()
        # Check if 'timestamp' column exists
        most_recent_date = "N/A"
        variance_learning_times = "N/A"
        frequency_per_day = "N/A"

        if not timestamps.empty:
            most_recent_date = datetime.fromtimestamp(most_recent_timestamp).strftime('%B %d, %Y at %I:%M:%S %p')

            # Variance of learning times (in days)
            learning_times_days = [(ts - oldest_timestamp) / 86400 for ts in timestamps]
            variance_learning_times = f"{np.std(learning_times_days):.2f} days"

            # Frequency of added words (words per day)
            total_days = (most_recent_timestamp - oldest_timestamp) / 86400
            frequency_per_day = f"{total_mnemonics / total_days:.2f} words/day" if total_days > 0 else "N/A"



        stats_str = (
            f"Total Mnemonics: {total_mnemonics}\n"
            f"Unique Korean Words: {unique_korean_words}\n"
            f"Unique English Meanings: {unique_english_meanings}\n"
            f"Missing Notes: {missing_notes}\n"
            f"Most Recent Date: {most_recent_date}\n"
            f"Variance of Learning Times: {variance_learning_times}\n"
            f"Frequency of Added Words: {frequency_per_day}"
        )

        print(stats_str)


    def show_all(self):
        print(self.df)

def main():
    # Prerequisites 
    if not os.path.isdir(EXPORTS):
        os.mkdir(EXPORTS)
    if not os.path.isdir(IMPORTS):
        os.mkdir(IMPORTS)
    
    parser = argparse.ArgumentParser(description="Manage Korean mnemonics.")
    parser.add_argument('--recall', help="Recall a mnemonic by Korean or English word.")
    parser.add_argument('--anki', action='store_true', help="Export to Anki CSV.")
    parser.add_argument('--english_first', action='store_true', help="Reverse card order (English → Korean).")
    parser.add_argument('--add', help="Import mnemonics from a JSON file.")
    parser.add_argument('--recent', type=int, help="Get the most recently added mnemonics", default=0)
    parser.add_argument('--stats', action='store_true', help="View stats on how many words you have learned and when.")
    args = parser.parse_args()

    manager = KoreanMnemonicsManager()

    if args.recall:
        manager.recall_mnemonic(args.recall)
    if args.anki:
        manager.export_to_anki_csv(reverse=args.english_first)
    if args.add:
        manager.bulk_add_from_json(args.add)
    if args.recent:
        manager.get_recent(args.recent)
    if args.stats:
        manager.get_stats()

if __name__ == "__main__":
    main()
