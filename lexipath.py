import os
from collections import Counter
from pathlib import Path
import re


class LexiPathEngine:

    def __init__(
        self, form_to_headword, headword_info=None, required_views=10
    ):
        """Initializes the engine with the BNC/COCA word family map.

        :param form_to_headword: Dict mapping word forms to headwords.
        :param headword_info: Optional dict mapping headwords to their metadata.
        :param required_views: Threshold 'n' for a word family to become
        implicitly learned.
        """
        self.form_to_headword = form_to_headword
        self.headword_info = headword_info if headword_info else {}
        self.required_views = required_views

        # Tracks headword (family) occurrences via incremental reading
        self.vocabulary_history = Counter()

        # Word families (headwords) explicitly or implicitly fully learned
        self.known_vocabulary = set()

    def _tokenize_to_headwords(self, text):
        """Helper method to convert raw text into a list of resolved headwords (in order)."""
        text = text.lower()
        words = re.findall(r"[\w\-\']+", text)
        return [self.form_to_headword.get(word, word) for word in words]

    def update_known_vocabulary(self):
        """Updates the master set of fully acquired word families based on thresholds."""
        implicit_learned = {
            headword
            for headword, count in self.vocabulary_history.items()
            if count >= self.required_views
        }
        self.known_vocabulary.update(implicit_learned)

    def read_text(self, text):
        """Simulates incremental reading: increments counts by 1 per word encounter.

        A family becomes mastered if total encounters >= required_views.
        """
        headwords = self._tokenize_to_headwords(text)
        self.vocabulary_history.update(headwords)
        self.update_known_vocabulary()

    def learn_text(self, text):
        """Forces immediate mastery of all word families present in the text.

        Bypasses the required_views threshold counter completely.
        """
        unique_headwords_in_text = set(self._tokenize_to_headwords(text))
        self.known_vocabulary.update(unique_headwords_in_text)

        # Sync history counter to match threshold requirement for consistency
        for headword in unique_headwords_in_text:
            if self.vocabulary_history[headword] < self.required_views:
                self.vocabulary_history[headword] = self.required_views

    def compute_known_percentage(self, text):
        """Computes the percentage of known words running through a text."""
        running_headwords = self._tokenize_to_headwords(text)
        if not running_headwords:
            return 0.0

        known_count = sum(
            1 for hw in running_headwords if hw in self.known_vocabulary
        )
        return (known_count / len(running_headwords)) * 100

    def display_vocabulary(self):
        """Nicely prints out all currently mastered word families."""
        if not self.known_vocabulary:
            print("\nReader's Vocabulary is currently empty.")
            return

        print(
            f"\n========================================\n"
            f"       READER'S MASTERED VOCABULARY     \n"
            f"       Total Word Families: {len(self.known_vocabulary)}\n"
            f"========================================"
        )

        grouped_vocab = {}
        for hw in sorted(self.known_vocabulary):
            level = self.headword_info.get(hw, {}).get("List", "Off-List/Other")
            grouped_vocab.setdefault(level, []).append(hw)

        for level, families in sorted(grouped_vocab.items()):
            print(f"\n➔ Band [{level}] ({len(families)} families):")
            chunked_lines = [
                families[i : i + 8] for i in range(0, len(families), 8)
            ]
            for line in chunked_lines:
                print("   " + ", ".join(line))
        print("========================================")


# =====================================================================
# AUTOMATED FILE PROCESSING RUN
# =====================================================================
if __name__ == "__main__":
    import pandas as pd

    # --- 1. SETUP ENVIRONMENT ---
    # Put your real BNC/COCA excel path here
    excel_file = "BNC_COCA_lists.xlsx"
    folder_name = "gutenberg_books"

    # Ensure the target folder exists so the user doesn't get a crash
    folder_path = Path(folder_name)
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
        print(
            f"Created empty directory: '{folder_name}'. Please drop your Gutenberg .txt files inside it!"
        )

    # --- 2. LOAD BNC/COCA MAP (REUSE PREVIOUS LOADER LOGIC) ---
    try:
        print("Loading BNC/COCA data tables...")
        df = pd.read_excel(excel_file)
        df.columns = [col.strip() for col in df.columns]

        mock_form_to_headword = {}
        mock_headword_info = {}

        for _, row in df.iterrows():
            if pd.isna(row["Headword"]) or pd.isna(row["Related forms"]):
                continue
            headword = str(row["Headword"]).strip().lower()
            list_level = str(row["List"]).strip()

            mock_headword_info[headword] = {"List": list_level}
            mock_form_to_headword[headword] = headword

            related_str = str(row["Related forms"])
            forms_found = re.findall(r"([\w\-\']+)\s*\(\d+\)", related_str)
            for form in forms_found:
                mock_form_to_headword[form.strip().lower()] = headword

        print("Dictionary loaded successfully.")

    except FileNotFoundError:
        print(
            f"\n[Warning] '{excel_file}' not found. Running with basic fallback mocks for demo."
        )
        # Fallback dictionary if Excel isn't in your workspace directory yet
        mock_form_to_headword = {
            "book": "book",
            "books": "book",
            "read": "read",
            "reading": "read",
            "captain": "captain",
            "whale": "whale",
            "whales": "whale",
        }
        mock_headword_info = {
            "book": {"List": "1k"},
            "read": {"List": "1k"},
            "captain": {"List": "3k"},
            "whale": {"List": "4k"},
        }

    # --- 3. INITIALIZE ENGINE ---
    engine = LexiPathEngine(
        form_to_headword=mock_form_to_headword,
        headword_info=mock_headword_info,
        required_views=10,
    )

    # --- 4. BATCH READ TEXT FILES FROM FOLDER ---
    txt_files = list(folder_path.glob("*.txt"))

    if not txt_files:
        print(
            f"\nNo text documents found in './{folder_name}/'. Add some .txt files and try again."
        )
    else:
        print(f"\nFound {len(txt_files)} books inside '{folder_name}'.")

        # Cycle 1: Let's incrementally READ the first book to see step-by-step vocabulary build-up
        first_book_path = txt_files[0]
        print(f"\n--- 1. Reading book incrementally: {first_book_path.name} ---")
        with open(first_book_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Check coverage before reading it
        pre_coverage = engine.compute_known_percentage(content)
        print(f"Reader's prior coverage metrics on this book: {pre_coverage:.2f}%")

        # Read it (counts items up to threshold)
        engine.read_text(content)
        print(
            f"Book parsed. Current overall mastered families count: {len(engine.known_vocabulary)}"
        )

        # Cycle 2: Directly LEARN a second book (if available) to force-master everything instantly
        if len(txt_files) > 1:
            second_book_path = txt_files[1]
            print(
                f"\n--- 2. Instantly learning second book: {second_book_path.name} ---"
            )
            with open(second_book_path, "r", encoding="utf-8") as file:
                second_content = file.read()

            engine.learn_text(second_content)

        # Cycle 3: Compute final vocabulary standings
        engine.display_vocabulary()