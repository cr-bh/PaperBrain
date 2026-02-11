# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PaperBrain is an AI-powered academic paper management system built with Streamlit. It helps researchers manage and understand academic papers through automated parsing, structured summarization, mind mapping, intelligent tagging, and conversational Q&A using RAG (Retrieval-Augmented Generation).

## Essential Commands

### Setup and Initialization
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (creates SQLite DB and tables)
python database/init_db.py

# Run the application
streamlit run app.py
```

### Configuration
- Copy `.env.example` to `.env` and configure:
  - `LLM_API_URL`: Custom Gemini API endpoint
  - `LLM_BEARER_TOKEN`: Bearer token for API authentication
  - Optional: `DATABASE_PATH`, `CHROMA_DB_PATH`, `PAPERS_DIR`, `IMAGES_DIR`

## Architecture Overview

### Core Data Flow

**Paper Upload Pipeline:**
1. User uploads PDF → `ui/upload_page.py`
2. PDF parsing → `services/pdf_parser.py` (extracts text, metadata, images)
3. LLM summarization → `services/summarizer.py` (generates structured JSON summary)
4. Mind map generation → `services/mindmap_generator.py` (creates Mermaid.js code)
5. Auto-tagging → `services/tagger.py` (generates domain/methodology/task tags)
6. Vectorization → `services/rag_service.py` (chunks text and stores in ChromaDB)
7. Database storage → `database/db_manager.py` (saves to SQLite)

**RAG Q&A Pipeline:**
1. User asks question → `ui/chat_interface.py`
2. Parse @mentions → `rag_service.parse_mention()` (supports @paper_title syntax)
3. Vector search → ChromaDB retrieves relevant chunks
4. LLM generates answer → `llm_service.generate_text()` with retrieved context
5. Display with source attribution

### Database Schema

**SQLite (Relational Data):**
- `papers`: Core paper metadata (title, authors, file_path, content_summary JSON, mindmap_code)
- `tags`: Hierarchical tags (name, category, parent_id, color)
- `paper_tags`: Many-to-many relationship
- `paper_images`: Extracted images (image_path, caption, page_number, image_type)

**ChromaDB (Vector Store):**
- Collection: "papers"
- Documents: Text chunks (~1000 chars)
- Metadata: `{paper_id, chunk_index}`
- IDs: `paper_{paper_id}_chunk_{i}`

### Key Architectural Patterns

**Session State Management:**
- `st.session_state.current_page`: Navigation state ('dashboard', 'upload', 'paper_detail', 'chat', 'tag_management')
- `st.session_state.selected_paper_id`: Currently viewed paper
- File upload deduplication: `st.session_state.uploaded_files_{paper_id}` tracks processed files by `{filename}_{size}`

**LLM Service:**
- Custom API endpoint support (not standard Gemini SDK)
- Retry decorator: `@retry_on_error(max_retries=3, delay=2.0)`
- JSON extraction: `generate_json()` parses JSON from LLM text responses
- Response parsing: `_extract_text()` handles streaming API format

**Prompt Engineering:**
- All prompts centralized in `utils/prompts.py`
- Structured summary uses detailed JSON schema with 8 sections
- Mind map prompt includes strict color contrast requirements (no white text on light backgrounds)
- Related work section must follow paper's organization logic (temporal/technical/problem-oriented/causal/MECE)
- Title hierarchy: Module titles use `###`, internal subtitles use `#####`

## Critical Implementation Details

### Structured Summary Generation

