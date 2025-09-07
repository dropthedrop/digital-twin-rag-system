-- Digital Twin Database - Common Query Examples
-- This file contains example queries for the digital twin application

-- =============================================================================
-- BASIC PROFILE QUERIES
-- =============================================================================

-- Get complete professional profile
SELECT 
    p.*,
    COUNT(DISTINCT e.id) as experience_count,
    COUNT(DISTINCT s.id) as skill_count,
    COUNT(DISTINCT pr.id) as project_count,
    COUNT(DISTINCT cc.id) as content_chunk_count
FROM professionals p
LEFT JOIN experiences e ON p.id = e.professional_id
LEFT JOIN skills s ON p.id = s.professional_id
LEFT JOIN projects pr ON p.id = pr.professional_id
LEFT JOIN content_chunks cc ON p.id = cc.professional_id
WHERE p.email = 'alexandroskar94@gmail.com'
GROUP BY p.id;

-- Get latest JSON content version
SELECT jc.version, jc.content, jc.created_at
FROM json_content jc
JOIN professionals p ON jc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
ORDER BY jc.created_at DESC
LIMIT 1;

-- =============================================================================
-- EXPERIENCE AND CAREER QUERIES
-- =============================================================================

-- Get current position and company
SELECT company, position, duration, description
FROM experiences e
JOIN professionals p ON e.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com' AND e.is_current = true;

-- Get all experiences ordered by recency
SELECT 
    company, 
    position, 
    duration,
    start_date,
    end_date,
    is_current,
    achievements,
    technologies,
    impact
FROM experiences e
JOIN professionals p ON e.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
ORDER BY e.is_current DESC, e.start_date DESC NULLS LAST, e.display_order;

-- Find experiences involving specific technology
SELECT company, position, duration, impact
FROM experiences e
JOIN professionals p ON e.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND 'Kubernetes' = ANY(e.technologies);

-- =============================================================================
-- SKILLS AND EXPERTISE QUERIES
-- =============================================================================

-- Get all technical skills by category
SELECT 
    category,
    name,
    proficiency,
    experience_years,
    context,
    projects
FROM skills s
JOIN professionals p ON s.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com' 
  AND s.is_technical = true
ORDER BY s.category, s.display_order, s.name;

-- Find skills with 'Advanced' proficiency
SELECT category, name, context, projects
FROM skills s
JOIN professionals p ON s.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND s.proficiency = 'Advanced'
ORDER BY s.category;

-- Get soft skills with examples
SELECT 
    name,
    examples,
    context
FROM skills s
JOIN professionals p ON s.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND s.is_technical = false
ORDER BY s.display_order;

-- =============================================================================
-- PROJECT PORTFOLIO QUERIES
-- =============================================================================

-- Get all completed projects with outcomes
SELECT 
    name,
    description,
    role,
    technologies,
    outcomes,
    challenges,
    repository_url
FROM projects pr
JOIN professionals p ON pr.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND pr.status = 'completed'
ORDER BY pr.display_order;

-- Find projects using specific technology
SELECT name, description, role, technologies, outcomes
FROM projects pr
JOIN professionals p ON pr.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND 'TypeScript' = ANY(pr.technologies);

-- Get current/active projects
SELECT name, description, status, start_date, technologies
FROM projects pr
JOIN professionals p ON pr.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND pr.status IN ('in_progress', 'planning')
ORDER BY pr.start_date DESC;

-- =============================================================================
-- EDUCATION AND LEARNING QUERIES
-- =============================================================================

-- Get degrees and certifications
SELECT 
    type,
    institution,
    degree_name,
    field,
    issuer,
    graduation_date,
    status,
    skills
FROM education ed
JOIN professionals p ON ed.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
ORDER BY ed.type, ed.graduation_date DESC NULLS LAST;

-- Get active/current education
SELECT institution, degree_name, field, status, relevant_coursework
FROM education ed
JOIN professionals p ON ed.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND ed.status IN ('in_progress', 'on_hold');

-- =============================================================================
-- CONTENT AND RAG QUERIES
-- =============================================================================

-- Get high-importance content chunks for RAG
SELECT 
    chunk_id,
    type,
    title,
    content,
    category,
    tags,
    relevance_score,
    date_range
FROM content_chunks cc
JOIN professionals p ON cc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND cc.importance = 'high'
ORDER BY cc.relevance_score DESC;

-- Full-text search across content chunks
SELECT 
    chunk_id,
    title,
    content,
    category,
    tags,
    ts_rank(search_vector, plainto_tsquery('english', 'DevOps automation')) as rank
FROM content_chunks cc
JOIN professionals p ON cc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND search_vector @@ plainto_tsquery('english', 'DevOps automation')
ORDER BY rank DESC;

-- Get content chunks by category
SELECT type, title, content, tags, importance
FROM content_chunks cc
JOIN professionals p ON cc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND cc.category = 'work_experience'
ORDER BY cc.relevance_score DESC;

-- =============================================================================
-- SEARCH AND DISCOVERY QUERIES
-- =============================================================================

