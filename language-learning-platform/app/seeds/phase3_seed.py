"""
Phase 3 Data Seeding Script
Seeds CEFR levels, skill domains, and sample learning nodes
"""

from app import create_app, db
from app.models.learning_node import CurriculumLevel, SkillDomain, LearningNode
from datetime import datetime


def seed_curriculum_levels():
    """Seed 6 CEFR levels (A1-C2)"""
    print("Seeding CEFR curriculum levels...")
    
    levels_data = [
        {
            'cefr_level': 'A1',
            'level_name': 'Beginner',
            'description': 'Can understand and use familiar everyday expressions and very basic phrases.',
            'vocabulary_range_min': 0,
            'vocabulary_range_max': 500,
            'grammar_concepts': [
                'Present Simple',
                'Basic Pronouns (I, you, he, she)',
                'Basic Question Words (what, where, who)',
                'Articles (a, an, the)',
                'Plural nouns (-s)',
                'Basic Prepositions (in, on, at)',
            ],
            'functional_skills': [
                'Introduce yourself',
                'Ask for and give basic information',
                'Understand simple signs and notices',
                'Fill in simple forms',
                'Order food and drinks',
            ],
            'estimated_hours': 80,
            'level_order': 1,
        },
        {
            'cefr_level': 'A2',
            'level_name': 'Elementary',
            'description': 'Can understand sentences and frequently used expressions related to everyday topics.',
            'vocabulary_range_min': 500,
            'vocabulary_range_max': 1000,
            'grammar_concepts': [
                'Past Simple',
                'Future (going to)',
                'Present Continuous',
                'Comparatives and Superlatives',
                'Modal Verbs (can, could, should)',
                'Countable/Uncountable Nouns',
            ],
            'functional_skills': [
                'Describe family and living conditions',
                'Make simple purchases',
                'Understand straightforward instructions',
                'Write short messages',
                'Talk about past experiences',
            ],
            'estimated_hours': 150,
            'level_order': 2,
        },
        {
            'cefr_level': 'B1',
            'level_name': 'Intermediate',
            'description': 'Can deal with most situations likely to arise while traveling in an area where the language is spoken.',
            'vocabulary_range_min': 1000,
            'vocabulary_range_max': 2000,
            'grammar_concepts': [
                'Present Perfect',
                'Past Continuous',
                'Future Will',
                'Conditional Sentences (Type 1)',
                'Passive Voice (simple)',
                'Relative Clauses',
            ],
            'functional_skills': [
                'Express opinions and preferences',
                'Handle travel situations',
                'Understand main points of clear texts',
                'Write simple connected text',
                'Describe experiences and events',
            ],
            'estimated_hours': 200,
            'level_order': 3,
        },
        {
            'cefr_level': 'B2',
            'level_name': 'Upper-Intermediate',
            'description': 'Can interact with a degree of fluency and spontaneity with native speakers.',
            'vocabulary_range_min': 2000,
            'vocabulary_range_max': 4000,
            'grammar_concepts': [
                'Mixed Conditionals',
                'Reported Speech',
                'Perfect Continuous Tenses',
                'Advanced Passive Forms',
                'Gerunds and Infinitives',
                'Phrasal Verbs',
            ],
            'functional_skills': [
                'Express viewpoints on complex topics',
                'Understand detailed texts',
                'Write clear, detailed text',
                'Participate in discussions',
                'Explain advantages and disadvantages',
            ],
            'estimated_hours': 250,
            'level_order': 4,
        },
        {
            'cefr_level': 'C1',
            'level_name': 'Advanced',
            'description': 'Can express ideas fluently and spontaneously without much obvious searching for expressions.',
            'vocabulary_range_min': 4000,
            'vocabulary_range_max': 8000,
            'grammar_concepts': [
                'Advanced Modal Verbs',
                'Inversion',
                'Cleft Sentences',
                'Emphatic Structures',
                'Subjunctive Mood',
                'Advanced Linking Words',
            ],
            'functional_skills': [
                'Produce clear, well-structured text',
                'Express yourself fluently',
                'Use language flexibly',
                'Understand complex texts',
                'Engage in detailed discussions',
            ],
            'estimated_hours': 300,
            'level_order': 5,
        },
        {
            'cefr_level': 'C2',
            'level_name': 'Proficient',
            'description': 'Can understand with ease virtually everything heard or read.',
            'vocabulary_range_min': 8000,
            'vocabulary_range_max': 16000,
            'grammar_concepts': [
                'Advanced Sentence Structures',
                'Nuanced Modal Usage',
                'Complex Passive Forms',
                'Stylistic Devices',
                'Register Variations',
                'Discourse Markers',
            ],
            'functional_skills': [
                'Express yourself spontaneously and precisely',
                'Summarize complex information',
                'Reconstruct arguments coherently',
                'Understand implicit meanings',
                'Differentiate finer shades of meaning',
            ],
            'estimated_hours': 400,
            'level_order': 6,
        },
    ]
    
    created_count = 0
    for level_data in levels_data:
        # Check if level already exists
        existing = CurriculumLevel.query.filter_by(cefr_level=level_data['cefr_level']).first()
        if not existing:
            level = CurriculumLevel(**level_data)
            db.session.add(level)
            created_count += 1
            print(f"  ✓ Created: {level_data['cefr_level']} - {level_data['level_name']}")
        else:
            print(f"  ⊘ Skipped: {level_data['cefr_level']} (already exists)")
    
    db.session.commit()
    print(f"✅ Curriculum levels seeded: {created_count} created, {len(levels_data) - created_count} existed\n")