The `content_summary` JSON field contains:
- `one_sentence_summary`: 1-2 sentence overview
- `problem_definition`: Research problem and motivation
- `existing_solutions`: Related work (must follow paper's organization logic with citations)
- `limitations`: Gaps in existing approaches
- `contribution`: Paper's main contributions
- `methodology`: Detailed method description (5 subsections: framework, algorithm, technical details, innovation, implementation)
- `results`: Experimental results with quantitative comparisons
- `future_work_paper`: Authors' stated future directions
- `future_work_insights`: Critical analysis and improvement suggestions

### Mind Map Color Requirements

**Critical:** Mind maps must have high contrast to avoid readability issues:
- **Forbidden:** Light backgrounds (yellow, light blue, light green, white) with white text
- **Recommended:**
  - Dark background + white text: `fill:#2C3E50,color:#FFFFFF`
  - Medium background + dark text: `fill:#3498DB,color:#000000`
  - Bright background + dark text: `fill:#E74C3C,color:#000000`
- Important nodes (contributions): Use bold colors with `stroke-width:3px`

### Tag Hierarchy System

Tags support parent-child relationships:
- Categories: Domain, Methodology, Task
- Parent tags can have children (e.g., "Reinforcement Learning" → "Multi-agent RL")
- Tag management UI (`ui/tag_management.py`) allows:
  - Creating/editing/deleting tags
  - Moving tags between parents
  - Changing tag colors

### RAG @Mention Syntax

Global chat supports mentioning specific papers:
- `@paper_title` or `@"paper title with spaces"` - targets specific paper(s)
- Multiple mentions supported: `@paper1 @paper2 what are the differences?`
- Fuzzy matching: Falls back to search if exact title not found
- No mention: Searches across all papers

### Image Upload and Caption Editing

Paper detail page supports user-uploaded images:
- Deduplication: Uses `{filename}_{size}` as unique identifier
- Session state tracking prevents duplicate uploads on rerun
- Edit mode: Inline caption editing with save button
- Images stored in `data/images/{paper_id}/`

## Common Gotchas

### SQLAlchemy Session Management

**Problem:** Lazy-loaded attributes (like `paper.mindmap_code`) fail after session closes.

**Solution:** Explicitly access attributes before closing session:
```python
def get_paper_by_id(self, paper_id: int):
    session = self.get_session()
    try:
        paper = session.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            _ = paper.mindmap_code  # Force load
            _ = paper.content_summary
        return paper
    finally:
        session.close()
```

### Streamlit File Uploader Reruns

**Problem:** `st.file_uploader` maintains state after upload, causing repeated processing on `st.rerun()`.

**Solution:** Track processed files in session state:
```python
file_id = f"{uploaded_file.name}_{uploaded_file.size}"
if file_id not in st.session_state.uploaded_files:
    # Process file
    st.session_state.uploaded_files.add(file_id)
```

### Prompt JSON Extraction

LLM responses may include markdown code blocks. Use `utils.helpers.extract_json_from_text()` to extract valid JSON from text that may contain:
- Markdown code fences (```json ... ```)
- Extra text before/after JSON
- Nested JSON structures

## File Organization Logic

- `app.py`: Entry point, navigation, session state initialization
- `config.py`: Environment variables and path configuration
- `database/`: SQLAlchemy models, db_manager (CRUD operations), init scripts
- `services/`: Business logic (LLM, PDF parsing, RAG, summarization, tagging, mind maps)
- `ui/`: Streamlit page components (dashboard, upload, paper detail, chat, tag management)
- `utils/`: Prompts (all LLM prompt templates), helpers (retry decorator, JSON extraction)
- `data/`: Runtime data (papers/, images/, paperbrain.db, chroma_db/)

## Prompt Template Maintenance

When modifying prompts in `utils/prompts.py`:

1. **Structured Summary (`SUMMARIZE_PAPER_PROMPT`):**
   - Maintain JSON schema compatibility
   - Keep MECE principle and organization logic requirements
   - Use `#####` for internal subtitles (not `####` or higher)

2. **Mind Map (`GENERATE_MINDMAP_PROMPT`):**
   - Always include color contrast requirements
   - Provide style definition examples
   - Require `style` statements for all nodes

3. **RAG Q&A (`RAG_QA_PROMPT`):**
   - Emphasize citation requirements
   - Handle multi-paper scenarios
   - Request source attribution

## Testing Paper Processing

To test the full pipeline:
1. Upload a PDF through the UI
2. Monitor terminal for processing logs
3. Check paper detail page for:
   - Structured notes with proper formatting
   - Mind map with readable colors
   - Auto-generated tags
   - Extracted images
4. Test chat with `@paper_title what is the main contribution?`
