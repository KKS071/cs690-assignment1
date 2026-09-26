def stable_partition(items, pivot):
    return [value for value in items if value < pivot] + [
        value for value in items if value >= pivot
    ]
