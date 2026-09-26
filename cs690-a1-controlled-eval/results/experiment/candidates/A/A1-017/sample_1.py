def is_palindrome_normalized(text):
    normalized = [char.lower() for char in text if char.isascii() and char.isalnum()]
    return normalized == normalized[::-1]
