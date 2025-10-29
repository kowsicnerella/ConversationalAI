-- Phase 3 Seeding - Direct SQL
-- Run these SQL commands to seed Phase 3 data

-- Seed CEFR Levels
INSERT INTO phase3_curriculum_levels (cefr_level, level_name, vocabulary_range_min, vocabulary_range_max, level_order, estimated_hours, created_at, updated_at)
VALUES
('A1', 'Beginner', 0, 500, 1, 80, NOW(), NOW()),
('A2', 'Elementary', 500, 1000, 2, 150, NOW(), NOW()),
('B1', 'Intermediate', 1000, 2000, 3, 200, NOW(), NOW()),
('B2', 'Upper-Intermediate', 2000, 4000, 4, 250, NOW(), NOW()),
('C1', 'Advanced', 4000, 8000, 5, 300, NOW(), NOW()),
('C2', 'Proficient', 8000, 16000, 6, 400, NOW(), NOW())
ON CONFLICT (cefr_level) DO NOTHING;

-- Seed Skill Domains  
INSERT INTO phase3_skill_domains (domain_name, icon, color, "order", created_at, updated_at)
VALUES
('Listening', '🎧', '#4A90E2', 1, NOW(), NOW()),
('Speaking', '🗣️', '#F5A623', 2, NOW(), NOW()),
('Reading', '📖', '#7ED321', 3, NOW(), NOW()),
('Writing', '✍️', '#BD10E0', 4, NOW(), NOW()),
('Vocabulary', '📚', '#50E3C2', 5, NOW(), NOW()),
('Grammar', '📝', '#FF6B6B', 6, NOW(), NOW())
ON CONFLICT (domain_name) DO NOTHING;

-- Verify
SELECT 'CEFR Levels' as table_name, COUNT(*) as count FROM phase3_curriculum_levels
UNION ALL
SELECT 'Skill Domains', COUNT(*) FROM phase3_skill_domains
UNION ALL
SELECT 'Learning Nodes', COUNT(*) FROM phase3_learning_nodes;
