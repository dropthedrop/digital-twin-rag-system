#!/usr/bin/env python3
"""
Debug RAG Content Retrieval
Test what content is actually being returned by the vector search
"""

import os
import psycopg2
from upstash_vector import Index
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Connect to databases
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    vector_index = Index.from_env()
    
    # Test query
    query = "What experience do you have with AI and machine learning?"
    
    print(f"Testing query: {query}")
    print("="*60)
    
    # Search vector database
    vector_results = vector_index.query(
        data=query,
        top_k=5,
        include_metadata=True
    )
    
    print(f"Found {len(vector_results)} vector results:")
    
    for i, result in enumerate(vector_results):
        chunk_id = result.metadata.get('chunk_id')
        content_type = result.metadata.get('type')
        relevance = result.score
        
        print(f"\nResult {i+1}:")
        print(f"  Chunk ID: {chunk_id}")
        print(f"  Type: {content_type}")
        print(f"  Relevance: {relevance:.4f}")
        
        # Get actual content from PostgreSQL
        cursor = pg_conn.cursor()
        cursor.execute("SELECT content FROM content_chunks WHERE chunk_id = %s", (chunk_id,))
        content_result = cursor.fetchone()
        
        if content_result:
            content = content_result[0]
            print(f"  Content: {content[:200]}..." if len(content) > 200 else f"  Content: {content}")
            
            # Check keyword matches
            keywords = ["ai", "machine learning", "artificial intelligence"]
            content_lower = content.lower()
            matches = [kw for kw in keywords if kw in content_lower]
            print(f"  Keywords found: {matches}")
        else:
            print("  Content: NOT FOUND")
    
    pg_conn.close()

if __name__ == "__main__":
    main()