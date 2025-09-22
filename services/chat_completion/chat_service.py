
from typing import List, Dict, Any, Optional
from datetime import datetime
from typing import Tuple


from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from models.models import ChatMessage
from settings import settings
from api.exceptions import ChatCompletionError


class ChatService:
    """
    Azure OpenAI-powered chat service with vector store context retrieval.
    
    Features:
    - Contextual chat using document embeddings
    - Secure authentication with managed identity
    - Proper error handling and logging
    """
    
    def __init__(self):
        """
        Initialize the ChatService with Azure OpenAI and vector store.
        
        Raises:
            ChatCompletionError: If initialization fails.
        """
        try:
            # Use managed identity for secure authentication
            credential = DefaultAzureCredential()
            
            # Initialize Azure OpenAI chat model
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                azure_deployment=settings.azure_openai_chat_deployment,
                api_version=settings.azure_openai_chat_api_version,
                azure_ad_token_provider=lambda: credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                ).token,
                max_completion_tokens=1000,  # Reasonable response length
                streaming=False,  # Disable streaming for simplicity
            )
            
            # Create the chat prompt template
            self.prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content=self._get_system_prompt()),
                MessagesPlaceholder(variable_name="context"),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}")
            ])
            
            # Create the processing chain
            self.chain = (
                RunnablePassthrough.assign(
                    context=lambda x: self._format_context(x.get("context", []))
                )
                | self.prompt_template
                | self.llm
                | StrOutputParser()
            )

            
        except Exception as e:
            raise ChatCompletionError(f"Chat service initialization failed: {str(e)}")
    
    def chat_with_context(
        self,
        question: str,
        chat_history: Optional[List[ChatMessage]] = None,
        context_docs: List[Tuple[Document, float]] = []
    ) -> Dict[str, Any]:
        """
        Generate a chat response using question + vector store context.
        
        Args:
            question (str): The user's question/message
            chat_history (List[Dict], optional): Previous chat messages
            top_k (int): Number of context documents to retrieve
            similarity_threshold (float): Minimum similarity score for context
            file_id_filter (str, optional): Filter context to specific file
            
        Returns:
            Dict containing:
                - response (str): AI-generated response
                - context_used (List[Dict]): Context documents that informed the response
                - timestamp (str): ISO timestamp of the response
                
        Raises:
            ValueError: If question is empty
            ChatCompletionError: If context retrieval fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
            
        try:
            # Format chat history for the prompt
            formatted_history = self._format_chat_history(chat_history or [])

            # For the chain, pass the list of (Document, score) tuples
            response = self.chain.invoke({
                "question": question,
                "context": context_docs,
                "chat_history": formatted_history
            })

            result = {
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

            return result
        except Exception as e:
            raise ChatCompletionError(f"Chat completion failed: {str(e)}")
    
    
    def _format_context(self, context_docs: List[Tuple[Document, float]]) -> list:
        """
        Format context documents (with scores) into a list of SystemMessage objects for the prompt.
        
        Args:
            context_docs (List[Tuple[Document, float]]): Context documents and their similarity scores
        Returns:
            list: List of SystemMessage objects for LangChain
        """
        if not context_docs:
            return []
        messages = []
        for i, (doc, score) in enumerate(context_docs, 1):
            file_id = doc.metadata.get("file_id", "unknown")
            content = f"Context {i} (from file: {file_id}, relevance: {score:.2f}):\n{doc.page_content}"
            messages.append(SystemMessage(content=content))
        return messages
    
    def _format_chat_history(self, chat_history: Optional[List[ChatMessage]]) -> list:
        """
        Convert chat history (List[ChatMessage]) to LangChain message format.
        Args:
            chat_history (Optional[List[ChatMessage]]): List of ChatMessage objects
        Returns:
            list: Formatted messages for LangChain
        """
        messages = []
        if not chat_history:
            return messages
        for message in chat_history:
            role = getattr(message, "role", "user")
            content = getattr(message, "content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
        return messages
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the AI assistant.
        
        Returns:
            str: System prompt
        """
        return (
            """
            You are a helpful AI assistant with access to document context.

            Guidelines:
            - Use the provided context to answer questions accurately.
            - Each context is labeled as 'Context N (from file: <file_id>, relevance: <score>)'.
            - If the context doesn't contain relevant information or there are no context, say so clearly.
            - Be concise but thorough in your responses.
            - If asked about something not in the context, provide general knowledge but mention the limitation.

            Always prioritize accuracy over completeness.
            """
                    )