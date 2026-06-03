import re
import string
from collections import Counter
import pandas as pd


def load_bnc_coca_lists(excel_path):
    """Loads the BNC/COCA Excel file and builds an inverted index dictionary.

    Every related form (e.g., 'abilities') will map back to its 'Headword'
    ('able') and its frequency band ('List').
    """
    print("Loading and indexing vocabulary list...")
    df = pd.read_excel(excel_path)

    # Clean any accidental leading/trailing spaces in column names
    df.columns = [col.strip() for col in df.columns]

    form_to_headword = {}
    headword_info = {}

    for _, row in df.iterrows():
        # Skip rows missing crucial data
        if pd.isna(row["Headword"]) or pd.isna(row["Related forms"]):
            continue

        headword = str(row["Headword"]).strip().lower()
        list_level = str(row["List"]).strip()

        # Save metadata for the headword
        headword_info[headword] = {"List": list_level}

        # Safety fallback: map the headword to itself
        form_to_headword[headword] = headword

        # Extract individual forms from the "Related forms" string
        # This regex matches word characters/hyphens/apostrophes followed by (numbers)
        related_str = str(row["Related forms"])
        forms_found = re.findall(r"([\w\-\']+)\s*\(\d+\)", related_str)

        for form in forms_found:
            form_cleaned = form.strip().lower()
            # Link the inflection/derivative back to the main headword
            form_to_headword[form_cleaned] = headword

    print(
        f"Indexing complete. {len(form_to_headword)} unique word forms mapped."
    )
    return form_to_headword, headword_info


def analyze_text_file(text_path, form_to_headword, headword_info):
    """Analyzes a raw text file to count the frequencies of word families."""
    print(f"Analyzing text file: {text_path}...")

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read().lower()

    # Tokenize text into words (including hyphens and apostrophes)
    words_in_text = re.findall(r"[\w\-\']+", text)

    # Counters for processing
    family_counts = Counter()
    off_list_words = Counter()

    for word in words_in_text:
        # Check if the token belongs to a known BNC/COCA family
        if word in form_to_headword:
            headword = form_to_headword[word]
            family_counts[headword] += 1
        else:
            # Proper nouns, typos, or highly specialized/rare words
            off_list_words[word] += 1

    # Format the results into a list of dictionaries
    analysis_data = []
    for headword, count in family_counts.items():
        analysis_data.append(
            {
                "Headword (Family)": headword,
                "List Level": headword_info[headword]["List"],
                "Occurrences": count,
            }
        )

    df_results = pd.DataFrame(analysis_data)

    if not df_results.empty:
        # Sort results from most frequent to least frequent
        df_results = df_results.sort_values(
            by="Occurrences", ascending=False
        ).reset_index(drop=True)

    return df_results, off_list_words


# ==========================================
# HOW TO RUN THE SCRIPT
# ==========================================
if __name__ == "__main__":
    # Change these strings to match your file paths
    excel_file = "BNC_COCA_lists.xlsx"
    text_file = "gutenberg_books/book_11.txt"

    try:
        # 1. Map all word forms to their headwords
        mapping, info = load_bnc_coca_lists(excel_file)

        # 2. Process and count words within the target text
        df_analysis, off_list = analyze_text_file(text_file, mapping, info)

        # 3. Print the top 20 most frequent word families found in the text
        print("\n--- TOP 20 MOST FREQUENT WORD FAMILIES ---")
        print(df_analysis.head(20))

        # 4. Profile Overview: Sum of occurrences per frequency band
        print("\n--- TEXT PROFILE BY FREQUENCY LEVEL ---")
        profile = (
            df_analysis.groupby("List Level")["Occurrences"]
            .sum()
            .reset_index()
        )
        profile["Percentage (%)"] = (
            profile["Occurrences"] / profile["Occurrences"].sum() * 100
        )
        print(profile.sort_values(by="Occurrences", ascending=False))

        # 5. Export findings to a clean CSV file
        df_analysis.to_csv("text_analysis_output.csv", index=False)
        print(
            "\nFull analysis report saved successfully to 'text_analysis_output.csv'."
        )

    except FileNotFoundError as e:
        print(
            f"File Error: Please double-check your local file paths. ({e})"
        )