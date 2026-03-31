from app.core.logging import configure_logging
from app.ingestion.pipeline import IngestionPipeline


def main() -> None:
    configure_logging()
    result = IngestionPipeline().run()
    print(
        f"Indexed {result.indexed_documents} documents and {result.indexed_chunks} chunks into {result.collection_name}."
    )


if __name__ == "__main__":
    main()
