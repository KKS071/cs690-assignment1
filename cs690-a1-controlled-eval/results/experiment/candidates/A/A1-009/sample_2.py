def first_unique_index(text):
    from collections import Counter

    counts = Counter(text)
    for index, char in enumerate(text):
        if counts[char] == 1:
            return index
    return -1
