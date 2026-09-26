def is_palindrome_normalized(text):
    filtered = []
    for char in text:
        if 'A' <= char <= 'Z':
            filtered.append(char.lower())
        elif 'a' <= char <= 'z' or '0' <= char <= '9':
            filtered.append(char)
    return filtered == filtered[::-1]
