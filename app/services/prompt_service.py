from app.models.document import DocumentChunk


class PromptService:
    def build(self, question: str, chunks: list[DocumentChunk]) -> str:
        context_blocks = []
        for index, chunk in enumerate(chunks, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"Source {index}: {chunk.document_name}",
                        f"Section: {chunk.section or 'General'}",
                        f"Content: {chunk.text}",
                    ]
                )
            )

        context = "\n\n".join(context_blocks)
        return (
            "You are an internal HR support chatbot. "
            "Answer only from the provided context. "
            "If the context does not clearly contain the answer, say that the answer could not be verified from the HR policies and suggest contacting HR. "
            "Keep the answer concise and mention the source names you used.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )
