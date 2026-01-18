def extract_context(file_path): 
    """Extract context from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            context = f.read()
        return context
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

if __name__ == "__main__":
    context = extract_context("data/policies.txt")
    print(context)