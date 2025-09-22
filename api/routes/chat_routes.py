from fastapi import APIRouter, HTTPException, Depends, status

from models.models import ChatRequest, ChatResponse, ErrorResponse
from services.auth_service import AuthService
from services.chat_completion.chat_service import ChatService
from services.file_pipeline.vector_store_service import VectoreStoreService

router = APIRouter(prefix="/chat", tags=["chat"])


chat_service = ChatService()
auth_service = AuthService()
vector_store_service = VectoreStoreService()


@router.post("/", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    username: str = Depends(auth_service.verify_token),
) -> ChatResponse:
    """
    Generate a chat response with optional vector store context.
    
    - **question**: The user's question or message
    - **chat_history**: Previous conversation messages (optional). Should be a list of dicts in the format {"role": "", "content": ""}, where role is either 'user' or 'assistant'.
    
    Returns enriched AI response with context information.
    """

    retrieved_context = vector_store_service.similarity_search(
        query=request.question)
    
    result = chat_service.chat_with_context(
            question=request.question,
            chat_history=request.chat_history,
            context_docs=retrieved_context
        )
    
    return ChatResponse(**result)