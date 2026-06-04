import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Importing logic from the provided sources
# Assuming these are available in the same directory as per the sources
from gutenbergpy.textget import get_text_by_id
import gutenbergpy.textget
from lexipath import LexiPathEngine 

class LexiPathGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LexiPath Engine - Text Manager")
        self.root.geometry("500x400")

        # Initialize the engine (logic from demo.txt [2])
        self.engine = LexiPathEngine()
        
        # Configuration for downloads (from gutenberg.txt [1])
        self.download_folder = "gutenberg_books"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        self.create_widgets()

    def create_widgets(self):
        # --- Section 1: Download Books ---
        tk.Label(self.root, text="Download Books (Gutenberg ID):", font=('Arial', 10, 'bold')).pack(pady=5)
        self.id_entry = tk.Entry(self.root)
        self.id_entry.pack()
        self.id_entry.insert(0, "84, 11") # Default examples: Frankenstein, Alice [1]
        
        tk.Button(self.root, text="Download Books", command=self.download_action).pack(pady=5)

        # --- Section 2: Add to Vocabulary ---
        tk.Label(self.root, text="User Vocabulary:", font=('Arial', 10, 'bold')).pack(pady=10)
        tk.Button(self.root, text="Add Text to My Vocabulary", command=self.add_vocab_action).pack()

        # --- Section 3: Visualization ---
        tk.Label(self.root, text="Analyze Book Overlap:", font=('Arial', 10, 'bold')).pack(pady=10)
        tk.Button(self.root, text="Select Book & Calculate Overlap", command=self.visualize_overlap).pack()
        
        self.result_label = tk.Label(self.root, text="Overlap: --%", fg="blue", font=('Arial', 12))
        self.result_label.pack(pady=10)

    def download_action(self):
        """Downloads books based on IDs provided (logic from gutenberg.txt [1])."""
        ids_str = self.id_entry.get()
        try:
            id_list = [int(i.strip()) for i in ids_str.split(",")]
            for book_id in id_list:
                # Mocking the cleaning process from source [1]
                raw_text = gutenbergpy.textget.get_text_by_id(book_id)
                clean_text = gutenbergpy.textget.strip_headers(raw_text)
                file_path = os.path.join(self.download_folder, f"book_{book_id}.txt")
                with open(file_path, "wb") as f:
                    f.write(clean_text)
            messagebox.showinfo("Success", f"Downloaded {len(id_list)} books to {self.download_folder}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download: {e}")

    def add_vocab_action(self):
        """Processes a file to add its word families to the user's known vocabulary [3, 4]."""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            # The engine processes the text to update user word family knowledge [3]
            self.engine.read_text(file_path)
            messagebox.showinfo("Vocabulary", "Text added to your vocabulary profile.")

    def visualize_overlap(self):
        """Calculates and displays the percentage of word family overlap [2, 4]."""
        book_path = filedialog.askopenfilename(initialdir=self.download_folder, filetypes=[("Text files", "*.txt")])
        if book_path:
            # Logic for calculating overlap between known families and the book [2, 3]
            # This uses the headword information and frequency counts [4]
            overlap = self.engine.compute_known_percentage(book_path)
            self.result_label.config(text=f"Overlap: {overlap:.2f}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = LexiPathGUI(root)
    root.mainloop()