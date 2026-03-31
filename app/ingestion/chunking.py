def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks
