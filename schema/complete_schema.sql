-- Digital Twin Database Migration Summary
-- Complete DDL for recreating the schema from scratch

-- =============================================================================
-- EXTENSIONS AND SETUP
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Main professional profiles
CREATE TABLE professionals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    location VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    linkedin VARCHAR(500),
    github VARCHAR(500),
    portfolio VARCHAR(500),
    summary TEXT,
    elevator_pitch TEXT,
    search_keywords TEXT[],
    data_quality_score INTEGER CHECK (data_quality_score >= 0 AND data_quality_score <= 100),
    completeness JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Full JSON content storage with versioning
CREATE TABLE json_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    content_hash VARCHAR(64) UNIQUE,
    validation_status VARCHAR(50) DEFAULT 'valid' CHECK (validation_status IN ('valid', 'invalid', 'pending')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(professional_id, version)
);

-- RAG-optimized content chunks
CREATE TABLE content_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    importance VARCHAR(20) DEFAULT 'medium' CHECK (importance IN ('low', 'medium', 'high', 'critical')),
    date_range VARCHAR(100),
    relevance_score DECIMAL(3,2) DEFAULT 1.0 CHECK (relevance_score >= 0 AND relevance_score <= 1),
    vector_id VARCHAR(255),
    embedding_model VARCHAR(100),
    search_vector tsvector,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Work experience history
CREATE TABLE experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    duration VARCHAR(100),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    description TEXT,
    achievements TEXT[],
    technologies TEXT[],
    skills_developed TEXT[],
    impact TEXT,
    keywords TEXT[],
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Technical and soft skills
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    proficiency VARCHAR(50) CHECK (proficiency IN ('Beginner', 'Intermediate', 'Intermediate‑Advanced', 'Advanced', 'Expert')),
    experience_years VARCHAR(20),
    context TEXT,
    projects TEXT[],
    is_technical BOOLEAN DEFAULT true,
    examples TEXT[],
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(professional_id, category, name)
);

-- Portfolio projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    role VARCHAR(255),
    technologies TEXT[],
    outcomes TEXT[],
    challenges TEXT[],
    demo_url VARCHAR(500),
    repository_url VARCHAR(500),
    documentation_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('planning', 'in_progress', 'completed', 'on_hold', 'cancelled')),
    start_date DATE,
    end_date DATE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Education and certifications
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('degree', 'certificate', 'certification', 'course')),
    institution VARCHAR(255) NOT NULL,
    degree_name VARCHAR(255),
    field VARCHAR(255),
    issuer VARCHAR(255),
    graduation_date DATE,
    expiry_date DATE,
    verification_url VARCHAR(500),
    achievements TEXT[],
    relevant_coursework TEXT[],
    projects TEXT[],
    skills TEXT[],
    gpa VARCHAR(10),
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('in_progress', 'completed', 'on_hold', 'dropped')),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Site analytics and operations
CREATE TABLE site_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID REFERENCES professionals(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN ('chat_session', 'search_query', 'page_view', 'content_update', 'admin_action', 'system_event')),
    session_id VARCHAR(255),
    user_agent TEXT,
    ip_address INET,
    request_data JSONB,
    response_data JSONB,
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Professionals table indexes
CREATE INDEX idx_professionals_email ON professionals(email);
CREATE INDEX idx_professionals_active ON professionals(is_active);
CREATE INDEX idx_professionals_keywords ON professionals USING GIN(search_keywords);
CREATE INDEX idx_professionals_updated ON professionals(updated_at);

-- JSON content indexes
CREATE INDEX idx_json_content_professional ON json_content(professional_id);
CREATE INDEX idx_json_content_version ON json_content(professional_id, version);
CREATE INDEX idx_json_content_gin ON json_content USING GIN(content);
CREATE INDEX idx_json_content_created ON json_content(created_at);

-- Content chunks indexes
CREATE INDEX idx_content_chunks_professional ON content_chunks(professional_id);
CREATE INDEX idx_content_chunks_type ON content_chunks(type);
CREATE INDEX idx_content_chunks_category ON content_chunks(category);
CREATE INDEX idx_content_chunks_importance ON content_chunks(importance);
CREATE INDEX idx_content_chunks_tags ON content_chunks USING GIN(tags);
CREATE INDEX idx_content_chunks_search ON content_chunks USING GIN(search_vector);
CREATE INDEX idx_content_chunks_relevance ON content_chunks(relevance_score DESC);
CREATE INDEX idx_content_chunks_vector ON content_chunks(vector_id) WHERE vector_id IS NOT NULL;

