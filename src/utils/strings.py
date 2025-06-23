def split_by_size(text: str, max_size: int) -> list[str]:
    return [text[i : i + max_size] for i in range(0, len(text), max_size)]


def beautify_int(x: int) -> str:
    char = "-" if x < 0 else ""
    x = abs(x)
    if x < 1_000:
        return f"{char}{x}"
    elif x < 1_000_000:
        return f"{char}{x // 1000}K"
    elif x < 1_000_000_000:
        return f"{char}{x // 1_000_000}M"
    else:
        return f"{char}{x // 1_000_000_000}B"
