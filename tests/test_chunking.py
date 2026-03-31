from app.ingestion.chunking import chunk_text


def test_chunk_text_splits_large_text() -> None:
    text = "a" * 100
    chunks = chunk_text(text, chunk_size=30, chunk_overlap=5)
    assert len(chunks) >= 3
    assert all(chunks)
