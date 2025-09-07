-- Digital Twin Sample Data Insertion Script
-- This script inserts the mytwin.json data into the database

-- First, get the professional_id for reference
-- professional_id = 'c6a93c28-904d-49b4-80f2-be7b04c0e2d4'

-- Insert full JSON content
INSERT INTO json_content (professional_id, version, content, content_hash, validation_status)
VALUES ('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', '1.0', 
'$(cat c:\Users\ALEKO\projects\DigTwin\data\mytwin.json)'::jsonb,
encode(sha256('$(cat c:\Users\ALEKO\projects\DigTwin\data\mytwin.json)'::bytea), 'hex'),
'valid');

-- Insert experiences
INSERT INTO experiences (professional_id, company, position, duration, is_current, description, achievements, technologies, skills_developed, impact, keywords, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'ServiceNow', 'Software Engineer / DevOps (Big Data & Analytics)', '2024-07 – Present', true, 
 'Infrastructure Operations within a custom private cloud environment. Full-stack infra ownership across runtimes, data stores, IaC, CI/CD, observability, and security. Builds internal tools and automations; operates in regulated environments with strict compliance.',
 ARRAY['Reduced manual toil and improved security by fully automating Splunk API access token rotations.', 'Accelerated vulnerability remediation by automating Tomcat upgrades across estates.', 'Stabilised Kafka HA operations and unblocked critical incidents through coordinated response and research-driven improvements.'],
 ARRAY['Custom Private Cloud', 'Linux', 'Python', 'Bash', 'Ansible', 'Kafka', 'Cloudera', 'Tomcat', 'GitLab/GitHub/Jenkins', 'Docker', 'Kubernetes', 'Terraform', 'Observability (Prometheus/Grafana/Elastic/Splunk)', 'Secrets Management / KMS', 'mTLS', 'WAF'],
 ARRAY['Incident response and on-call readiness', 'Security automation and key/token rotation', 'Upgrade orchestration at scale', 'Access management and compliance operations'],
 'Improved platform security posture, shortened remediation cycles, and reduced repetitive work for engineers; increased resilience of Kafka clusters in production.',
 ARRAY['DevOps', 'Infrastructure Operations', 'Private Cloud', 'Kafka', 'Ansible', 'Automation', 'Security', 'Token Rotation', 'Cloudera', 'Tomcat'], 1),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'AusBiz Consulting', 'DevOps / Full‑stack Engineer (Intern)', '2023 – 2024', false,
 'Delivered an AI‑driven resume builder; implemented CI/CD with environment gating and automated linting; deployed to AWS with high availability.',
 ARRAY['Launched and maintained AI resume builder in production on AWS.', 'Implemented GitHub-based CI/CD with auto-rollback to previous version for reliability.'],
 ARRAY['AWS', 'PostgreSQL', 'React', 'AdonisJS', 'JavaScript', 'TypeScript', 'GitHub Actions'],
 ARRAY['JavaScript/TypeScript proficiency', 'Cloud deployment', 'CI/CD automation', 'Monitoring and rollback practices'],
 'Improved delivery cadence and reliability for a production web application on AWS.',
 ARRAY['AWS', 'React', 'PostgreSQL', 'CI/CD', 'GitHub Actions', 'AI Resume Builder'], 2),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Hospitality Sector', 'Manager', 'N/A', false,
 'Led operations and staff in hospitality settings with a strong emphasis on customer service and conflict resolution.',
 ARRAY['Maintained high customer satisfaction during peak trading periods.', 'Resolved staff and customer conflicts while sustaining service standards.'],
 ARRAY[]::text[],
 ARRAY['Customer service', 'Conflict resolution', 'Shift management', 'Team leadership'],
 'Improved staff coordination and guest experience in high-pressure environments.',
 ARRAY['Customer Service', 'Team Leadership', 'Operations'], 3),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Construction (Steel Fixing)', 'Team Leader', 'N/A', false,
 'Coordinated crews in physically demanding environments with strong focus on order, safety, and delivery timelines.',
 ARRAY['Maintained site safety protocols while coordinating multiple crews.', 'Delivered sections to plan by enforcing sequencing and quality checks.'],
 ARRAY[]::text[],
 ARRAY['Safety leadership', 'Crew coordination', 'Scheduling', 'Decision-making under pressure'],
 'Enhanced discipline and reliability on site, ensuring deliverables met sequencing and safety constraints.',
 ARRAY['Safety', 'Leadership', 'Coordination'], 4);

