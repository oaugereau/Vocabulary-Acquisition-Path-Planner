from lexipath import LexiPathEngine

def run_demo():
    # Initializing the engine with low thresholds for demonstration purposes
    # (n=2 views to master, m=50% vocabulary overlap required)
    engine = LexiPathEngine(required_views=2, required_percentage=0.50)

    # Bootstrapping: Simulate a basic vocabulary so the user can read the first text
    starting_vocabulary = "the a cat dog eats mat is on".split()
    for _ in range(2):
        engine.vocabulary_history.update(starting_vocabulary)
    engine.update_known_vocabulary()

    # Our sample text library
    library = {
        "Text A (Easy)": "The cat eats on the mat.",
        "Text B (Gateway)": "The dog eats a red apple on the mat.", # introduces "red", "apple"
        "Text C (Target)": "A big red dog eats an apple and chases a cat." # introduces "big", "an", "and", "chases"
    }

    print("--- Evaluating Library Accessibility ---")
    for name, content in library.items():
        accessible, score = engine.evaluate_accessibility(content)
        print(f"{name}: Accessible? {accessible} (Overlap Score: {score:.2%})")

    # Path Progression Simulation
    print("\n--- Reading Gateway Text B to learn vocabulary ---")
    engine.read_text(library["Text B (Gateway)"])
    # Reading it a second time so the new words "red" and "apple" reach count=2 (mastered)
    engine.read_text(library["Text B (Gateway)"]) 

    print("\n--- Re-evaluating Target Text C ---")
    accessible, score = engine.evaluate_accessibility(library["Text C (Target)"])
    print(f"Text C: Accessible now? {accessible} (New Overlap Score: {score:.2%})")

if __name__ == "__main__":
    run_demo()