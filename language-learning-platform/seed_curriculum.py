"""
Seed Curriculum Data Script
Populates CEFR levels (A1-C2) and initial learning nodes for A1-B1 levels
"""
from app import create_app, db
from app.models.curriculum import CurriculumLevel, LearningNode

app = create_app()


def seed_curriculum_levels():
    """Create CEFR curriculum levels"""
    print("🌱 Seeding Curriculum Levels...")
    
    levels = [
        {
            'cefr_level': 'A1',
            'level_name': 'Beginner',
            'description': 'Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type.',
            'vocabulary_range_min': 0,
            'vocabulary_range_max': 1000,
            'estimated_hours': 80,
            'grammar_concepts': [
                'Present simple tense',
                'Basic pronouns (I, you, he, she, it, we, they)',
                'Articles (a/an/the)',
                'Plural nouns',
                'Basic prepositions (in, on, at)',
                'Question words (who, what, where, when, why, how)',
                'There is/There are',
                'This/That/These/Those',
                'Possessive adjectives',
                'Simple negations'
            ],
            'functional_skills': [
                'Introduce yourself and others',
                'Ask and answer simple questions about personal details',
                'Understand basic instructions',
                'Tell time and dates',
                'Order food and drinks',
                'Ask for directions in simple terms',
                'Talk about daily routines',
                'Describe people and places using simple words'
            ]
        },
        {
            'cefr_level': 'A2',
            'level_name': 'Elementary',
            'description': 'Can communicate in simple and routine tasks requiring a simple and direct exchange of information on familiar and routine matters.',
            'vocabulary_range_min': 1000,
            'vocabulary_range_max': 2000,
            'estimated_hours': 120,
            'grammar_concepts': [
                'Past simple tense',
                'Future tense (going to, will)',
                'Modal verbs (can, could, should, must)',
                'Comparative and superlative adjectives',
                'Present continuous',
                'Adverbs of frequency',
                'Countable and uncountable nouns',
                'Some/Any/Much/Many',
                'Past continuous',
                'Present perfect (introduction)'
            ],
            'functional_skills': [
                'Describe past experiences',
                'Make plans for the future',
                'Give opinions and suggestions',
                'Write simple messages and emails',
                'Understand conversations about familiar topics',
                'Handle most travel situations',
                'Make simple phone calls',
                'Talk about likes and dislikes'
            ]
        },
        {
            'cefr_level': 'B1',
            'level_name': 'Intermediate',
            'description': 'Can deal with most situations likely to arise while traveling. Can produce simple connected text on topics of personal interest.',
            'vocabulary_range_min': 2000,
            'vocabulary_range_max': 3500,
            'estimated_hours': 180,
            'grammar_concepts': [
                'Present perfect vs past simple',
                'Past continuous',
                'First and second conditionals',
                'Passive voice (present and past simple)',
                'Reported speech',
                'Relative clauses (who, which, that)',
                'Used to / Would',
                'Future perfect',
                'Phrasal verbs',
                'Modal verbs for deduction'
            ],
            'functional_skills': [
                'Understand main points of clear standard speech',
                'Produce simple connected text on familiar topics',
                'Describe experiences and events in detail',
                'Explain opinions and plans with reasons',
                'Write personal letters and emails',
                'Handle work situations',
                'Understand TV programs and movies with subtitles',
                'Give presentations on familiar topics'
            ]
        }
    ]
    
    for level_data in levels:
        # Check if level already exists
        existing = CurriculumLevel.query.filter_by(cefr_level=level_data['cefr_level']).first()
        if existing:
            print(f"  ⚠️  Level {level_data['cefr_level']} already exists, skipping...")
            continue
            
        level = CurriculumLevel(**level_data)
        db.session.add(level)
        print(f"  ✅ Created level: {level.cefr_level} - {level.level_name}")
    
    db.session.commit()
    print("✅ Curriculum levels seeded successfully!\n")