-- Insert technical skills
INSERT INTO skills (professional_id, category, name, proficiency, experience_years, context, projects, is_technical, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Programming Languages', 'Python', 'Advanced', '9 years', 'Automation, tooling, gateways, SDKs', ARRAY['CryptoGent', 'RAGFOOD', 'Infra tools'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Programming Languages', 'JavaScript/TypeScript', 'Advanced', '9 years', 'Full‑stack apps, Next.js dashboard, CI tooling', ARRAY['AusBiz Resume Builder', 'CryptoGent Console'], true, 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Programming Languages', 'Bash', 'Advanced', '9 years', 'Ops scripts, CI/CD, containers', ARRAY['Infra operations'], true, 3),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Cloud & Infra', 'AWS (EC2, RDS, S3, Secrets Manager, KMS, Elastic Beanstalk, Elasticache, ALB/WAF)', 'Advanced', '5+ years', 'End‑to‑end deployments, HA, rollbacks', ARRAY['AusBiz Resume Builder', 'CryptoGent (Dev/Stage)'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Cloud & Infra', 'Custom Private Cloud', 'Advanced', 'Current', 'Enterprise infra ops, regulated environments', ARRAY['ServiceNow (Big Data & Analytics)'], true, 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'DevOps & Platforms', 'Docker & Kubernetes', 'Advanced', '5+ years', 'Packaging, deployment, scaling, HPA', ARRAY['CryptoGent', 'Infra ops'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'DevOps & Platforms', 'Terraform & Ansible', 'Advanced', '5+ years', 'IaC + config management, automated upgrades', ARRAY['Tomcat upgrade automation'], true, 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'DevOps & Platforms', 'Jenkins / GitLab / GitHub Actions', 'Advanced', '5+ years', 'CI/CD pipelines, quality gates, rollbacks', ARRAY['Multiple'], true, 3),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Data & AI', 'Vector Databases', 'Intermediate‑Advanced', '2+ years', 'RAG, context stores', ARRAY['RAGFOOD'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Data & AI', 'Embeddings & RAG frameworks', 'Intermediate‑Advanced', '2+ years', 'MCP to cloud migration', ARRAY['RAGFOOD'], true, 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Security', 'mTLS, DPoP, capability tokens', 'Intermediate‑Advanced', 'Current', 'Planned/implemented in gateways', ARRAY['CryptoGent'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Security', 'Secrets/KMS, key rotation, WAF', 'Advanced', '5+ years', 'Enterprise ops & automation', ARRAY['ServiceNow', 'AusBiz'], true, 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Web / Frontend', 'React / Next.js', 'Advanced', '3+ years', 'Admin dashboards, product UIs', ARRAY['CryptoGent Console', 'AusBiz Resume Builder'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Blockchain', 'EVM, Foundry/Hardhat', 'Intermediate', '1–2 years', 'Contracts & testnets', ARRAY['CryptoGent'], true, 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Blockchain', 'Base (OP Stack), BLS/ECDSA basics', 'Intermediate', '1–2 years', 'Oracle thresholds, receipts', ARRAY['CryptoGent'], true, 2);

-- Insert soft skills  
INSERT INTO skills (professional_id, category, name, proficiency, experience_years, context, projects, is_technical, examples, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Soft Skills', 'Customer Service & Conflict Resolution', 'Advanced', 'Multiple years', 'Hospitality management', ARRAY[]::text[], false, ARRAY['Handled difficult patrons and peak loads as a hospitality manager; maintained service KPIs.'], 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Soft Skills', 'Team Leadership under Pressure', 'Advanced', 'Multiple years', 'Construction leadership', ARRAY[]::text[], false, ARRAY['Coordinated steel-fixing crews while enforcing sequencing and safety.'], 2),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Soft Skills', 'Incident Response & Ownership', 'Advanced', 'Current', 'Production operations', ARRAY[]::text[], false, ARRAY['Led Kafka HA recovery efforts; coordinated stakeholders to avert major outage.'], 3),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Soft Skills', 'Cross‑functional Communication', 'Advanced', 'Current', 'Enterprise change windows', ARRAY[]::text[], false, ARRAY['Explained risk and remediation plans to non‑technical stakeholders during upgrades.'], 4),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Soft Skills', 'Adaptability', 'Advanced', 'Multiple years', 'Career planning', ARRAY[]::text[], false, ARRAY['Shifted study plans due to role demands while continuing professional growth via projects.'], 5);

-- Insert projects
INSERT INTO projects (professional_id, name, description, role, technologies, outcomes, challenges, repository_url, status, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'CryptoGent — Tokenised API Calls for AI', 'Enterprise system that tokenises API calls with verifiable usage receipts, programmable credits, and chain‑anchored, per‑call authorization.', 'Founder / Architect / Full‑stack Engineer',
 ARRAY['TypeScript', 'Node.js', 'Fastify', 'Next.js', 'Docker', 'Redis', 'PostgreSQL', 'OpenTelemetry', 'Prometheus/Grafana', 'Solidity/Foundry', 'Base (OP Stack)'],
 ARRAY['Local demo flows (quote → lock → execute) operational', 'Docs A–E authored', 'Deployment & scaling playbook drafted'],
 ARRAY['Designing per‑call cryptographic auth without per‑call chain latency', 'Interoperability across providers'],
 'https://github.com/dropthedrop/', 'completed', 1),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'RAGFOOD — Cloud MCP Migration', 'Migrated a local MCP with food context into a cloud-native stack using Vector DB and AI Gateway; improved availability and maintainability.', 'Developer',
 ARRAY['Python', 'Vector DB', 'Embeddings', 'Vercel', 'Gateway'],
 ARRAY['End‑to‑end migration from local to cloud', 'Operational RAG serving'],
 ARRAY['Index design and cost/latency balances', 'Context freshness management'],
 '', 'completed', 2),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'Digital Twin — Personal AI Context', 'A self‑representation AI twin that answers questions based on curated, privacy‑controlled personal data and projects.', 'Designer / Builder',
 ARRAY['TypeScript/Python', 'Vector DB', 'Embeddings', 'Gateway/Orchestrator'],
 ARRAY['Initial context schema and ingestion plan', 'Narratives and profile assembled'],
 ARRAY['Data boundaries and redaction rules', 'Policy engine for safe responses'],
 '', 'in_progress', 3),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'AI Resume Builder — AusBiz', 'A production web app for generating and managing resumes with AI assistance deployed on AWS with HA and CI/CD.', 'Full‑stack / DevOps Intern',
 ARRAY['React', 'AdonisJS', 'PostgreSQL', 'AWS', 'GitHub Actions'],
 ARRAY['Production launch with auto‑rollback CI/CD'],
 ARRAY['Quality gates and deployment safety', 'Performance & availability'],
 '', 'completed', 4);