-- Search across all professional content (experiences, skills, projects)
WITH search_results AS (
    -- Search in experiences
    SELECT 'experience' as type, company || ' - ' || position as title, 
           description as content, 'experience' as category
    FROM experiences e
    JOIN professionals p ON e.professional_id = p.id
    WHERE p.email = 'alexandroskar94@gmail.com'
      AND (description ILIKE '%cloud%' OR 'Cloud' = ANY(e.technologies))
    
    UNION ALL
    
    -- Search in skills
    SELECT 'skill' as type, category || ' - ' || name as title,
           context as content, 'skill' as category
    FROM skills s
    JOIN professionals p ON s.professional_id = p.id
    WHERE p.email = 'alexandroskar94@gmail.com'
      AND (name ILIKE '%cloud%' OR context ILIKE '%cloud%')
    
    UNION ALL
    
    -- Search in projects
    SELECT 'project' as type, name as title,
           description as content, 'project' as category
    FROM projects pr
    JOIN professionals p ON pr.professional_id = p.id
    WHERE p.email = 'alexandroskar94@gmail.com'
      AND (description ILIKE '%cloud%' OR 'Cloud' = ANY(pr.technologies))
)
SELECT * FROM search_results ORDER BY type, title;

-- =============================================================================
-- ANALYTICS AND INSIGHTS QUERIES
-- =============================================================================

-- Technology frequency analysis
WITH tech_usage AS (
    SELECT unnest(technologies) as technology
    FROM experiences e
    JOIN professionals p ON e.professional_id = p.id
    WHERE p.email = 'alexandroskar94@gmail.com'
    
    UNION ALL
    
    SELECT unnest(technologies) as technology
    FROM projects pr
    JOIN professionals p ON pr.professional_id = p.id
    WHERE p.email = 'alexandroskar94@gmail.com'
)
SELECT technology, COUNT(*) as usage_count
FROM tech_usage
WHERE technology IS NOT NULL AND technology != ''
GROUP BY technology
ORDER BY usage_count DESC, technology;

-- Skills progression analysis
SELECT 
    category,
    COUNT(*) as skill_count,
    COUNT(CASE WHEN proficiency = 'Advanced' THEN 1 END) as advanced_skills,
    COUNT(CASE WHEN proficiency = 'Expert' THEN 1 END) as expert_skills
FROM skills s
JOIN professionals p ON s.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
  AND s.is_technical = true
GROUP BY category
ORDER BY skill_count DESC;

-- =============================================================================
-- SITE OPERATIONS AND USAGE QUERIES
-- =============================================================================

-- Recent site activity summary
SELECT 
    operation_type,
    COUNT(*) as occurrence_count,
    AVG(response_time_ms) as avg_response_time,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
FROM site_operations
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY operation_type
ORDER BY occurrence_count DESC;

-- Chat session analysis
SELECT 
    session_id,
    COUNT(*) as interaction_count,
    MIN(created_at) as session_start,
    MAX(created_at) as session_end
FROM site_operations
WHERE operation_type = 'chat_session'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY session_id
ORDER BY session_start DESC;

-- =============================================================================
-- DATA QUALITY AND MAINTENANCE QUERIES
-- =============================================================================

-- Check data completeness
SELECT 
    'professionals' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN email IS NOT NULL THEN 1 END) as has_email,
    COUNT(CASE WHEN summary IS NOT NULL THEN 1 END) as has_summary
FROM professionals
UNION ALL
SELECT 
    'experiences' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN start_date IS NOT NULL THEN 1 END) as has_start_date,
    COUNT(CASE WHEN array_length(achievements, 1) > 0 THEN 1 END) as has_achievements
FROM experiences
UNION ALL
SELECT 
    'skills' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN proficiency IS NOT NULL THEN 1 END) as has_proficiency,
    COUNT(CASE WHEN experience_years IS NOT NULL THEN 1 END) as has_experience_years
FROM skills;

-- Find records needing attention
SELECT 'Missing proficiency in skills' as issue, COUNT(*) as count
FROM skills WHERE proficiency IS NULL
UNION ALL
SELECT 'Experiences without start dates' as issue, COUNT(*) as count
FROM experiences WHERE start_date IS NULL
UNION ALL
SELECT 'Projects without outcomes' as issue, COUNT(*) as count
FROM projects WHERE array_length(outcomes, 1) IS NULL OR array_length(outcomes, 1) = 0;

-- =============================================================================
-- JSONB PATH QUERIES (Advanced)
-- =============================================================================

-- Query specific fields from JSON content
SELECT 
    jc.version,
    jc.content->>'personalInfo'->>'name' as name,
    jc.content->'personalInfo'->'contact'->>'email' as email,
    jsonb_array_length(jc.content->'experience') as experience_count,
    jc.content->'metadata'->>'data_quality_score' as quality_score
FROM json_content jc
JOIN professionals p ON jc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
ORDER BY jc.created_at DESC
LIMIT 1;

-- Extract search keywords from JSON
SELECT 
    unnest(
        ARRAY(
            SELECT jsonb_array_elements_text(jc.content->'search_keywords')
        )
    ) as keyword,
    COUNT(*) as frequency
FROM json_content jc
JOIN professionals p ON jc.professional_id = p.id
WHERE p.email = 'alexandroskar94@gmail.com'
GROUP BY keyword
ORDER BY frequency DESC, keyword;