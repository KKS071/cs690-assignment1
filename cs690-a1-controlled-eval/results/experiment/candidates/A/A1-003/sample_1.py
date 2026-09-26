def balanced_delimiters(text):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())

    for char in text:
        if char in opening:
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False

    return not stack
