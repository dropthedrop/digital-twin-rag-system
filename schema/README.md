# Digital Twin Database Schema Documentation

## Overview
This PostgreSQL database schema is designed for a professional digital twin application that stores both structured professional data and flexible JSON content chunks for RAG (Retrieval-Augmented Generation) system integration.

## Database Information
- **Database**: neondb
- **PostgreSQL Version**: 17
- **Extensions Used**: uuid-ossp, btree_gin

## Tables Overview

### Core Tables (8 total)

1. **professionals** (16 columns) - Main profile information
2. **json_content** (7 columns) - Full JSON document storage
3. **content_chunks** (16 columns) - Processed content for RAG system
4. **experiences** (17 columns) - Structured work history
5. **skills** (13 columns) - Technical and soft skills
6. **projects** (17 columns) - Portfolio projects and case studies
7. **education** (19 columns) - Academic and professional learning
8. **site_operations** (13 columns) - Operational data and analytics

## Detailed Table Descriptions

### professionals
Primary table containing core professional information.
- **Primary Key**: id (UUID)
- **Key Fields**: name, title, location, email, linkedin, github
- **Search Features**: search_keywords (TEXT[]), full-text capabilities
- **Metadata**: data_quality_score, completeness (JSONB)
- **Audit**: created_at, updated_at, is_active

### json_content
Stores complete mytwin.json data with versioning and validation.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Content**: Full JSONB document with hash-based deduplication
- **Versioning**: version field with unique constraint per professional
- **Validation**: validation_status with check constraint

### content_chunks
RAG-optimized content pieces with search and embedding support.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Content**: title, content (text), category, tags (TEXT[])
- **RAG Features**: vector_id, embedding_model, search_vector (tsvector)
- **Scoring**: importance, relevance_score, date_range
- **Search**: Full-text search via tsvector with automatic updates

### experiences
Structured work history with comprehensive details.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Core**: company, position, duration, start_date, end_date, is_current
- **Details**: description, achievements (TEXT[]), technologies (TEXT[])
- **Impact**: skills_developed (TEXT[]), impact, keywords (TEXT[])
- **Ordering**: display_order for UI presentation

### skills
Technical and soft skills with categorization and proficiency tracking.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Classification**: category, name, is_technical
- **Assessment**: proficiency, experience_years, context
- **Evidence**: projects (TEXT[]), examples (TEXT[])
- **Constraints**: Unique per (professional_id, category, name)

### projects
Portfolio projects with comprehensive metadata.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Core**: name, description, role, status
- **Technical**: technologies (TEXT[]), outcomes (TEXT[]), challenges (TEXT[])
- **Links**: demo_url, repository_url, documentation_url
- **Timeline**: start_date, end_date, display_order

### education
Academic and professional learning with flexible typing.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id)
- **Types**: degree, certificate, certification, course
- **Details**: institution, degree_name, field, issuer
- **Academic**: achievements (TEXT[]), relevant_coursework (TEXT[])
- **Validation**: verification_url, expiry_date for certifications
- **Timeline**: graduation_date, status

### site_operations
Analytics and operational data for the digital twin site.
- **Primary Key**: id (UUID)
- **Foreign Key**: professional_id → professionals(id) (optional)
- **Types**: chat_session, search_query, page_view, content_update, admin_action, system_event
- **Session**: session_id, user_agent, ip_address
- **Data**: request_data (JSONB), response_data (JSONB), metadata (JSONB)
- **Performance**: response_time_ms, status_code, error_message

## Indexes and Performance

### Comprehensive Indexing Strategy
- **Primary Keys**: B-tree indexes on all UUID primary keys
- **Foreign Keys**: B-tree indexes on all foreign key relationships
- **JSONB**: GIN indexes for JSONB columns (content, metadata, request_data)
- **Arrays**: GIN indexes for all TEXT[] columns (tags, technologies, etc.)
- **Full-text Search**: GIN indexes on tsvector columns
- **Temporal**: B-tree indexes on date/timestamp columns
- **Status**: B-tree indexes on enum-like varchar fields
- **Composite**: Multi-column indexes for common query patterns

### Vector Search Support
- Prepared for vector similarity search with vector_id references
- Search vector automatically maintained via triggers
- Relevance scoring built into content_chunks

## Triggers and Functions

### Automatic Timestamp Updates
- `update_updated_at_column()` function maintains updated_at timestamps
- Triggers on: professionals, content_chunks, experiences, skills, projects, education

### Search Vector Maintenance
- `update_content_search_vector()` function maintains search_vector
- Automatically indexes title, content, and tags for full-text search
- Trigger fires on INSERT/UPDATE of content_chunks

## Data Validation

### Check Constraints
- **professionals**: data_quality_score (0-100)
- **json_content**: validation_status (valid/invalid/pending)
- **content_chunks**: importance (low/medium/high/critical), relevance_score (0-1)
- **skills**: proficiency levels (Beginner to Expert)
- **projects**: status (planning/in_progress/completed/on_hold/cancelled)
- **education**: type and status constraints
- **site_operations**: operation_type constraints

### Unique Constraints
- **professionals**: email (unique)
- **json_content**: (professional_id, version), content_hash
- **content_chunks**: chunk_id
- **skills**: (professional_id, category, name)

## Sample Data
The database contains sample data for Alexandros Karanikola including:
- 2+ work experiences (ServiceNow, AusBiz Consulting)
- 3+ technical skills (Python, JavaScript/TypeScript, AWS)
- 1+ project (CryptoGent)
- 2+ content chunks for RAG system

## Migration History
1. **Part 1**: Core tables (professionals, json_content, content_chunks, experiences)
2. **Part 2**: Remaining tables (skills, projects, education, site_operations)
3. **Part 3**: Comprehensive indexing strategy (48 indexes)
4. **Part 4**: Triggers and functions for automation
5. **Part 5**: Sample data insertion from mytwin.json

## Usage Notes
- All tables include audit trails (created_at, updated_at where applicable)
- Soft delete capability via is_active fields
- JSONB columns support path queries and flexible schema evolution
- Array columns enable efficient storage of lists without junction tables
- Full-text search ready across all relevant content
- Vector database integration prepared via vector_id references