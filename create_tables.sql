-- Create a schema for our vector search implementation
CREATE SCHEMA IF NOT EXISTS vector_search;

-- Create a table for storing markdown sections
CREATE TABLE IF NOT EXISTS vector_search.markdown_sections (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_file TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for storing vector embeddings
CREATE TABLE IF NOT EXISTS vector_search.embeddings (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES vector_search.markdown_sections(id) ON DELETE CASCADE,
    embedding vector(1536),  -- Using 1536 dimensions which is standard for many embedding models
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the embedding column
CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON vector_search.embeddings USING ivfflat (embedding vector_cosine_ops);
