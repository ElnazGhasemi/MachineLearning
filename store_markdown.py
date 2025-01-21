import psycopg2
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import re

def get_database_connection():
    """Create a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname="vector_db",
        user="postgres",
        password="****",
        host="localhost"
    )

def load_markdown_file(file_path):
    """Read and return the content of a markdown file."""
    with open(file_path, 'r') as file:
        return file.read()

def split_into_sections(content):
    """Split markdown content into sections based on headers."""
    # Split on headers (# or ## or ###)
    sections = re.split(r'\n(?=#+\s)', content)
    processed_sections = []
    
    for section in sections:
        if not section.strip():
            continue
        
        # Extract title and content
        lines = section.strip().split('\n')
        title = lines[0].strip('#').strip()
        content = '\n'.join(lines[1:]).strip()
        
        if content:  # Only include sections with content
            processed_sections.append({
                'title': title,
                'content': content
            })
    
    return processed_sections

def generate_embedding(text, model, tokenizer):
    """Generate embeddings for a text using the model."""
    # Prepare the text
    inputs = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
    
    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    
    return embeddings[0].numpy()

def store_section_and_embedding(conn, section, embedding, source_file):
    """Store a section and its embedding in the database."""
    with conn.cursor() as cur:
        # Insert section
        cur.execute("""
            INSERT INTO vector_search.markdown_sections (title, content, source_file)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (section['title'], section['content'], source_file))
        section_id = cur.fetchone()[0]
        
        # Insert embedding
        embedding_list = embedding.tolist()
        cur.execute("""
            INSERT INTO vector_search.embeddings (section_id, embedding)
            VALUES (%s, %s)
        """, (section_id, embedding_list))
    
    conn.commit()

def main():
    # Initialize the model and tokenizer
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Connect to database
    conn = get_database_connection()
    
    try:
        # Read markdown file
        markdown_content = load_markdown_file('sql-code-layout.md')
        
        # Split into sections
        sections = split_into_sections(markdown_content)
        
        # Process each section
        for section in sections:
            # Combine title and content for embedding
            full_text = f"{section['title']}\n{section['content']}"
            
            # Generate embedding
            embedding = generate_embedding(full_text, model, tokenizer)
            
            # Store in database
            store_section_and_embedding(conn, section, embedding, 'sql-code-layout.md')
            
        print(f"Successfully processed and stored {len(sections)} sections")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
