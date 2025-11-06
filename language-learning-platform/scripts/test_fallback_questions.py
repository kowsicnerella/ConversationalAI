from app.services.initial_assessment_service import InitialAssessmentService

service = InitialAssessmentService()

print('Checking uniqueness for each skill/level (6 questions requested)')
problems = []
for skill in ['vocabulary','grammar','reading','listening','writing','speaking']:
    for level in ['beginner','intermediate','advanced']:
        qs = service._generate_fallback_questions(skill, level, 6)
        texts = [q['question_text'] for q in qs]
        unique = len(set(texts))
        print(f'{skill}/{level}: {unique}/6 unique')
        if unique < 6:
            problems.append((skill,level,unique,texts))

if not problems:
    print('\n✅ All requested fallback sets returned 6 unique question_texts.')
else:
    print('\n⚠️ Problems found:')
    for p in problems:
        print(p)