-- Experiences indexes
CREATE INDEX idx_experiences_professional ON experiences(professional_id);
CREATE INDEX idx_experiences_company ON experiences(company);
CREATE INDEX idx_experiences_current ON experiences(is_current);
CREATE INDEX idx_experiences_dates ON experiences(start_date, end_date);
CREATE INDEX idx_experiences_technologies ON experiences USING GIN(technologies);
CREATE INDEX idx_experiences_keywords ON experiences USING GIN(keywords);
CREATE INDEX idx_experiences_order ON experiences(professional_id, display_order);

-- Skills indexes
CREATE INDEX idx_skills_professional ON skills(professional_id);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_proficiency ON skills(proficiency);
CREATE INDEX idx_skills_technical ON skills(is_technical);
CREATE INDEX idx_skills_projects ON skills USING GIN(projects);
CREATE INDEX idx_skills_order ON skills(professional_id, category, display_order);

-- Projects indexes
CREATE INDEX idx_projects_professional ON projects(professional_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_technologies ON projects USING GIN(technologies);
CREATE INDEX idx_projects_dates ON projects(start_date, end_date);
CREATE INDEX idx_projects_order ON projects(professional_id, display_order);

-- Education indexes
CREATE INDEX idx_education_professional ON education(professional_id);
CREATE INDEX idx_education_type ON education(type);
CREATE INDEX idx_education_institution ON education(institution);
CREATE INDEX idx_education_status ON education(status);
CREATE INDEX idx_education_graduation ON education(graduation_date);
CREATE INDEX idx_education_order ON education(professional_id, display_order);

-- Site operations indexes
CREATE INDEX idx_site_ops_professional ON site_operations(professional_id);
CREATE INDEX idx_site_ops_type ON site_operations(operation_type);
CREATE INDEX idx_site_ops_session ON site_operations(session_id);
CREATE INDEX idx_site_ops_created ON site_operations(created_at);
CREATE INDEX idx_site_ops_response_time ON site_operations(response_time_ms);
CREATE INDEX idx_site_ops_status ON site_operations(status_code);
CREATE INDEX idx_site_ops_request_data ON site_operations USING GIN(request_data);
CREATE INDEX idx_site_ops_metadata ON site_operations USING GIN(metadata);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to automatically update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_professionals_updated_at 
    BEFORE UPDATE ON professionals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_chunks_updated_at 
    BEFORE UPDATE ON content_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_experiences_updated_at 
    BEFORE UPDATE ON experiences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at 
    BEFORE UPDATE ON skills 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_updated_at 
    BEFORE UPDATE ON education 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically maintain search vectors
CREATE OR REPLACE FUNCTION update_content_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        COALESCE(NEW.title, '') || ' ' || 
        COALESCE(NEW.content, '') || ' ' || 
        COALESCE(array_to_string(NEW.tags, ' '), '')
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for automatic search vector updates
CREATE TRIGGER update_content_chunks_search_vector 
    BEFORE INSERT OR UPDATE ON content_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_content_search_vector();

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE professionals IS 'Core professional profile information with search keywords and data quality metrics';
COMMENT ON TABLE json_content IS 'Full JSON document storage with versioning and validation for complete data preservation';
COMMENT ON TABLE content_chunks IS 'RAG-optimized content pieces with search vectors and relevance scoring for AI applications';
COMMENT ON TABLE experiences IS 'Structured work history with achievements, technologies, and impact metrics';
COMMENT ON TABLE skills IS 'Technical and soft skills with proficiency levels, context, and project references';
COMMENT ON TABLE projects IS 'Portfolio projects with comprehensive metadata, outcomes, and technical details';
COMMENT ON TABLE education IS 'Academic credentials, certifications, and learning achievements with flexible typing';
COMMENT ON TABLE site_operations IS 'Analytics and operational data for digital twin site usage and performance monitoring';

COMMENT ON COLUMN content_chunks.search_vector IS 'Automatically maintained tsvector for full-text search across title, content, and tags';
COMMENT ON COLUMN content_chunks.vector_id IS 'Reference to vector database for similarity search and embeddings';
COMMENT ON COLUMN json_content.content_hash IS 'SHA-256 hash for deduplication and change detection';
COMMENT ON COLUMN professionals.search_keywords IS 'Array of keywords for discovery and matching algorithms';

-- =============================================================================
-- SCHEMA VALIDATION QUERY
-- =============================================================================

-- Verify schema creation
SELECT 
    t.table_name,
    COUNT(c.column_name) as column_count,
    COUNT(i.indexname) as index_count
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name AND c.table_schema = 'public'
LEFT JOIN pg_indexes i ON t.table_name = i.tablename AND i.schemaname = 'public'
WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
GROUP BY t.table_name
ORDER BY t.table_name;