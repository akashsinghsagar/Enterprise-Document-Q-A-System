"""
Prompt Templates for RAG-based Document Q&A System

Contains carefully crafted prompt templates that instruct the LLM to:
1. Answer ONLY from the provided context
2. Be concise and accurate
3. Return a specific message when the answer is not in the context
"""

from langchain_core.prompts import PromptTemplate


# High-quality RAG prompt for clear, direct document-based answers
RAG_PROMPT_TEMPLATE = """You are a precise document assistant. Answer using ONLY the provided information.

KEY RULES:
1. ANSWER DIRECTLY - Start with the main answer immediately
2. NO meta-commentary - Don't mention what's in or not in the context
3. SIMPLE LANGUAGE - Write for general readers, not academics
4. STRUCTURED FORMAT - Use bullets (•) for lists, clear paragraphs for text
5. EXPLAIN DATA - When showing numbers/percentages, explain what they mean
6. IF NOT FOUND - Respond with exactly: "Answer not available in the document."
7. CITE SOURCES - Reference which part of the document supports your answer
8. BE COMPLETE - Answer fully but concisely (3-5 sentences typical)

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {question}

DIRECT ANSWER (no preamble):"""


# Alternative condensed prompt for shorter responses
CONDENSED_RAG_PROMPT_TEMPLATE = """Answer the question using ONLY the context below. If not found, respond with: "Answer not available in the document."

Context: {context}

Question: {question}

Answer:"""


# Prompt for query reformulation (optional enhancement)
QUERY_REFORMULATION_TEMPLATE = """Given the following user question, rephrase it to be more suitable for semantic search while preserving the intent.

Original Question: {question}

Reformulated Question:"""


def get_rag_prompt() -> PromptTemplate:
    """
    Get the main RAG prompt template for question answering.
    
    Returns:
        PromptTemplate: LangChain prompt template configured for strict RAG
    """
    return PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )


def get_condensed_prompt() -> PromptTemplate:
    """
    Get a condensed version of the RAG prompt for faster inference.
    
    Returns:
        PromptTemplate: Condensed prompt template
    """
    return PromptTemplate(
        template=CONDENSED_RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )


def get_query_reformulation_prompt() -> PromptTemplate:
    """
    Get prompt template for query reformulation.
    
    This can be used to improve retrieval quality by rephrasing user questions
    into more search-friendly formats.
    
    Returns:
        PromptTemplate: Query reformulation prompt template
    """
    return PromptTemplate(
        template=QUERY_REFORMULATION_TEMPLATE,
        input_variables=["question"]
    )


def format_context(documents: list) -> str:
    """
    Format retrieved documents into a structured context for LLM.
    """
    if not documents:
        return "No relevant information found."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        
        source = metadata.get('source', 'Unknown')
        page = metadata.get('page', 'N/A')
        
        content = ' '.join(content.split())
        context_part = f"[Source {i}] {source} (Page {page}):\n{content}"
        context_parts.append(context_part)
    
    return "\n---\n".join(context_parts)


def validate_answer(answer: str) -> dict:
    """
    Validate and categorize the model's answer.
    
    Args:
        answer: Raw answer from the LLM
        
    Returns:
        dict: Dictionary containing validated answer and metadata
    """
    answer_cleaned = answer.strip()
    
    # Check if answer indicates context unavailability
    not_available_phrases = [
        "answer not available in the document",
        "not found in the context",
        "information is not available",
        "cannot be answered from the context"
    ]
    
    answer_available = True
    for phrase in not_available_phrases:
        if phrase.lower() in answer_cleaned.lower():
            answer_available = False
            break
    
    return {
        "answer": answer_cleaned,
        "answer_available": answer_available,
        "confidence": "high" if answer_available and len(answer_cleaned) > 10 else "low"
    }
