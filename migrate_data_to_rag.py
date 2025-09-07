#!/usr/bin/env python3
"""
Digital Twin Data Migration Script
==================================

Migrates data from mytwin.json to PostgreSQL database and generates vector embeddings
for RAG (Retrieval-Augmented Generation) functionality.

Features:
- JSON data validation and parsing
- PostgreSQL data insertion with proper relationships
- Content chunking for optimal RAG retrieval
- Vector embedding generation using Upstash Vector's mixbread-large model
- Comprehensive error handling and logging
- Progress tracking and recovery capabilities

Author: Digital Twin Migration System
Version: 1.0.0
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from upstash_vector import Index, Vector

# Load environment variables
load_dotenv()

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a content chunk for vector embedding"""
    content: str
    metadata: Dict[str, Any]
    chunk_type: str
    importance: str
    keywords: List[str]
    date_context: Optional[str] = None

@dataclass
class MigrationStats:
    """Track migration statistics"""
    professionals_inserted: int = 0
    experiences_inserted: int = 0
    skills_inserted: int = 0
    projects_inserted: int = 0
    education_inserted: int = 0
    json_content_inserted: int = 0
    content_chunks_created: int = 0
    vectors_embedded: int = 0
    errors_encountered: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class DigitalTwinMigrator:
    """Main migration class for Digital Twin data"""
    
    def __init__(self):
        """Initialize the migrator with database connections"""
        self.postgres_conn = None
        self.vector_index = None
        self.stats = MigrationStats()
        self.stats.start_time = datetime.now()
        
        # Configuration from environment
        self.postgres_url = os.getenv('POSTGRES_CONNECTION_STRING') or "postgresql://neondb_owner:npg_BAWzXMoQ69yn@ep-rapid-silence-a93kwvl5-pooler.gwc.azure.neon.tech/neondb?channel_binding=require&sslmode=require"
        self.vector_url = os.getenv('UPSTASH_VECTOR_REST_URL')
        self.vector_token = os.getenv('UPSTASH_VECTOR_REST_TOKEN')
        
        if not self.vector_url or not self.vector_token:
            raise ValueError("Missing Upstash Vector configuration in environment variables")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect_databases()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.close_connections()
        if exc_type:
            logger.error(f"Migration failed with error: {exc_val}")
            self.stats.errors_encountered += 1
        self.log_final_stats()
    
    def connect_databases(self):
        """Establish database connections"""
        try:
            logger.info("Connecting to PostgreSQL database...")
            self.postgres_conn = psycopg2.connect(
                self.postgres_url,
                cursor_factory=RealDictCursor
            )
            logger.info("[SUCCESS] PostgreSQL connection established")
            
            logger.info("Connecting to Upstash Vector database...")
            self.vector_index = Index(
                url=self.vector_url,
                token=self.vector_token
            )
            
            # Test vector connection
            info = self.vector_index.info()
            logger.info(f"[SUCCESS] Upstash Vector connection established - Dimension: {info.dimension}, Vectors: {info.vector_count}")
            
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {str(e)}")
            raise
    
    def close_connections(self):
        """Close database connections"""
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("PostgreSQL connection closed")
    
    def load_and_validate_json(self, file_path: str) -> Dict[str, Any]:
        """Load and validate the mytwin.json file"""
        logger.info(f"Loading JSON data from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required sections
            required_sections = ['personalInfo', 'experience', 'skills', 'projects', 'education']
            missing_sections = [section for section in required_sections if section not in data]
            
            if missing_sections:
                logger.warning(f"Missing sections in JSON: {missing_sections}")
            
            logger.info(f"[SUCCESS] JSON data loaded successfully")
            logger.info(f"   - Experiences: {len(data.get('experience', []))}")
            logger.info(f"   - Skills: {len(data.get('skills', []))}")
            logger.info(f"   - Projects: {len(data.get('projects', []))}")
            logger.info(f"   - Education: {len(data.get('education', []))}")
            
            return data
            
        except FileNotFoundError:
            logger.error(f"[ERROR] JSON file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Invalid JSON format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Error loading JSON: {str(e)}")
            raise
    
    def insert_professional_data(self, personal_info: Dict[str, Any]) -> int:
        """Insert or update personal information into professionals table"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Extract contact information
            contact = personal_info.get('contact', {})
            email = contact.get('email')
            
            # First check if professional already exists
            check_query = "SELECT id FROM professionals WHERE email = %s"
            cursor.execute(check_query, (email,))
            existing = cursor.fetchone()
            
            if existing:
                professional_id = existing['id']
                logger.info(f"[INFO] Professional already exists (ID: {professional_id}), updating data...")
                
                # Update existing record
                update_query = """
                UPDATE professionals SET
                    name = %(name)s, title = %(title)s, location = %(location)s,
                    linkedin = %(linkedin)s, github = %(github)s, portfolio = %(portfolio)s,
                    summary = %(summary)s, elevator_pitch = %(elevator_pitch)s,
                    updated_at = NOW()
                WHERE id = %(prof_id)s
                """
                
                cursor.execute(update_query, {
                    'prof_id': professional_id,
                    'name': personal_info.get('name'),
                    'title': personal_info.get('title'),
                    'location': personal_info.get('location'),
                    'linkedin': contact.get('linkedin'),
                    'github': contact.get('github'),
                    'portfolio': contact.get('portfolio'),
                    'summary': personal_info.get('summary'),
                    'elevator_pitch': personal_info.get('elevator_pitch')
                })
                
                logger.info(f"[SUCCESS] Professional data updated (ID: {professional_id})")
                
            else:
                # Insert new record
                insert_query = """
                INSERT INTO professionals (
                    name, title, location, email, 
                    linkedin, github, portfolio,
                    summary, elevator_pitch,
                    created_at, updated_at
                ) VALUES (
                    %(name)s, %(title)s, %(location)s, %(email)s,
                    %(linkedin)s, %(github)s, %(portfolio)s,
                    %(summary)s, %(elevator_pitch)s,
                    NOW(), NOW()
                ) RETURNING id
                """
                
                cursor.execute(insert_query, {
                    'name': personal_info.get('name'),
                    'title': personal_info.get('title'),
                    'location': personal_info.get('location'),
                    'email': email,
                    'linkedin': contact.get('linkedin'),
                    'github': contact.get('github'),
                    'portfolio': contact.get('portfolio'),
                    'summary': personal_info.get('summary'),
                    'elevator_pitch': personal_info.get('elevator_pitch')
                })
                
                professional_id = cursor.fetchone()['id']
                logger.info(f"[SUCCESS] Professional data inserted (ID: {professional_id})")
                self.stats.professionals_inserted += 1
            
            self.postgres_conn.commit()
            return professional_id
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting/updating professional data: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def insert_experiences(self, experiences: List[Dict[str, Any]], professional_id: int):
        """Insert experience data (clear existing first)"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Clear existing experiences for this professional
            delete_query = "DELETE FROM experiences WHERE professional_id = %s"
            cursor.execute(delete_query, (professional_id,))
            logger.info(f"[INFO] Cleared existing experiences for professional {professional_id}")
            
            for exp in experiences:
                # Parse duration to extract dates
                duration = exp.get('duration', '')
                start_date, end_date, is_current = self.parse_duration(duration)
                
                insert_query = """
                INSERT INTO experiences (
                    professional_id, company, position,
                    start_date, end_date, is_current,
                    description, achievements, technologies,
                    skills_developed, impact, keywords,
                    created_at, updated_at
                ) VALUES (
                    %(prof_id)s, %(company)s, %(position)s,
                    %(start_date)s, %(end_date)s, %(is_current)s,
                    %(description)s, %(achievements)s, %(technologies)s,
                    %(skills_developed)s, %(impact)s, %(keywords)s,
                    NOW(), NOW()
                )
                """
                
                cursor.execute(insert_query, {
                    'prof_id': professional_id,
                    'company': exp.get('company'),
                    'position': exp.get('position'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_current': is_current,
                    'description': exp.get('description'),
                    'achievements': exp.get('achievements', []),  # Direct array, no JSON encoding
                    'technologies': exp.get('technologies', []),
                    'skills_developed': exp.get('skills_developed', []),
                    'impact': exp.get('impact'),
                    'keywords': exp.get('keywords', [])
                })
                
                self.stats.experiences_inserted += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] {len(experiences)} experiences inserted")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting experiences: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def insert_skills(self, skills: Dict[str, Any], professional_id: int):
        """Insert skills data (clear existing first)"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Clear existing skills for this professional
            delete_query = "DELETE FROM skills WHERE professional_id = %s"
            cursor.execute(delete_query, (professional_id,))
            logger.info(f"[INFO] Cleared existing skills for professional {professional_id}")
            
            # Process both technical and soft skills
            all_skills = []
            
            # Process technical skills
            if 'technical' in skills:
                for category_group in skills['technical']:
                    category = category_group.get('category', 'Technical')
                    for skill in category_group.get('skills', []):
                        all_skills.append({
                            'category': category,
                            'name': skill.get('name'),
                            'proficiency': skill.get('proficiency', 'Intermediate'),
                            'experience_years': skill.get('experience', ''),
                            'context': skill.get('context', ''),
                            'projects': skill.get('projects', []),
                            'is_technical': True,
                            'examples': []  # We can extract from context if needed
                        })
            
            # Process soft skills
            if 'soft_skills' in skills:
                for skill in skills['soft_skills']:
                    all_skills.append({
                        'category': 'Soft Skills',
                        'name': skill.get('skill', skill.get('name', '')),
                        'proficiency': 'Advanced',  # Assume advanced for soft skills
                        'experience_years': '',
                        'context': skill.get('evidence', ''),
                        'projects': [],
                        'is_technical': False,
                        'examples': skill.get('examples', [])
                    })
            
            for skill in all_skills:
                insert_query = """
                INSERT INTO skills (
                    professional_id, category, name,
                    proficiency, experience_years, context,
                    projects, is_technical, examples,
                    created_at, updated_at
                ) VALUES (
                    %(prof_id)s, %(category)s, %(name)s,
                    %(proficiency)s, %(experience_years)s, %(context)s,
                    %(projects)s, %(is_technical)s, %(examples)s,
                    NOW(), NOW()
                )
                """
                
                cursor.execute(insert_query, {
                    'prof_id': professional_id,
                    'category': skill['category'],
                    'name': skill['name'],
                    'proficiency': skill['proficiency'],
                    'experience_years': skill['experience_years'],
                    'context': skill['context'],
                    'projects': skill['projects'],  # Direct array, no JSON encoding
                    'is_technical': skill['is_technical'],
                    'examples': skill['examples']  # Direct array, no JSON encoding
                })
                
                self.stats.skills_inserted += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] {len(all_skills)} skills inserted")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting skills: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def insert_projects(self, projects: List[Dict[str, Any]], professional_id: int):
        """Insert projects data (clear existing first)"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Clear existing projects for this professional
            delete_query = "DELETE FROM projects WHERE professional_id = %s"
            cursor.execute(delete_query, (professional_id,))
            logger.info(f"[INFO] Cleared existing projects for professional {professional_id}")
            
            for project in projects:
                # Parse date range
                start_date, end_date = None, None
                if 'timeline' in project:
                    start_date, end_date, _ = self.parse_duration(project['timeline'])
                
                insert_query = """
                INSERT INTO projects (
                    professional_id, name, description,
                    role, technologies, outcomes,
                    challenges, demo_url, repository_url,
                    documentation_url, status, start_date, end_date,
                    created_at, updated_at
                ) VALUES (
                    %(prof_id)s, %(name)s, %(description)s,
                    %(role)s, %(technologies)s, %(outcomes)s,
                    %(challenges)s, %(demo_url)s, %(repository_url)s,
                    %(documentation_url)s, %(status)s, %(start_date)s, %(end_date)s,
                    NOW(), NOW()
                )
                """
                
                cursor.execute(insert_query, {
                    'prof_id': professional_id,
                    'name': project.get('name'),
                    'description': project.get('description'),
                    'role': project.get('role'),
                    'technologies': project.get('technologies', []),  # Direct array
                    'outcomes': project.get('achievements', []),  # Map achievements to outcomes
                    'challenges': project.get('challenges', []),  # Direct array
                    'demo_url': project.get('url'),
                    'repository_url': project.get('github'),
                    'documentation_url': project.get('documentation'),
                    'status': project.get('status', 'completed'),
                    'start_date': start_date,
                    'end_date': end_date
                })
                
                self.stats.projects_inserted += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] {len(projects)} projects inserted")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting projects: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def insert_education(self, education_list: List[Dict[str, Any]], professional_id: int):
        """Insert education data (clear existing first)"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Clear existing education for this professional
            delete_query = "DELETE FROM education WHERE professional_id = %s"
            cursor.execute(delete_query, (professional_id,))
            logger.info(f"[INFO] Cleared existing education for professional {professional_id}")
            
            for edu in education_list:
                # Parse graduation date
                graduation_date = None
                if 'graduation_date' in edu:
                    graduation_date = self.parse_date(edu['graduation_date'])
                
                insert_query = """
                INSERT INTO education (
                    professional_id, type, institution, degree_name,
                    field, graduation_date, gpa,
                    achievements, relevant_coursework, projects,
                    skills, status,
                    created_at, updated_at
                ) VALUES (
                    %(prof_id)s, %(type)s, %(institution)s, %(degree_name)s,
                    %(field)s, %(graduation)s, %(gpa)s,
                    %(achievements)s, %(coursework)s, %(projects)s,
                    %(skills)s, %(status)s,
                    NOW(), NOW()
                )
                """
                
                cursor.execute(insert_query, {
                    'prof_id': professional_id,
                    'type': 'degree',  # Default to degree
                    'institution': edu.get('institution'),
                    'degree_name': edu.get('degree'),
                    'field': edu.get('field_of_study'),
                    'graduation': graduation_date,
                    'gpa': edu.get('gpa'),
                    'achievements': edu.get('honors_awards', []),  # Direct array
                    'coursework': edu.get('relevant_coursework', []),  # Direct array
                    'projects': edu.get('thesis_projects', []),  # Direct array
                    'skills': edu.get('skills', []),  # Direct array
                    'status': 'completed'  # Default to completed
                })
                
                self.stats.education_inserted += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] {len(education_list)} education records inserted")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting education: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def insert_json_content(self, json_data: Dict[str, Any], professional_id: int) -> int:
        """Insert or update complete JSON document"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # Generate content hash for deduplication
            import hashlib
            content_str = json.dumps(json_data, sort_keys=True)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Check if content already exists for this professional
            check_query = "SELECT id FROM json_content WHERE professional_id = %s AND version = 'v1'"
            cursor.execute(check_query, (professional_id,))
            existing = cursor.fetchone()
            
            if existing:
                content_id = existing['id']
                logger.info(f"[INFO] JSON content already exists (ID: {content_id}), updating...")
                
                # Update existing record
                update_query = """
                UPDATE json_content SET
                    content = %s,
                    content_hash = %s,
                    validation_status = 'valid',
                    created_at = NOW()
                WHERE id = %s
                """
                
                cursor.execute(update_query, (json.dumps(json_data), content_hash, content_id))
                
            else:
                # Insert new record
                insert_query = """
                INSERT INTO json_content (
                    professional_id, version, content, content_hash,
                    validation_status, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, NOW()
                ) RETURNING id
                """
                
                cursor.execute(insert_query, (
                    professional_id, 'v1', json.dumps(json_data), 
                    content_hash, 'valid'
                ))
                
                content_id = cursor.fetchone()['id']
                self.stats.json_content_inserted += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] JSON content processed (ID: {content_id})")
            return content_id
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting JSON content: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def create_content_chunks(self, json_data: Dict[str, Any], professional_id: int) -> List[ContentChunk]:
        """Create optimized content chunks for RAG retrieval"""
        chunks = []
        
        try:
            # Personal info chunk
            personal_info = json_data.get('personalInfo', {})
            if personal_info:
                content = f"""
                Professional Profile: {personal_info.get('name', '')}
                Title: {personal_info.get('title', '')}
                Location: {personal_info.get('location', '')}
                
                Summary: {personal_info.get('summary', '')}
                
                Elevator Pitch: {personal_info.get('elevator_pitch', '')}
                """.strip()
                
                chunks.append(ContentChunk(
                    content=content,
                    metadata={
                        'professional_id': professional_id,
                        'content_type': 'personal_info',
                        'name': personal_info.get('name'),
                        'title': personal_info.get('title')
                    },
                    chunk_type='personal_info',
                    importance='high',
                    keywords=['profile', 'summary', 'elevator pitch', 'professional']
                ))
            
            # Experience chunks
            for i, exp in enumerate(json_data.get('experience', [])):
                content = f"""
                Experience at {exp.get('company', '')}
                Position: {exp.get('position', '')}
                Duration: {exp.get('duration', '')}
                
                Description: {exp.get('description', '')}
                
                Key Achievements:
                {chr(10).join(f'- {achievement}' for achievement in exp.get('achievements', []))}
                
                Technologies: {', '.join(exp.get('technologies', []))}
                
                Skills Developed: {', '.join(exp.get('skills_developed', []))}
                
                Impact: {exp.get('impact', '')}
                """.strip()
                
                chunks.append(ContentChunk(
                    content=content,
                    metadata={
                        'professional_id': professional_id,
                        'content_type': 'experience',
                        'company': exp.get('company'),
                        'position': exp.get('position'),
                        'duration': exp.get('duration'),
                        'index': i
                    },
                    chunk_type='experience',
                    importance='high' if i < 3 else 'medium',  # Recent experiences more important
                    keywords=exp.get('keywords', []) + ['experience', 'work', exp.get('company', '').lower()],
                    date_context=exp.get('duration')
                ))
            
            # Skills chunks - group by category
            skills_data = json_data.get('skills', {})
            
            # Process technical skills
            if 'technical' in skills_data:
                for category_group in skills_data['technical']:
                    category = category_group.get('category', 'Technical')
                    skills_in_category = category_group.get('skills', [])
                    
                    content = f"""
                    {category} Skills:
                    
                    {chr(10).join(f'- {skill.get("name", "")} ({skill.get("proficiency", "")}) - {skill.get("experience", "N/A")} experience' for skill in skills_in_category)}
                    
                    Context and Examples:
                    {chr(10).join(f'- {skill.get("name", "")}: {skill.get("context", "")}' for skill in skills_in_category if skill.get("context"))}
                    """.strip()
                    
                    chunks.append(ContentChunk(
                        content=content,
                        metadata={
                            'professional_id': professional_id,
                            'content_type': 'skills',
                            'category': category,
                            'skill_count': len(skills_in_category)
                        },
                        chunk_type='skills',
                        importance='high',
                        keywords=['skills', category.lower(), 'expertise'] + [skill.get('name', '').lower() for skill in skills_in_category]
                    ))
            
            # Process soft skills
            if 'soft_skills' in skills_data:
                soft_skills = skills_data['soft_skills']
                content = f"""
                Soft Skills:
                
                {chr(10).join(f'- {skill.get("skill", "")}' for skill in soft_skills)}
                
                Examples and Context:
                {chr(10).join(f'- {skill.get("skill", "")}: {", ".join(skill.get("examples", []))}' for skill in soft_skills if skill.get("examples"))}
                """.strip()
                
                chunks.append(ContentChunk(
                    content=content,
                    metadata={
                        'professional_id': professional_id,
                        'content_type': 'skills',
                        'category': 'Soft Skills',
                        'skill_count': len(soft_skills)
                    },
                    chunk_type='skills',
                    importance='medium',
                    keywords=['skills', 'soft skills', 'interpersonal'] + [skill.get('skill', '').lower() for skill in soft_skills]
                ))
            
            # Project chunks
            for i, project in enumerate(json_data.get('projects', [])):
                content = f"""
                Project: {project.get('name', '')}
                Type: {project.get('type', '')}
                Status: {project.get('status', '')}
                
                Description: {project.get('description', '')}
                
                Technologies: {', '.join(project.get('technologies', []))}
                
                Role: {project.get('role', '')}
                
                Achievements:
                {chr(10).join(f'- {achievement}' for achievement in project.get('achievements', []))}
                
                Team Size: {project.get('team_size', 'N/A')}
                """.strip()
                
                chunks.append(ContentChunk(
                    content=content,
                    metadata={
                        'professional_id': professional_id,
                        'content_type': 'project',
                        'project_name': project.get('name'),
                        'project_type': project.get('type'),
                        'status': project.get('status'),
                        'index': i
                    },
                    chunk_type='project',
                    importance='high' if project.get('status') == 'completed' else 'medium',
                    keywords=['project', 'portfolio'] + project.get('technologies', []) + [project.get('name', '').lower()],
                    date_context=project.get('timeline')
                ))
            
            # Education chunks
            for i, edu in enumerate(json_data.get('education', [])):
                content = f"""
                Education: {edu.get('degree', '')} in {edu.get('field_of_study', '')}
                Institution: {edu.get('institution', '')}
                Graduation: {edu.get('graduation_date', '')}
                GPA: {edu.get('gpa', 'N/A')}
                
                Relevant Coursework: {', '.join(edu.get('relevant_coursework', []))}
                
                Thesis/Projects:
                {chr(10).join(f'- {project}' for project in edu.get('thesis_projects', []))}
                
                Honors & Awards: {', '.join(edu.get('honors_awards', []))}
                
                Activities: {', '.join(edu.get('activities', []))}
                """.strip()
                
                chunks.append(ContentChunk(
                    content=content,
                    metadata={
                        'professional_id': professional_id,
                        'content_type': 'education',
                        'institution': edu.get('institution'),
                        'degree': edu.get('degree'),
                        'field': edu.get('field_of_study'),
                        'index': i
                    },
                    chunk_type='education',
                    importance='medium',
                    keywords=['education', 'degree', 'university', edu.get('institution', '').lower(), edu.get('field_of_study', '').lower()],
                    date_context=edu.get('graduation_date')
                ))
            
            logger.info(f"[SUCCESS] Created {len(chunks)} content chunks for RAG")
            return chunks
            
        except Exception as e:
            logger.error(f"[ERROR] Error creating content chunks: {str(e)}")
            self.stats.errors_encountered += 1
            raise
    
    def insert_content_chunks(self, chunks: List[ContentChunk], professional_id: int):
        """Insert content chunks into database"""
        try:
            cursor = self.postgres_conn.cursor()
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"chunk-{professional_id}-{chunk.chunk_type}-{i}"
                
                insert_query = """
                INSERT INTO content_chunks (
                    professional_id, chunk_id, type,
                    title, content, category,
                    tags, importance, date_range,
                    relevance_score, vector_id, embedding_model,
                    created_at, updated_at
                ) VALUES (
                    %(professional_id)s, %(chunk_id)s, %(type)s,
                    %(title)s, %(content)s, %(category)s,
                    %(tags)s, %(importance)s, %(date_range)s,
                    %(relevance_score)s, %(vector_id)s, %(embedding_model)s,
                    NOW(), NOW()
                ) RETURNING id
                """
                
                # Generate title from content type and metadata
                title = f"{chunk.chunk_type.title()}"
                if chunk.chunk_type == 'experience':
                    title = f"Experience at {chunk.metadata.get('company', 'Unknown')}"
                elif chunk.chunk_type == 'project':
                    title = f"Project: {chunk.metadata.get('project_name', 'Unknown')}"
                elif chunk.chunk_type == 'skills':
                    title = f"{chunk.metadata.get('category', 'General')} Skills"
                elif chunk.chunk_type == 'education':
                    title = f"Education at {chunk.metadata.get('institution', 'Unknown')}"
                elif chunk.chunk_type == 'personal_info':
                    title = f"Professional Profile"
                
                cursor.execute(insert_query, {
                    'professional_id': professional_id,
                    'chunk_id': chunk_id,
                    'type': chunk.chunk_type,
                    'title': title,
                    'content': chunk.content,
                    'category': chunk.metadata.get('content_type', chunk.chunk_type),
                    'tags': chunk.keywords,  # Direct array
                    'importance': chunk.importance,
                    'date_range': chunk.date_context,
                    'relevance_score': 1.0,  # Default high relevance
                    'vector_id': f"upstash-{chunk_id}",  # Will be used in vector store
                    'embedding_model': 'mixbread-large'
                })
                
                db_chunk_id = cursor.fetchone()['id']
                # Store DB chunk_id back in metadata for vector embedding
                chunk.metadata['chunk_id'] = db_chunk_id
                chunk.metadata['vector_id'] = f"upstash-{chunk_id}"
                
                self.stats.content_chunks_created += 1
            
            self.postgres_conn.commit()
            logger.info(f"[SUCCESS] {len(chunks)} content chunks inserted into database")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inserting content chunks: {str(e)}")
            self.postgres_conn.rollback()
            self.stats.errors_encountered += 1
            raise
    
    def generate_vector_embeddings(self, chunks: List[ContentChunk]):
        """Generate and store vector embeddings using Upstash Vector"""
        try:
            # First, clear all existing vectors for this professional
            try:
                # Get current vector info
                info = self.vector_index.info()
                if info.vector_count > 0:
                    logger.info(f"[INFO] Clearing {info.vector_count} existing vectors...")
                    # Reset the entire index (Upstash doesn't support selective delete by metadata)
                    self.vector_index.reset()
                    logger.info("[INFO] Existing vectors cleared")
            except Exception as e:
                logger.warning(f"[WARNING] Could not clear existing vectors: {str(e)}")
            
            vectors_to_upsert = []
            batch_size = 10  # Process in batches for efficiency
            
            for chunk in chunks:
                # Create vector for Upstash
                vector = Vector(
                    id=chunk.metadata['vector_id'],  # Use the vector_id we generated
                    data=chunk.content,  # Upstash will auto-generate embedding
                    metadata={
                        **chunk.metadata,
                        'chunk_type': chunk.chunk_type,
                        'importance': chunk.importance,
                        'keywords': chunk.keywords,
                        'date_context': chunk.date_context,
                        'created_at': datetime.now().isoformat()
                    }
                )
                vectors_to_upsert.append(vector)
                
                # Process in batches
                if len(vectors_to_upsert) >= batch_size:
                    self._upsert_vector_batch(vectors_to_upsert)
                    vectors_to_upsert = []
            
            # Process remaining vectors
            if vectors_to_upsert:
                self._upsert_vector_batch(vectors_to_upsert)
            
            logger.info(f"[SUCCESS] {self.stats.vectors_embedded} vector embeddings generated and stored")
            
        except Exception as e:
            logger.error(f"[ERROR] Error generating vector embeddings: {str(e)}")
            self.stats.errors_encountered += 1
            raise
    
    def _upsert_vector_batch(self, vectors: List[Vector]):
        """Upsert a batch of vectors with retry logic"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                result = self.vector_index.upsert(vectors=vectors)
                self.stats.vectors_embedded += len(vectors)
                logger.info(f"   Batch of {len(vectors)} vectors upserted successfully")
                return result
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"   Retry {attempt + 1}/{max_retries} for vector batch (error: {str(e)})")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"   Failed to upsert vector batch after {max_retries} attempts: {str(e)}")
                    raise
    
    def parse_duration(self, duration_str: str) -> Tuple[Optional[datetime], Optional[datetime], bool]:
        """Parse duration string to extract start/end dates"""
        try:
            if not duration_str:
                return None, None, False
            
            # Handle "Present" or "Current"
            is_current = 'present' in duration_str.lower() or 'current' in duration_str.lower()
            
            # Simple parsing for "YYYY-MM – YYYY-MM" or "YYYY-MM – Present"
            parts = duration_str.replace('–', '-').replace('—', '-').split(' - ')
            if len(parts) >= 2:
                start_str = parts[0].strip()
                end_str = parts[1].strip()
                
                start_date = self.parse_date(start_str)
                end_date = None if is_current else self.parse_date(end_str)
                
                return start_date, end_date, is_current
            
            return None, None, False
            
        except Exception as e:
            logger.warning(f"Could not parse duration '{duration_str}': {str(e)}")
            return None, None, False
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        # Common date formats
        formats = ['%Y-%m', '%Y/%m', '%m/%Y', '%Y', '%B %Y', '%b %Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def log_final_stats(self):
        """Log final migration statistics"""
        self.stats.end_time = datetime.now()
        duration = (self.stats.end_time - self.stats.start_time).total_seconds()
        
        logger.info("="*60)
        logger.info("[MIGRATION COMPLETE] FINAL STATISTICS")
        logger.info("="*60)
        logger.info(f"Total Duration: {duration:.2f} seconds")
        logger.info(f"Professionals: {self.stats.professionals_inserted}")
        logger.info(f"Experiences: {self.stats.experiences_inserted}")
        logger.info(f"Skills: {self.stats.skills_inserted}")
        logger.info(f"Projects: {self.stats.projects_inserted}")
        logger.info(f"Education: {self.stats.education_inserted}")
        logger.info(f"JSON Content: {self.stats.json_content_inserted}")
        logger.info(f"Content Chunks: {self.stats.content_chunks_created}")
        logger.info(f"Vector Embeddings: {self.stats.vectors_embedded}")
        logger.info(f"Errors: {self.stats.errors_encountered}")
        
        if self.stats.errors_encountered == 0:
            logger.info("[SUCCESS] MIGRATION SUCCESSFUL - All data migrated without errors!")
        else:
            logger.warning(f"[WARNING] MIGRATION COMPLETED WITH {self.stats.errors_encountered} ERRORS")
        
        logger.info("="*60)

def main():
    """Main migration execution"""
    logger.info("[START] Starting Digital Twin Data Migration")
    logger.info("="*60)
    
    # Check for required files
    json_file_path = 'data/mytwin.json'
    if not Path(json_file_path).exists():
        logger.error(f"[ERROR] Required file not found: {json_file_path}")
        sys.exit(1)
    
    try:
        with DigitalTwinMigrator() as migrator:
            # Load and validate JSON data
            json_data = migrator.load_and_validate_json(json_file_path)
            
            # Insert professional data
            professional_id = migrator.insert_professional_data(json_data['personalInfo'])
            
            # Insert related data
            if 'experience' in json_data:
                migrator.insert_experiences(json_data['experience'], professional_id)
            
            if 'skills' in json_data:
                migrator.insert_skills(json_data['skills'], professional_id)
            
            if 'projects' in json_data:
                migrator.insert_projects(json_data['projects'], professional_id)
            
            if 'education' in json_data:
                migrator.insert_education(json_data['education'], professional_id)
            
            # Insert complete JSON document
            content_id = migrator.insert_json_content(json_data, professional_id)
            
            # Create and insert content chunks
            chunks = migrator.create_content_chunks(json_data, professional_id)
            migrator.insert_content_chunks(chunks, professional_id)
            
            # Generate vector embeddings
            migrator.generate_vector_embeddings(chunks)
            
            logger.info("[SUCCESS] Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"[ERROR] Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()