def seed_skill_domains():
    """Seed 6 core skill domains"""
    print("Seeding skill domains...")
    
    domains_data = [
        {
            'domain_name': 'Listening',
            'description': 'Ability to understand spoken language in various contexts',
            'sub_skills': [
                'Phoneme recognition',
                'Word recognition',
                'Sentence comprehension',
                'Contextual understanding',
                'Accent adaptation',
                'Inference from context',
            ],
            'assessment_criteria': {
                'accuracy': 'Percentage of correctly understood content',
                'speed': 'Words per minute comprehension rate',
                'complexity': 'Level of vocabulary and grammar understood',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '🎧',
            'color': '#4A90E2',
            'order': 1,
        },
        {
            'domain_name': 'Speaking',
            'description': 'Ability to produce spoken language clearly and effectively',
            'sub_skills': [
                'Pronunciation accuracy',
                'Fluency (words per minute)',
                'Grammar in speech',
                'Vocabulary usage',
                'Intonation and stress',
                'Confidence and naturalness',
            ],
            'assessment_criteria': {
                'pronunciation': 'Clarity and accuracy of sounds',
                'fluency': 'Smoothness and speed of speech',
                'grammar': 'Correctness of sentence structures',
                'vocabulary': 'Appropriateness of word choice',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '🗣️',
            'color': '#F5A623',
            'order': 2,
        },
        {
            'domain_name': 'Reading',
            'description': 'Ability to understand written text across various genres',
            'sub_skills': [
                'Reading speed (WPM)',
                'Comprehension',
                'Vocabulary recognition',
                'Inference ability',
                'Retention',
                'Skimming and scanning',
            ],
            'assessment_criteria': {
                'speed': 'Words per minute reading rate',
                'comprehension': 'Understanding of main ideas and details',
                'vocabulary': 'Percentage of words understood',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '📖',
            'color': '#7ED321',
            'order': 3,
        },
        {
            'domain_name': 'Writing',
            'description': 'Ability to produce written text clearly and coherently',
            'sub_skills': [
                'Spelling accuracy',
                'Grammar correctness',
                'Sentence structure',
                'Paragraph coherence',
                'Vocabulary diversity',
                'Style and tone',
            ],
            'assessment_criteria': {
                'accuracy': 'Spelling and grammar correctness',
                'coherence': 'Logical flow and organization',
                'vocabulary': 'Variety and appropriateness of words',
                'complexity': 'Sophistication of sentence structures',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '✍️',
            'color': '#BD10E0',
            'order': 4,
        },
        {
            'domain_name': 'Vocabulary',
            'description': 'Knowledge and appropriate use of words and expressions',
            'sub_skills': [
                'Active vocabulary (production)',
                'Passive vocabulary (recognition)',
                'Context-appropriate usage',
                'Collocations',
                'Idiomatic expressions',
                'Register awareness',
            ],
            'assessment_criteria': {
                'breadth': 'Total number of words known',
                'depth': 'Understanding of word meanings and usage',
                'production': 'Ability to use words correctly',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '📚',
            'color': '#50E3C2',
            'order': 5,
        },
        {
            'domain_name': 'Grammar',
            'description': 'Understanding and application of language rules and structures',
            'sub_skills': [
                'Tense usage',
                'Sentence structure',
                'Articles and prepositions',
                'Agreement (subject-verb)',
                'Complex sentences',
                'Advanced structures',
            ],
            'assessment_criteria': {
                'accuracy': 'Correctness of grammar usage',
                'complexity': 'Range of structures used',
                'appropriateness': 'Context-appropriate grammar',
            },
            'mastery_thresholds': {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'mastered': 0.95,
            },
            'icon': '📝',
            'color': '#FF6B6B',
            'order': 6,
        },
    ]
    
    created_count = 0
    for domain_data in domains_data:
        # Check if domain already exists
        existing = SkillDomain.query.filter_by(domain_name=domain_data['domain_name']).first()
        if not existing:
            domain = SkillDomain(**domain_data)
            db.session.add(domain)
            created_count += 1
            print(f"  ✓ Created: {domain_data['domain_name']} - {domain_data['icon']}")
        else:
            print(f"  ⊘ Skipped: {domain_data['domain_name']} (already exists)")
    
    db.session.commit()
    print(f"✅ Skill domains seeded: {created_count} created, {len(domains_data) - created_count} existed\n")


def seed_sample_learning_nodes():
    """Seed sample learning nodes for testing"""
    print("Seeding sample learning nodes...")
    
    # Get A1 level and Listening skill
    a1_level = CurriculumLevel.query.filter_by(cefr_level='A1').first()
    listening_skill = SkillDomain.query.filter_by(domain_name='Listening').first()
    speaking_skill = SkillDomain.query.filter_by(domain_name='Speaking').first()
    grammar_skill = SkillDomain.query.filter_by(domain_name='Grammar').first()
    
    if not (a1_level and listening_skill and speaking_skill and grammar_skill):
        print("❌ Cannot create sample nodes - missing curriculum level or skill domains")
        return
    
    sample_nodes = [
        {
            'node_id': 'A1_GREETING_001',
            'curriculum_level_id': a1_level.id,
            'skill_domain_id': speaking_skill.id,
            'concept_name': 'Basic Greetings',
            'description': 'Learn to greet people in different contexts (formal/informal)',
            'learning_objectives': [
                'Use "Hello", "Hi", "Good morning/afternoon/evening"',
                'Respond appropriately to greetings',
                'Understand formal vs informal greetings',
            ],
            'prerequisites': [],
            'difficulty_min': 0.10,
            'difficulty_max': 0.30,
            'recommended_difficulty': 0.20,
            'estimated_time_minutes': 10,
            'mastery_threshold': 0.80,
            'activity_templates': ['dialogue', 'fill_in_blank', 'multiple_choice'],
        },
        {
            'node_id': 'A1_GREETING_002',
            'curriculum_level_id': a1_level.id,
            'skill_domain_id': speaking_skill.id,
            'concept_name': 'Self Introduction',
            'description': 'Introduce yourself and ask others their names',
            'learning_objectives': [
                'Say "My name is..." and "I am..."',
                'Ask "What is your name?"',
                'Respond when someone introduces themselves',
            ],
            'prerequisites': ['A1_GREETING_001'],
            'difficulty_min': 0.15,
            'difficulty_max': 0.35,
            'recommended_difficulty': 0.25,
            'estimated_time_minutes': 12,
            'mastery_threshold': 0.80,
            'activity_templates': ['dialogue', 'fill_in_blank', 'speaking_practice'],
        },
        {
            'node_id': 'A1_LISTENING_001',
            'curriculum_level_id': a1_level.id,
            'skill_domain_id': listening_skill.id,
            'concept_name': 'Numbers 1-10',
            'description': 'Understand and recognize numbers from 1 to 10 when spoken',
            'learning_objectives': [
                'Recognize numbers 1-10 when heard',
                'Distinguish between similar sounding numbers',
                'Understand numbers in context (age, phone)',
            ],
            'prerequisites': [],
            'difficulty_min': 0.10,
            'difficulty_max': 0.30,
            'recommended_difficulty': 0.20,
            'estimated_time_minutes': 8,
            'mastery_threshold': 0.85,
            'activity_templates': ['audio_comprehension', 'multiple_choice', 'matching'],
        },
        {
            'node_id': 'A1_GRAMMAR_001',
            'curriculum_level_id': a1_level.id,
            'skill_domain_id': grammar_skill.id,
            'concept_name': 'Personal Pronouns',
            'description': 'Learn and use personal pronouns: I, you, he, she, it, we, they',
            'learning_objectives': [
                'Identify all personal pronouns',
                'Use correct pronoun for subject',
                'Distinguish he/she/it appropriately',
            ],
            'prerequisites': [],
            'difficulty_min': 0.15,
            'difficulty_max': 0.40,
            'recommended_difficulty': 0.25,
            'estimated_time_minutes': 15,
            'mastery_threshold': 0.80,
            'activity_templates': ['fill_in_blank', 'multiple_choice', 'sentence_building'],
        },
    ]
    
    created_count = 0
    for node_data in sample_nodes:
        # Check if node already exists
        existing = LearningNode.query.filter_by(node_id=node_data['node_id']).first()
        if not existing:
            node = LearningNode(**node_data)
            db.session.add(node)
            created_count += 1
            print(f"  ✓ Created: {node_data['node_id']} - {node_data['concept_name']}")
        else:
            print(f"  ⊘ Skipped: {node_data['node_id']} (already exists)")
    
    db.session.commit()
    print(f"✅ Sample learning nodes seeded: {created_count} created, {len(sample_nodes) - created_count} existed\n")


def run_all_seeds():
    """Run all seeding functions"""
    print("\n" + "="*60)
    print("  PHASE 3 DATA SEEDING")
    print("="*60 + "\n")
    
    seed_curriculum_levels()
    seed_skill_domains()
    seed_sample_learning_nodes()
    
    print("="*60)
    print("  ✅ PHASE 3 SEEDING COMPLETE!")
    print("="*60 + "\n")
    
    # Print summary
    total_levels = CurriculumLevel.query.count()
    total_domains = SkillDomain.query.count()
    total_nodes = LearningNode.query.count()
    
    print(f"Database Summary:")
    print(f"  - CEFR Levels: {total_levels}")
    print(f"  - Skill Domains: {total_domains}")
    print(f"  - Learning Nodes: {total_nodes}")
    print()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        run_all_seeds()
