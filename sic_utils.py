def get_line_index_by_char_index(input_string: str, char_index: int) -> int:
    lines = input_string.split('\n')

    total_chars = 0
    for line_index, line in enumerate(lines):
        total_chars += len(line) + 1  # +1 to account for the newline character

        if total_chars > char_index:
            return line_index

    raise SyntaxError("Index out of range")


def get_line_by_index(input_string: str, line_index: int) -> str:
    lines = input_string.split('\n')

    return lines[line_index]  # in case of index out of range error, we let it propagate


def label_suffix(label, suffix):
    """Returns (label + suffix) or a truncated version if it's too long.
    Parameters
    ----------
    label : str
        Label name
    suffix : str
        Label suffix
    """
    if len(label) > 50:
        nhead = 25
        return ''.join([label[:nhead], '..', suffix])
    else:
        return label + suffix
