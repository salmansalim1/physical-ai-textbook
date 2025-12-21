"""
Physical AI Textbook - RAG Backend
Simplified version without database dependency
Works with Python 3.14+ and flexible package versions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from typing import List, Optional
import logging
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Physical AI Textbook RAG API",
    description="RAG-powered chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("✅ OpenAI client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI: {e}")
    openai_client = None

# Initialize Qdrant client
try:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    
    if qdrant_url and qdrant_key:
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_key,
            timeout=30
        )
        logger.info("✅ Qdrant client initialized")
    else:
        logger.warning("⚠️ Qdrant credentials not found in .env")
        qdrant_client = None
except Exception as e:
    logger.error(f"❌ Failed to initialize Qdrant: {e}")
    qdrant_client = None

# Configuration
COLLECTION_NAME = "textbook_content"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-3.5-turbo"  # Change to "gpt-4o-mini" if you have access

# ============================================================================
# Pydantic Models
# ============================================================================

class ChatQuery(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., min_length=1, max_length=2000, description="User's question")
    selected_text: Optional[str] = Field(None, max_length=10000, description="Text selected by user")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What is ROS 2?",
                    "selected_text": None
                },
                {
                    "question": "Explain this concept",
                    "selected_text": "ROS 2 is a middleware framework..."
                }
            ]
        }
    }

class Source(BaseModel):
    """Model for source information"""
    content: str = Field(..., description="Content excerpt from source")
    source: str = Field(..., description="Source file path")
    relevance_score: float = Field(..., description="Similarity score (0-1)")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default=[], description="Source documents used")
    query_time: float = Field(..., description="Time taken to process query (seconds)")
    used_selected_text: bool = Field(..., description="Whether selected text was used")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall system status")
    openai_configured: bool = Field(..., description="OpenAI API status")
    qdrant_configured: bool = Field(..., description="Qdrant connection status")
    collection_exists: bool = Field(default=False, description="Whether collection exists")
    timestamp: str = Field(..., description="Current timestamp")

# ============================================================================
# Helper Functions
# ============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI API
    
    Args:
        text: Input text to embed (max 8000 chars)
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        HTTPException: If embedding generation fails
    """
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI client not configured")
    
    try:
        # Truncate text if too long
        text = text[:8000]
        
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        
        return response.data[0].embedding
    
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate embedding: {str(e)}"
        )

def search_similar_content(query: str, limit: int = 5, score_threshold: float = 0.5) -> List[dict]:
    """
    Search for similar content in Qdrant vector database
    
    Args:
        query: Search query text
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score (0-1)
        
    Returns:
        List of dictionaries containing content, source, and score
    """
    if not qdrant_client:
        logger.warning("Qdrant client not available")
        return []
    
    try:
        # Generate embedding for query
        query_embedding = get_embedding(query)
        
        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format results
        formatted_results = []
        for hit in search_results:
            formatted_results.append({
                "content": hit.payload.get("content", ""),
                "source": hit.payload.get("source", "Unknown"),
                "score": float(hit.score)
            })
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
    
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []

