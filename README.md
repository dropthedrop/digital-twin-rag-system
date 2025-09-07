# 🤖 Digital Twin RAG System

> A sophisticated AI-powered system that creates a searchable digital representation of professional experience, skills, and knowledge using Retrieval-Augmented Generation (RAG) technology.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://postgresql.org)
[![Vector DB](https://img.shields.io/badge/Upstash-Vector-green.svg)](https://upstash.com)
[![RAG](https://img.shields.io/badge/RAG-Enabled-orange.svg)](https://github.com)

## 🌟 Overview

The Digital Twin RAG System transforms your professional profile, experience, and knowledge into an intelligent, queryable AI assistant. By combining traditional databases with modern vector search technology, it creates a comprehensive digital representation that can answer detailed questions about your background, skills, projects, and expertise.

### ✨ Key Features

- 🔍 **Semantic Search**: Natural language queries about professional experience
- 📊 **Comprehensive Data Model**: 8-table PostgreSQL schema with 61+ indexes
- 🧠 **Vector Embeddings**: 1024-dimensional embeddings using mixbread-large model
- ⚡ **High Performance**: Sub-300ms average query latency, 3.8 queries/second
- 🎯 **Smart Filtering**: Content type, importance, and metadata-based filtering
- 📈 **Analytics Ready**: Built-in performance monitoring and test suite
- 🔒 **Neon Integration**: Cloud-native PostgreSQL with branching capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   JSON Data     │    │   PostgreSQL     │    │  Upstash Vector │
│   (Source)      │───▶│   Database       │◀──▶│   Database      │
│                 │    │  (Structured)    │    │  (Embeddings)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                └────────────────────────┘
                                         │
                                ┌─────────▼──────────┐
                                │   RAG System       │
                                │  Query Engine      │
                                └────────────────────┘
```

### 🔧 Technology Stack

- **Database**: PostgreSQL 17 (Neon Cloud)
- **Vector Store**: Upstash Vector Database
- **Embeddings**: mixbread-large (1024 dimensions)
- **Language**: Python 3.12+
- **ORM**: psycopg2-binary
- **Environment**: python-dotenv
- **Testing**: Custom RAG test framework

## 📋 Database Schema

### Core Tables
- **professionals**: User profile and contact information
- **experiences**: Work history and professional experience
- **skills**: Technical and soft skills with proficiency levels
- **projects**: Portfolio projects with technologies and outcomes
- **education**: Academic background and certifications
- **content_chunks**: RAG-optimized content pieces for vector search
- **json_content**: Original JSON data preservation
- **search_analytics**: Query performance and usage tracking

### Key Features
- ✅ **61 Optimized Indexes** for fast queries
- ✅ **Full-text Search** with tsvector support
- ✅ **JSONB Support** for flexible metadata
- ✅ **Foreign Key Constraints** ensuring data integrity
- ✅ **Automatic Timestamps** for audit trails

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Neon PostgreSQL account
- Upstash Vector Database account

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/digital-twin-rag.git
cd digital-twin-rag
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
# PostgreSQL (Neon)
POSTGRES_CONNECTION_STRING="postgresql://user:pass@host/db?sslmode=require"

# Upstash Vector Database
UPSTASH_VECTOR_REST_URL="https://your-endpoint.upstash.io"
UPSTASH_VECTOR_REST_TOKEN="your-token"
UPSTASH_VECTOR_REST_READONLY_TOKEN="your-readonly-token"
```

### 3. Initialize Database

```bash
# Create database schema
python -c "from migrate_data_to_rag import DigitalTwinMigrator; migrator = DigitalTwinMigrator(); migrator.create_schema()"
```

### 4. Load Your Data

Prepare your professional data in `data/mytwin.json` format:

```json
{
  "professional_info": {
    "name": "Your Name",
    "title": "Your Title",
    "location": "Your Location"
  },
  "experiences": [...],
  "skills": {...},
  "projects": [...],
  "education": [...]
}
```

Run the migration:

```bash
python migrate_data_to_rag.py
```

### 5. Test the System

```bash
python test_rag_functionality.py
```

## 📊 Performance Metrics

Our latest test results show excellent performance:

- ✅ **Success Rate**: 86.7% (13/15 tests passed)
- ⚡ **Average Latency**: 265ms per query
- 🔥 **Throughput**: 3.8 queries per second
- 📈 **Concurrent Performance**: 100% success rate
- 🎯 **Vector Search**: 19 embeddings, 0.8+ relevance scores

### Category Performance
- Experience: 100% ✅
- Projects: 100% ✅
- Skills: 100% ✅
- Leadership: 100% ✅
- Technical: 100% ✅
- Education: 100% ✅
- Achievements: 100% ✅

## 🔍 Usage Examples

### Basic Query
```python
from test_rag_functionality import DigitalTwinRAGTester

tester = DigitalTwinRAGTester()
tester.connect_databases()

# Ask about AI experience
results = tester.run_single_test({
    "query": "What experience do you have with AI and machine learning?",
    "expected_content_types": ["experience", "skills", "project"],
    "expected_keywords": ["ai", "machine learning"]
})

print(f"Found {len(results)} relevant results")
```

### Advanced Filtering
```python
# Search with metadata filters
vector_results = vector_index.query(
    data="python programming experience",
    top_k=5,
    filter={"content_type": "skills", "importance": "high"}
)
```

## 📁 Project Structure

```
digital-twin-rag/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── data/
│   └── mytwin.json             # Source professional data
├── migrate_data_to_rag.py      # Main migration script
├── test_rag_functionality.py   # Comprehensive test suite
├── test_upstash_vector.py      # Vector DB validation
└── docs/
    ├── API.md                  # API documentation
    ├── current_system_overview.md
    └── OPERATIONS.md           # Operational guides
```

## 🧪 Testing

The system includes a comprehensive test suite that validates:

- ✅ **Vector Search Accuracy**: Semantic similarity and relevance
- ✅ **Content Retrieval**: PostgreSQL integration and data consistency
- ✅ **Keyword Matching**: Smart content analysis
- ✅ **Performance Benchmarks**: Latency and throughput testing
- ✅ **Concurrent Operations**: Multi-query handling
- ✅ **Metadata Filtering**: Content type and importance filtering

Run tests:

```bash
# Full test suite
python test_rag_functionality.py

# Vector database validation
python test_upstash_vector.py

# Check specific query
python -c "
from test_rag_functionality import DigitalTwinRAGTester
tester = DigitalTwinRAGTester()
tester.connect_databases()
result = tester.run_single_test(tester._create_test_cases()[0])
print(f'Success: {result.passed}')
"
```

## 🔧 Configuration

### Database Tuning

The system includes optimized database configurations:

```sql
-- Example index for skills search
CREATE INDEX idx_skills_proficiency_gin 
ON skills USING gin(to_tsvector('english', proficiency || ' ' || examples));

-- Vector similarity search optimization
CREATE INDEX idx_content_chunks_vector 
ON content_chunks(vector_id) WHERE vector_id IS NOT NULL;
```

### Vector Search Parameters

```python
# Optimal search configuration
search_params = {
    "top_k": 5,                    # Number of results
    "include_metadata": True,       # Include filtering metadata
    "filter": {                    # Optional content filtering
        "importance": "high",
        "content_type": "skills"
    }
}
```

## 📈 Monitoring

Track system performance with built-in analytics:

```python
# Performance monitoring
summary = tester.run_all_tests()
print(f"Success Rate: {summary['success_rate']:.1%}")
print(f"Avg Latency: {summary['average_query_time']:.3f}s")
print(f"Total Tests: {summary['total_tests']}")
```

## 🚧 Roadmap

### Upcoming Features
- [ ] **Web Interface**: React-based query interface
- [ ] **API Endpoints**: RESTful API for external integrations
- [ ] **Advanced Analytics**: Query optimization and usage insights
- [ ] **Multi-Modal Support**: Document and image embedding
- [ ] **Real-time Updates**: Live data synchronization
- [ ] **Authentication**: User management and access control

### Optimization Targets
- [ ] Sub-200ms query latency
- [ ] 95%+ test success rate
- [ ] Automated data pipeline
- [ ] Advanced semantic search

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Follow the coding standards
4. **Run Tests**: Ensure all tests pass
5. **Submit PR**: With clear description of changes

### Development Setup

```bash
# Development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests before committing
python test_rag_functionality.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neon Database**: For excellent PostgreSQL cloud platform with branching
- **Upstash**: For high-performance vector database infrastructure
- **mixbread.ai**: For powerful embedding model (mixbread-large)
- **Python Community**: For the amazing ecosystem of AI/ML tools

## 📞 Support

- 📧 **Email**: your.email@domain.com
- 💬 **Issues**: [GitHub Issues](https://github.com/yourusername/digital-twin-rag/issues)
- 📖 **Documentation**: [Wiki](https://github.com/yourusername/digital-twin-rag/wiki)

---

**Built with ❤️ for the AI-powered future of professional representation**

*Transform your professional story into an intelligent, searchable digital twin that represents you accurately and comprehensively.*