-- Insert education
INSERT INTO education (professional_id, type, institution, degree_name, field, graduation_date, status, relevant_coursework, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'certificate', 'Charles Sturt University', 'Graduate Certificate in Computing', 'Cloud Computing', NULL, 'completed', ARRAY['Cloud Computing', 'Virtualisation'], 1),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'degree', 'Charles Sturt University', 'Master of Cloud Computing & Virtualisation', 'Cloud Computing & Virtualisation', NULL, 'on_hold', ARRAY['Advanced Cloud Architecture', 'Virtualisation'], 2);

-- Insert certifications
INSERT INTO education (professional_id, type, institution, degree_name, issuer, status, skills, display_order)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'certification', '', 'CompTIA Cloud Essentials+', 'CompTIA', 'completed', ARRAY['Cloud fundamentals', 'Business & cloud alignment'], 3),
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'certification', '', 'Data Analyst with AI', '', 'completed', ARRAY['Data analysis', 'AI-assisted insight generation'], 4);

-- Insert content chunks for RAG
INSERT INTO content_chunks (professional_id, chunk_id, type, title, content, category, tags, importance, date_range, relevance_score)
VALUES 
('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'chunk_experience_sn', 'experience', 'ServiceNow — Software Engineer/DevOps (Big Data & Analytics)', 'On-call, private cloud infra ops, Kafka/Cloudera/Tomcat upgrades, automation (Splunk token rotation, Tomcat upgrades), access management, regulated environments.', 'work_experience', ARRAY['DevOps', 'Private Cloud', 'Kafka', 'Automation', 'Security'], 'high', '2024-07 – Present', 1.0),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'chunk_project_cryptogent', 'project', 'CryptoGent — Tokenised API Calls for AI', 'Design and prototype of chain‑anchored per‑call authorization, credits, and verifiable usage receipts; gateway/oracle/SDK/console scaffolds with docs and deployment plan.', 'projects', ARRAY['AI', 'Blockchain', 'Authorization', 'Gateway', 'OP Stack'], 'high', '2025', 1.0),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'chunk_project_ragfood', 'project', 'RAGFOOD — MCP to Cloud Migration', 'Migrated local MCP to Vector DB + Gateway in cloud; improved availability and maintainability for food knowledge queries.', 'projects', ARRAY['RAG', 'Vector DB', 'Migration'], 'medium', '2024–2025', 0.8),

('c6a93c28-904d-49b4-80f2-be7b04c0e2d4', 'chunk_softskills', 'skills', 'Soft skills evidence', 'Customer service and conflict resolution (hospitality manager); leadership under pressure (steel fixing crew Leading hand); incident ownership and communication (Kafka HA recovery).', 'skills', ARRAY['Leadership', 'Communication', 'Customer Service', 'Incident Response'], 'medium', '', 0.7);