def generate_response(context: str, question: str) -> str:
    """
    Generate answer using OpenAI GPT model
    
    Args:
        context: Retrieved context from vector database
        question: User's question
        
    Returns:
        Generated answer as string
        
    Raises:
        HTTPException: If response generation fails
    """
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI client not configured")
    
    try:
        system_prompt = """You are a helpful AI assistant specialized in Physical AI and Humanoid Robotics. 

You have expertise in:
- ROS 2 (Robot Operating System 2)
- Gazebo and Unity simulation
- NVIDIA Isaac platform (Isaac Sim, Isaac ROS)
- Vision-Language-Action (VLA) systems
- Humanoid robot kinematics and control
- Sensor systems (LiDAR, cameras, IMUs)
- Bipedal locomotion and balance control

Answer questions based on the provided context from the textbook. 
Be clear, technical yet accessible, and provide code examples when relevant.
If the context doesn't contain enough information, acknowledge this and provide what you can based on general knowledge of the field."""

        user_prompt = f"""Context from the textbook:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If you reference specific concepts or code, explain them clearly."""

        response = openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            top_p=0.95
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Physical AI & Humanoid Robotics Textbook - RAG API",
        "version": "1.0.0",
        "description": "Retrieval-Augmented Generation chatbot for textbook Q&A",
        "endpoints": {
            "health": "/health - Health check",
            "chat": "/api/chat - Main chat endpoint",
            "docs": "/docs - Interactive API documentation",
            "redoc": "/redoc - Alternative API documentation"
        },
        "features": [
            "RAG-powered question answering",
            "Selected text queries",
            "Source citation",
            "Real-time responses"
        ]
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and configuration
    """
    collection_exists = False
    
    if qdrant_client:
        try:
            collections = qdrant_client.get_collections()
            collection_exists = any(c.name == COLLECTION_NAME for c in collections.collections)
        except Exception as e:
            logger.warning(f"Could not check collection: {e}")
    
    openai_ok = openai_client is not None
    qdrant_ok = qdrant_client is not None
    
    status = "healthy" if (openai_ok and qdrant_ok and collection_exists) else "degraded"
    
    return HealthResponse(
        status=status,
        openai_configured=openai_ok,
        qdrant_configured=qdrant_ok,
        collection_exists=collection_exists,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(query: ChatQuery):
    """
    Main chat endpoint with RAG capabilities
    
    Supports two modes:
    1. **Selected text mode**: Answer questions about user-selected text
    2. **RAG mode**: Search textbook and answer from retrieved content
    
    Args:
        query: ChatQuery object with question and optional selected_text
        
    Returns:
        ChatResponse with answer, sources, and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"📩 Received query: {query.question[:100]}...")
        
        # Mode 1: User selected specific text
        if query.selected_text:
            logger.info("📝 Using selected text mode")
            
            context = query.selected_text
            sources = [Source(
                content=query.selected_text[:200] + ("..." if len(query.selected_text) > 200 else ""),
                source="User-selected text",
                relevance_score=1.0
            )]
            used_selected = True
        
        # Mode 2: RAG - search for relevant content
        else:
            logger.info("🔍 Using RAG mode - searching vector database")
            
            similar_docs = search_similar_content(query.question, limit=5)
            
            if not similar_docs:
                logger.warning("No relevant documents found")
                return ChatResponse(
                    answer="I couldn't find relevant information in the textbook to answer your question. Please try:\n\n1. Rephrasing your question\n2. Asking about topics covered in the course modules:\n   - Module 1: ROS 2 fundamentals\n   - Module 2: Gazebo & Unity simulation\n   - Module 3: NVIDIA Isaac platform\n   - Module 4: Vision-Language-Action systems\n\nOr try selecting specific text from the textbook and asking about it!",
                    sources=[],
                    query_time=time.time() - start_time,
                    used_selected_text=False
                )
            
            # Combine content from similar documents
            context = "\n\n---\n\n".join([doc["content"] for doc in similar_docs])
            
            sources = [
                Source(
                    content=doc["content"][:200] + ("..." if len(doc["content"]) > 200 else ""),
                    source=doc["source"],
                    relevance_score=doc["score"]
                )
                for doc in similar_docs
            ]
            used_selected = False
        
        # Generate response using GPT
        logger.info("🤖 Generating response with GPT...")
        answer = generate_response(context, query.question)
        
        query_time = time.time() - start_time
        logger.info(f"✅ Query completed in {query_time:.2f}s")
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            query_time=query_time,
            used_selected_text=used_selected
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/api/stats", tags=["Stats"])
async def get_stats():
    """
    Get basic statistics about the system
    
    Returns collection info if available
    """
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Qdrant not configured")
    
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        
        return {
            "collection_name": COLLECTION_NAME,
            "total_vectors": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size,
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("="*60)
    logger.info("🚀 Physical AI Textbook RAG API Starting Up")
    logger.info("="*60)
    logger.info(f"OpenAI Configured: {openai_client is not None}")
    logger.info(f"Qdrant Configured: {qdrant_client is not None}")
    logger.info(f"Chat Model: {CHAT_MODEL}")
    logger.info(f"Embedding Model: {EMBEDDING_MODEL}")
    logger.info("="*60)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server directly...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )