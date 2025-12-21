"""
Document Ingestion Script for Physical AI Textbook
Processes markdown files and creates embeddings for RAG system
No database required - stores everything in Qdrant vector database
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import logging
from typing import List, Tuple
import hashlib
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize clients
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("✅ OpenAI client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI: {e}")
    sys.exit(1)

try:
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=60
    )
    logger.info("✅ Qdrant client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Qdrant: {e}")
    sys.exit(1)

# Configuration
COLLECTION_NAME = "textbook_content"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# ============================================================================
# Collection Management
# ============================================================================

def create_collection_if_not_exists():
    """Create Qdrant collection if it doesn't exist"""
    try:
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            logger.info(f"📦 Collection '{COLLECTION_NAME}' already exists")
            
            # Ask user if they want to recreate
            response = input("❓ Do you want to recreate the collection? This will delete all existing data (y/N): ")
            if response.lower() == 'y':
                qdrant_client.delete_collection(COLLECTION_NAME)
                logger.info(f"🗑️  Deleted existing collection")
            else:
                logger.info("➡️  Will append to existing collection")
                return False
        
        # Create new collection
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
        logger.info(f"✅ Created collection '{COLLECTION_NAME}'")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create collection: {e}")
        sys.exit(1)

# ============================================================================
# Text Processing Functions
# ============================================================================

def clean_markdown_text(text: str) -> str:
    """
    Clean markdown text by removing excessive formatting while preserving content
    
    Args:
        text: Raw markdown text
        
    Returns:
        Cleaned text suitable for embedding
    """
    # Remove YAML front matter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Convert headers to plain text (keep content)
    text = re.sub(r'#{1,6}\s+', '', text)
    
    # Remove code block markers but keep content
    text = re.sub(r'```[\w]*\n', '', text)
    text = re.sub(r'```', '', text)
    
    # Remove inline code markers
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove links but keep text [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # Remove Docusaurus-specific tags
    text = re.sub(r':::\w+.*?:::', '', text, flags=re.DOTALL)
    
    # Remove excess whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text

def extract_metadata_from_markdown(text: str, file_path: Path) -> dict:
    """
    Extract metadata from markdown front matter
    
    Args:
        text: Markdown content
        file_path: Path to the file
        
    Returns:
        Dictionary with metadata
    """
    metadata = {
        "file_path": str(file_path),
        "title": file_path.stem.replace('-', ' ').title()
    }
    
    # Try to extract YAML front matter
    front_matter_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if front_matter_match:
        front_matter = front_matter_match.group(1)
        for line in front_matter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
    
    return metadata

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks for better context
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to end at a sentence boundary
        if end < len(text):
            # Look for sentence endings
            last_period = chunk.rfind('. ')
            last_question = chunk.rfind('? ')
            last_exclamation = chunk.rfind('! ')
            last_newline = chunk.rfind('\n\n')
            
            # Find the best break point
            break_point = max(last_period, last_question, last_exclamation, last_newline)
            
            if break_point > chunk_size * 0.5:  # At least 50% through chunk
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        
        # Move start position with overlap
        start = end - overlap
        
        # Prevent infinite loop
        if start >= len(text) - overlap:
            break
    
    return chunks

# ============================================================================
# Embedding Generation
# ============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as list of floats
    """
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text[:8000]  # Limit to avoid token limits
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise

def generate_chunk_id(content: str, source: str, chunk_index: int) -> str:
    """
    Generate a unique ID for a chunk
    
    Args:
        content: Chunk content
        source: Source file
        chunk_index: Index of chunk
        
    Returns:
        Unique hash ID
    """
    hash_input = f"{source}:{chunk_index}:{content[:100]}"
    return hashlib.md5(hash_input.encode()).hexdigest()

# ============================================================================
# File Processing
# ============================================================================

def process_markdown_file(file_path: Path, docs_dir: Path) -> List[Tuple[str, dict]]:
    """
    Process a single markdown file
    
    Args:
        file_path: Path to markdown file
        docs_dir: Base docs directory
        
    Returns:
        List of (chunk_text, metadata) tuples
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Extract metadata
        metadata = extract_metadata_from_markdown(raw_content, file_path)
        
        # Clean and chunk text
        cleaned_text = clean_markdown_text(raw_content)
        
        if not cleaned_text or len(cleaned_text) < 50:
            logger.warning(f"⚠️  Skipping {file_path.name} - insufficient content")
            return []
        
        chunks = chunk_text(cleaned_text)
        
        # Prepare chunk data
        chunk_data = []
        relative_path = file_path.relative_to(docs_dir)
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "source": str(relative_path),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk)
            })
            chunk_data.append((chunk, chunk_metadata))
        
        logger.info(f"✅ Processed {file_path.name}: {len(chunks)} chunks")
        return chunk_data
        
    except Exception as e:
        logger.error(f"❌ Failed to process {file_path}: {e}")
        return []

# ============================================================================
# Main Ingestion Function
# ============================================================================

def ingest_documents(docs_path: str, batch_size: int = 100):
    """
    Main ingestion function - processes all markdown files
    
    Args:
        docs_path: Path to docs directory
        batch_size: Number of points to upload in each batch
    """
    docs_dir = Path(docs_path)
    
    if not docs_dir.exists():
        logger.error(f"❌ Docs directory not found: {docs_path}")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("🚀 Starting Document Ingestion")
    logger.info("="*60)
    
    # Create collection
    create_collection_if_not_exists()
    
    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    logger.info(f"📚 Found {len(md_files)} markdown files")
    
    if not md_files:
        logger.error("❌ No markdown files found!")
        sys.exit(1)
    
    # Process all files
    all_chunks = []
    for md_file in md_files:
        chunks = process_markdown_file(md_file, docs_dir)
        all_chunks.extend(chunks)
    
    logger.info(f"📦 Total chunks to process: {len(all_chunks)}")
    
    if not all_chunks:
        logger.warning("⚠️  No content to ingest!")
        return
    
    # Generate embeddings and create points
    logger.info("🔄 Generating embeddings...")
    points = []
    
    for idx, (chunk_text, metadata) in enumerate(all_chunks):
        try:
            # Generate embedding
            embedding = get_embedding(chunk_text)
            
            # Create point ID
            point_id = generate_chunk_id(
                chunk_text, 
                metadata["source"], 
                metadata["chunk_index"]
            )
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": chunk_text,
                    "source": metadata["source"],
                    "title": metadata.get("title", ""),
                    "chunk_index": metadata["chunk_index"],
                    "total_chunks": metadata["total_chunks"],
                    "char_count": metadata["char_count"]
                }
            )
            points.append(point)
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                logger.info(f"⏳ Processed {idx + 1}/{len(all_chunks)} chunks")
            
            # Small delay to avoid rate limits
            if (idx + 1) % 50 == 0:
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Failed to create point for chunk {idx}: {e}")
            continue
    
    # Upload to Qdrant in batches
    logger.info(f"☁️  Uploading {len(points)} points to Qdrant...")
    
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(points) - 1) // batch_size + 1
        
        try:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            logger.info(f"✅ Uploaded batch {batch_num}/{total_batches}")
        except Exception as e:
            logger.error(f"❌ Failed to upload batch {batch_num}: {e}")
    
    logger.info("="*60)
    logger.info(f"✅ Ingestion complete!")
    logger.info(f"📊 Summary:")
    logger.info(f"   - Files processed: {len(md_files)}")
    logger.info(f"   - Total chunks: {len(points)}")
    logger.info(f"   - Collection: {COLLECTION_NAME}")
    logger.info("="*60)
    
    # Verify
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        logger.info(f"🔍 Collection now contains {collection_info.points_count} points")
    except Exception as e:
        logger.warning(f"⚠️  Could not verify collection: {e}")

# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest markdown documents into Qdrant for RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_docs.py --docs-path ../book-site/docs
  python ingest_docs.py --docs-path ./docs --batch-size 50
        """
    )
    
    parser.add_argument(
        "--docs-path",
        type=str,
        default="../book-site/docs",
        help="Path to docs directory (default: ../book-site/docs)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for uploading to Qdrant (default: 100)"
    )
    
    args = parser.parse_args()
    
    logger.info("Starting document ingestion...")
    ingest_documents(args.docs_path, args.batch_size)