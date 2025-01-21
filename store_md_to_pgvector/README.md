# Vector Search for Markdown Documents

This project implements a vector search system for markdown documents using PostgreSQL and transformer-based embeddings. It processes markdown files by splitting them into sections, generating embeddings for each section using a pre-trained transformer model, and storing them in a PostgreSQL database for efficient similarity search.

## Components

### 1. Database Schema (`create_tables.sql`)
- Creates a `vector_search` schema
- `markdown_sections` table: Stores individual sections from markdown files
- `embeddings` table: Stores vector embeddings for each section
- Uses PostgreSQL's vector extension for efficient similarity search

### 2. Markdown Processor (`store_markdown.py`)
- Reads and splits markdown files into logical sections based on headers
- Generates embeddings using the `sentence-transformers/all-MiniLM-L6-v2` model
- Stores both sections and their embeddings in the database

## Setup

1. Install PostgreSQL and create a database:
```bash
createdb vector_db
```

2. Install Python dependencies:
```bash
pip install psycopg2-binary numpy transformers torch
```

3. Create database tables:
```bash
psql -U postgres -d vector_db -f create_tables.sql
```

## Usage

1. Place your markdown files in the project directory

2. Run the processing script:
```bash
python store_markdown.py
```

The script will:
- Split the markdown file into sections
- Generate embeddings for each section
- Store everything in the database

## Database Configuration

The database connection is configured in `store_markdown.py` with these default settings:
- Database: vector_db
- User: postgres
- Password: ****
- Host: localhost

## Technical Details

- Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- Database: PostgreSQL with vector extension
- Vector Search: Uses IVFFlat index with cosine similarity

## Dependencies

- Python 3.x
- PostgreSQL
- Python packages:
  - psycopg2-binary
  - numpy
  - transformers
  - torch
