def transpose_rectangular(matrix):
    if not matrix:
        return []

    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("rows have different lengths")

    return [[matrix[row][column] for row in range(len(matrix))]
            for column in range(width)]
