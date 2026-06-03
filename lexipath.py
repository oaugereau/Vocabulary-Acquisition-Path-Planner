import re
from collections import Counter

class LexiPathEngine:
    def __init__(self, required_views=10, required_percentage=0.90):
        self.required_views = required_views          # 'n' parameter
        self.required_percentage = required_percentage # 'm' parameter
        self.vocabulary_history = Counter()           # Tracks word occurrences
        self.known_vocabulary = set()                 # Words seen >= required_views

    def _clean_text(self, text):
        """Converts text to lowercase and extracts a list of clean words."""
        text = text.lower()
        # Extracts alphanumeric words, ignoring basic punctuation
        words = re.findall(r'\b\w+\b', text)
        return words

    def update_known_vocabulary(self):
        """Updates the set of words considered fully acquired."""
        self.known_vocabulary = {
            word for word, count in self.vocabulary_history.items() 
            if count >= self.required_views
        }

    def evaluate_accessibility(self, text):
        """Checks if a text shares at least m% of already known vocabulary."""
        text_words = set(self._clean_text(text))
        if not text_words:
            return False, 0.0
        
        # Count how many unique words in the text are already known
        known_words_in_text = text_words.intersection(self.known_vocabulary)
        ratio = len(known_words_in_text) / len(text_words)
        
        is_accessible = ratio >= self.required_percentage
        return is_accessible, ratio

    def read_text(self, text):
        """Simulates reading a text: adds words to history and updates vocabulary."""
        words = self._clean_text(text)
        self.vocabulary_history.update(words)
        self.update_known_vocabulary()
        print(f"Text read. Total mastered vocabulary: {len(self.known_vocabulary)} words.")