def seed_learning_nodes():
    """Create initial learning nodes for A1 and A2 levels"""
    print("🌱 Seeding Learning Nodes...")
    
    # Get curriculum levels
    a1_level = CurriculumLevel.query.filter_by(cefr_level='A1').first()
    a2_level = CurriculumLevel.query.filter_by(cefr_level='A2').first()
    b1_level = CurriculumLevel.query.filter_by(cefr_level='B1').first()
    
    if not a1_level or not a2_level or not b1_level:
        print("  ❌ Error: Curriculum levels not found. Run seed_curriculum_levels() first.")
        return
    
    nodes = [
        # ========== A1 LEVEL NODES ==========
        {
            'node_id': 'A1_VOCAB_GREETINGS',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Basic Greetings and Introductions',
            'learning_objectives': [
                'Use common greeting phrases (Hello, Hi, Good morning, etc.)',
                'Introduce yourself with name and basic information',
                'Ask someone\'s name politely',
                'Say goodbye in different contexts',
                'Use appropriate greetings for different times of day'
            ],
            'activity_templates': ['flashcard', 'dialogue_completion', 'role_play', 'quiz'],
            'example_content': {
                'vocabulary': ['hello', 'hi', 'goodbye', 'good morning', 'good evening', 'nice to meet you', 'my name is'],
                'phrases': ['How are you?', 'I am fine', 'See you later', 'Have a good day']
            },
            'difficulty_range_min': 0.0,
            'difficulty_range_max': 0.3,
            'estimated_time_minutes': 15,
            'prerequisites': [],
            'is_core': True,
            'tags': ['vocabulary', 'conversation', 'basics', 'daily_life']
        },
        {
            'node_id': 'A1_VOCAB_NUMBERS',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Numbers 1-100',
            'learning_objectives': [
                'Count from 1 to 100 in English',
                'Use numbers in daily contexts (time, prices, phone numbers)',
                'Understand and say time',
                'Express prices and amounts'
            ],
            'activity_templates': ['flashcard', 'quiz', 'listening', 'speaking'],
            'example_content': {
                'numbers': ['one', 'two', 'three', 'ten', 'twenty', 'fifty', 'hundred'],
                'contexts': ['price', 'time', 'age', 'phone_number']
            },
            'difficulty_range_min': 0.0,
            'difficulty_range_max': 0.3,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_VOCAB_GREETINGS'],
            'is_core': True,
            'tags': ['vocabulary', 'numbers', 'practical', 'daily_life']
        },
        {
            'node_id': 'A1_GRAMMAR_PRESENT_SIMPLE',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Present Simple Tense',
            'learning_objectives': [
                'Form present simple sentences correctly',
                'Use correct subject-verb agreement',
                'Make negative sentences with don\'t/doesn\'t',
                'Ask yes/no questions',
                'Use present simple for habits and routines'
            ],
            'activity_templates': ['sentence_construction', 'error_correction', 'quiz', 'writing'],
            'example_content': {
                'examples': ['I work', 'She works', 'I don\'t like', 'Do you speak English?'],
                'verbs': ['work', 'live', 'like', 'speak', 'eat', 'drink', 'play']
            },
            'difficulty_range_min': 0.2,
            'difficulty_range_max': 0.5,
            'estimated_time_minutes': 25,
            'prerequisites': ['A1_VOCAB_GREETINGS'],
            'is_core': True,
            'tags': ['grammar', 'verb_tenses', 'fundamental']
        },
        {
            'node_id': 'A1_VOCAB_FAMILY',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Family Members',
            'learning_objectives': [
                'Name immediate family members',
                'Describe family relationships',
                'Talk about family in simple terms',
                'Use possessive forms (my, your, his, her)'
            ],
            'activity_templates': ['flashcard', 'reading', 'speaking', 'quiz'],
            'example_content': {
                'vocabulary': ['father', 'mother', 'brother', 'sister', 'son', 'daughter', 'grandfather', 'grandmother'],
                'phrases': ['my family', 'this is my', 'I have a']
            },
            'difficulty_range_min': 0.1,
            'difficulty_range_max': 0.3,
            'estimated_time_minutes': 15,
            'prerequisites': ['A1_VOCAB_GREETINGS'],
            'is_core': True,
            'tags': ['vocabulary', 'family', 'personal', 'relationships']
        },
        {
            'node_id': 'A1_VOCAB_DAILY_ROUTINE',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Daily Routine Activities',
            'learning_objectives': [
                'Name common daily activities',
                'Describe your daily routine',
                'Use time expressions (in the morning, at night)',
                'Use frequency adverbs (always, sometimes, never)'
            ],
            'activity_templates': ['flashcard', 'writing', 'speaking', 'reading'],
            'example_content': {
                'activities': ['wake up', 'get up', 'brush teeth', 'have breakfast', 'go to work', 'come home', 'go to bed'],
                'time_expressions': ['in the morning', 'in the afternoon', 'in the evening', 'at night']
            },
            'difficulty_range_min': 0.2,
            'difficulty_range_max': 0.4,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_VOCAB_NUMBERS', 'A1_GRAMMAR_PRESENT_SIMPLE'],
            'is_core': True,
            'tags': ['vocabulary', 'daily_life', 'routine', 'time']
        },
        {
            'node_id': 'A1_VOCAB_FOOD_DRINKS',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Food and Drinks',
            'learning_objectives': [
                'Name common food items',
                'Name common drinks',
                'Order food in a restaurant',
                'Express likes and dislikes about food',
                'Use "I would like" for ordering'
            ],
            'activity_templates': ['flashcard', 'role_play', 'quiz', 'listening'],
            'example_content': {
                'food': ['bread', 'rice', 'chicken', 'fish', 'vegetables', 'fruit', 'egg'],
                'drinks': ['water', 'tea', 'coffee', 'juice', 'milk'],
                'phrases': ['I would like', 'Can I have', 'I like', 'I don\'t like']
            },
            'difficulty_range_min': 0.1,
            'difficulty_range_max': 0.3,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_VOCAB_GREETINGS'],
            'is_core': True,
            'tags': ['vocabulary', 'food', 'restaurant', 'practical']
        },
        {
            'node_id': 'A1_VOCAB_COLORS_SHAPES',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Colors and Basic Shapes',
            'learning_objectives': [
                'Name common colors',
                'Name basic shapes',
                'Describe objects using colors and shapes',
                'Use adjectives for description'
            ],
            'activity_templates': ['flashcard', 'quiz', 'speaking', 'game'],
            'example_content': {
                'colors': ['red', 'blue', 'green', 'yellow', 'black', 'white', 'orange', 'purple'],
                'shapes': ['circle', 'square', 'triangle', 'rectangle'],
                'phrases': ['it is', 'the color is', 'the shape is']
            },
            'difficulty_range_min': 0.0,
            'difficulty_range_max': 0.2,
            'estimated_time_minutes': 15,
            'prerequisites': ['A1_VOCAB_GREETINGS'],
            'is_core': False,
            'tags': ['vocabulary', 'colors', 'shapes', 'description']
        },
        {
            'node_id': 'A1_GRAMMAR_ARTICLES',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Articles (a/an/the)',
            'learning_objectives': [
                'Understand when to use "a" vs "an"',
                'Use "the" for specific things',
                'Know when to omit articles',
                'Apply articles correctly in sentences'
            ],
            'activity_templates': ['sentence_construction', 'error_correction', 'quiz', 'fill_in_blank'],
            'example_content': {
                'rules': ['a before consonants', 'an before vowels', 'the for specific items'],
                'examples': ['a book', 'an apple', 'the sun', 'the teacher']
            },
            'difficulty_range_min': 0.2,
            'difficulty_range_max': 0.5,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_GRAMMAR_PRESENT_SIMPLE'],
            'is_core': True,
            'tags': ['grammar', 'articles', 'fundamental']
        },
        {
            'node_id': 'A1_VOCAB_PLACES',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Places in Town',
            'learning_objectives': [
                'Name common places in town',
                'Ask for and give simple directions',
                'Use prepositions of place (next to, opposite, near)',
                'Describe locations'
            ],
            'activity_templates': ['flashcard', 'role_play', 'quiz', 'reading'],
            'example_content': {
                'places': ['bank', 'hospital', 'school', 'restaurant', 'supermarket', 'post office', 'park'],
                'prepositions': ['next to', 'opposite', 'near', 'between', 'in front of', 'behind'],
                'phrases': ['Where is the', 'How do I get to', 'Go straight', 'Turn left/right']
            },
            'difficulty_range_min': 0.2,
            'difficulty_range_max': 0.4,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_VOCAB_GREETINGS', 'A1_GRAMMAR_PRESENT_SIMPLE'],
            'is_core': True,
            'tags': ['vocabulary', 'places', 'directions', 'practical']
        },
        {
            'node_id': 'A1_VOCAB_WEATHER',
            'curriculum_level_id': a1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Weather and Seasons',
            'learning_objectives': [
                'Describe weather conditions',
                'Name the four seasons',
                'Talk about climate',
                'Use weather-related vocabulary'
            ],
            'activity_templates': ['flashcard', 'quiz', 'speaking', 'listening'],
            'example_content': {
                'weather': ['sunny', 'rainy', 'cloudy', 'windy', 'hot', 'cold', 'warm'],
                'seasons': ['spring', 'summer', 'autumn', 'winter'],
                'phrases': ['It is', 'The weather is', 'It\'s raining', 'It\'s sunny']
            },
            'difficulty_range_min': 0.1,
            'difficulty_range_max': 0.3,
            'estimated_time_minutes': 15,
            'prerequisites': ['A1_GRAMMAR_PRESENT_SIMPLE'],
            'is_core': False,
            'tags': ['vocabulary', 'weather', 'seasons', 'conversation']
        },
        
        # ========== A2 LEVEL NODES ==========
        {
            'node_id': 'A2_GRAMMAR_PAST_SIMPLE',
            'curriculum_level_id': a2_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Past Simple Tense',
            'learning_objectives': [
                'Form regular past simple verbs',
                'Use common irregular past simple verbs',
                'Make negative sentences in past simple',
                'Ask questions in past simple',
                'Describe past events and experiences'
            ],
            'activity_templates': ['sentence_construction', 'error_correction', 'quiz', 'writing', 'story_telling'],
            'example_content': {
                'regular_verbs': ['worked', 'played', 'visited', 'watched'],
                'irregular_verbs': ['went', 'saw', 'ate', 'had', 'did', 'came', 'took'],
                'phrases': ['yesterday', 'last week', 'ago', 'in 2020']
            },
            'difficulty_range_min': 0.3,
            'difficulty_range_max': 0.6,
            'estimated_time_minutes': 25,
            'prerequisites': ['A1_GRAMMAR_PRESENT_SIMPLE'],
            'is_core': True,
            'tags': ['grammar', 'verb_tenses', 'past', 'storytelling']
        },
        {
            'node_id': 'A2_VOCAB_TRAVEL',
            'curriculum_level_id': a2_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Travel and Tourism',
            'learning_objectives': [
                'Use travel-related vocabulary',
                'Book hotel rooms and transportation',
                'Understand travel announcements',
                'Handle airport and station situations',
                'Ask for tourist information'
            ],
            'activity_templates': ['flashcard', 'role_play', 'listening', 'reading', 'quiz'],
            'example_content': {
                'vocabulary': ['airport', 'hotel', 'ticket', 'passport', 'luggage', 'flight', 'train', 'tourist'],
                'phrases': ['I would like to book', 'What time does it leave', 'Where is the gate', 'Check in/out']
            },
            'difficulty_range_min': 0.3,
            'difficulty_range_max': 0.5,
            'estimated_time_minutes': 25,
            'prerequisites': ['A1_VOCAB_PLACES', 'A2_GRAMMAR_PAST_SIMPLE'],
            'is_core': True,
            'tags': ['vocabulary', 'travel', 'practical', 'tourism']
        },
        {
            'node_id': 'A2_GRAMMAR_FUTURE',
            'curriculum_level_id': a2_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Future Tenses (will/going to)',
            'learning_objectives': [
                'Use "will" for spontaneous decisions',
                'Use "going to" for plans',
                'Make predictions about the future',
                'Understand differences between will and going to',
                'Form negative and question forms'
            ],
            'activity_templates': ['sentence_construction', 'quiz', 'writing', 'speaking'],
            'example_content': {
                'will_uses': ['spontaneous decisions', 'offers', 'promises', 'predictions'],
                'going_to_uses': ['plans', 'intentions', 'predictions with evidence'],
                'examples': ['I will help you', 'I am going to visit', 'It will rain', 'She is going to study']
            },
            'difficulty_range_min': 0.3,
            'difficulty_range_max': 0.6,
            'estimated_time_minutes': 25,
            'prerequisites': ['A2_GRAMMAR_PAST_SIMPLE'],
            'is_core': True,
            'tags': ['grammar', 'verb_tenses', 'future', 'planning']
        },
        {
            'node_id': 'A2_VOCAB_SHOPPING',
            'curriculum_level_id': a2_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Shopping and Money',
            'learning_objectives': [
                'Use shopping vocabulary',
                'Ask about prices and sizes',
                'Return or exchange items',
                'Understand sales and discounts',
                'Handle payment situations'
            ],
            'activity_templates': ['flashcard', 'role_play', 'listening', 'quiz'],
            'example_content': {
                'vocabulary': ['shop', 'store', 'price', 'expensive', 'cheap', 'discount', 'sale', 'size', 'color'],
                'phrases': ['How much is it', 'Do you have this in', 'Can I try it on', 'I would like to return']
            },
            'difficulty_range_min': 0.3,
            'difficulty_range_max': 0.5,
            'estimated_time_minutes': 20,
            'prerequisites': ['A1_VOCAB_NUMBERS', 'A1_VOCAB_COLORS_SHAPES'],
            'is_core': True,
            'tags': ['vocabulary', 'shopping', 'practical', 'money']
        },
        {
            'node_id': 'A2_GRAMMAR_COMPARATIVES',
            'curriculum_level_id': a2_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Comparative and Superlative Adjectives',
            'learning_objectives': [
                'Form comparative adjectives (bigger, more expensive)',
                'Form superlative adjectives (biggest, most expensive)',
                'Use than in comparisons',
                'Use the with superlatives',
                'Understand irregular forms (good-better-best)'
            ],
            'activity_templates': ['sentence_construction', 'quiz', 'error_correction', 'speaking'],
            'example_content': {
                'regular': ['big-bigger-biggest', 'small-smaller-smallest'],
                'with_more': ['expensive-more expensive-most expensive'],
                'irregular': ['good-better-best', 'bad-worse-worst'],
                'examples': ['This is bigger than that', 'It is the most beautiful place']
            },
            'difficulty_range_min': 0.4,
            'difficulty_range_max': 0.6,
            'estimated_time_minutes': 25,
            'prerequisites': ['A1_GRAMMAR_ARTICLES'],
            'is_core': True,
            'tags': ['grammar', 'adjectives', 'comparison']
        },
        
        # ========== B1 LEVEL NODES ==========
        {
            'node_id': 'B1_GRAMMAR_PRESENT_PERFECT',
            'curriculum_level_id': b1_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Present Perfect Tense',
            'learning_objectives': [
                'Form present perfect with have/has + past participle',
                'Use present perfect for life experiences',
                'Use present perfect for unfinished time',
                'Distinguish present perfect from past simple',
                'Use ever, never, already, yet, just'
            ],
            'activity_templates': ['sentence_construction', 'quiz', 'error_correction', 'speaking', 'writing'],
            'example_content': {
                'structure': 'have/has + past participle',
                'uses': ['life experiences', 'recent actions', 'unfinished time periods'],
                'time_words': ['ever', 'never', 'already', 'yet', 'just', 'recently', 'lately'],
                'examples': ['I have visited India', 'She has just arrived', 'Have you ever been to']
            },
            'difficulty_range_min': 0.5,
            'difficulty_range_max': 0.8,
            'estimated_time_minutes': 30,
            'prerequisites': ['A2_GRAMMAR_PAST_SIMPLE'],
            'is_core': True,
            'tags': ['grammar', 'verb_tenses', 'present_perfect', 'experiences']
        },
        {
            'node_id': 'B1_GRAMMAR_CONDITIONALS',
            'curriculum_level_id': b1_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'First and Second Conditionals',
            'learning_objectives': [
                'Use first conditional for real future possibilities',
                'Use second conditional for unreal/unlikely situations',
                'Understand the structure of both conditionals',
                'Use appropriate time clauses (if, when, unless)',
                'Apply conditionals in real situations'
            ],
            'activity_templates': ['sentence_construction', 'quiz', 'speaking', 'writing'],
            'example_content': {
                'first_conditional': 'If + present simple, will + infinitive',
                'second_conditional': 'If + past simple, would + infinitive',
                'examples_first': ['If it rains, I will stay home', 'If you study, you will pass'],
                'examples_second': ['If I had money, I would travel', 'If I were you, I would go']
            },
            'difficulty_range_min': 0.6,
            'difficulty_range_max': 0.8,
            'estimated_time_minutes': 30,
            'prerequisites': ['A2_GRAMMAR_FUTURE'],
            'is_core': True,
            'tags': ['grammar', 'conditionals', 'hypothetical', 'reasoning']
        },
        {
            'node_id': 'B1_VOCAB_WORK',
            'curriculum_level_id': b1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Work and Career',
            'learning_objectives': [
                'Discuss jobs and professions',
                'Talk about work responsibilities',
                'Describe workplace situations',
                'Use professional language',
                'Handle job interviews'
            ],
            'activity_templates': ['flashcard', 'role_play', 'reading', 'listening', 'quiz'],
            'example_content': {
                'vocabulary': ['job', 'career', 'profession', 'salary', 'interview', 'colleague', 'manager', 'employee'],
                'phrases': ['I work as', 'I am responsible for', 'My duties include', 'I report to']
            },
            'difficulty_range_min': 0.5,
            'difficulty_range_max': 0.7,
            'estimated_time_minutes': 25,
            'prerequisites': ['A2_VOCAB_TRAVEL', 'B1_GRAMMAR_PRESENT_PERFECT'],
            'is_core': True,
            'tags': ['vocabulary', 'work', 'career', 'professional', 'business']
        },
        {
            'node_id': 'B1_GRAMMAR_PASSIVE_VOICE',
            'curriculum_level_id': b1_level.id,
            'skill_domain': 'grammar',
            'concept_name': 'Passive Voice (Present and Past)',
            'learning_objectives': [
                'Understand passive voice structure',
                'Form present simple passive',
                'Form past simple passive',
                'Know when to use passive voice',
                'Convert active to passive sentences'
            ],
            'activity_templates': ['sentence_construction', 'transformation', 'quiz', 'error_correction'],
            'example_content': {
                'structure': 'be + past participle',
                'present': 'is/are + past participle',
                'past': 'was/were + past participle',
                'examples': ['The house is built', 'English is spoken', 'The book was written']
            },
            'difficulty_range_min': 0.6,
            'difficulty_range_max': 0.8,
            'estimated_time_minutes': 30,
            'prerequisites': ['B1_GRAMMAR_PRESENT_PERFECT'],
            'is_core': True,
            'tags': ['grammar', 'passive_voice', 'advanced_structure']
        },
        {
            'node_id': 'B1_VOCAB_HEALTH',
            'curriculum_level_id': b1_level.id,
            'skill_domain': 'vocabulary',
            'concept_name': 'Health and Medical',
            'learning_objectives': [
                'Describe symptoms and illnesses',
                'Talk to doctors and medical professionals',
                'Understand medical advice',
                'Discuss healthy lifestyle',
                'Use health-related vocabulary'
            ],
            'activity_templates': ['flashcard', 'role_play', 'listening', 'reading', 'quiz'],
            'example_content': {
                'vocabulary': ['headache', 'fever', 'cough', 'medicine', 'doctor', 'hospital', 'healthy', 'exercise'],
                'phrases': ['I have a', 'I feel', 'I need to see a doctor', 'Take this medicine']
            },
            'difficulty_range_min': 0.5,
            'difficulty_range_max': 0.7,
            'estimated_time_minutes': 25,
            'prerequisites': ['A1_VOCAB_FAMILY', 'B1_GRAMMAR_PRESENT_PERFECT'],
            'is_core': True,
            'tags': ['vocabulary', 'health', 'medical', 'practical', 'wellbeing']
        }
    ]
    
    nodes_created = 0
    for node_data in nodes:
        # Check if node already exists
        existing = LearningNode.query.filter_by(node_id=node_data['node_id']).first()
        if existing:
            print(f"  ⚠️  Node {node_data['node_id']} already exists, skipping...")
            continue
            
        node = LearningNode(**node_data)
        db.session.add(node)
        nodes_created += 1
        print(f"  ✅ Created node: {node.node_id} - {node.concept_name}")
    
    db.session.commit()
    print(f"\n✅ Successfully created {nodes_created} learning nodes!\n")


def main():
    """Main seeding function"""
    with app.app_context():
        print("\n" + "="*60)
        print("🚀 SEEDING CURRICULUM DATA")
        print("="*60 + "\n")
        
        try:
            seed_curriculum_levels()
            seed_learning_nodes()
            
            # Print summary
            print("="*60)
            print("📊 SEEDING SUMMARY")
            print("="*60)
            print(f"Total Curriculum Levels: {CurriculumLevel.query.count()}")
            print(f"Total Learning Nodes: {LearningNode.query.count()}")
            
            # Breakdown by level
            for level in ['A1', 'A2', 'B1']:
                level_obj = CurriculumLevel.query.filter_by(cefr_level=level).first()
                if level_obj:
                    node_count = LearningNode.query.filter_by(curriculum_level_id=level_obj.id).count()
                    print(f"  - {level} Nodes: {node_count}")
            
            print("\n✅ All curriculum data seeded successfully!")
            print("🎓 Ready to start personalized learning!\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()
