"""Check if assessment questions are unique"""
from app.services.initial_assessment_service import InitialAssessmentService

service = InitialAssessmentService()

print("=" * 80)
print("CHECKING SPEAKING ADVANCED QUESTIONS FOR UNIQUENESS")
print("=" * 80)

questions = service._generate_fallback_questions('speaking', 'advanced', 6)

print(f"\nGenerated {len(questions)} questions:\n")
for i, q in enumerate(questions, 1):
    print(f"{i}. ID: {q['question_id']}")
    print(f"   Text: {q['question_text'][:100]}...")
    print()

# Check for duplicates
question_texts = [q['question_text'] for q in questions]
unique_texts = set(question_texts)

print("=" * 80)
if len(unique_texts) == len(question_texts):
    print(f"✅ ALL {len(questions)} QUESTIONS ARE UNIQUE!")
else:
    print(f"❌ WARNING: Only {len(unique_texts)}/{len(questions)} unique questions")
    print("\nDuplicate questions found:")
    for text in question_texts:
        if question_texts.count(text) > 1:
            print(f"  - {text[:80]}... (appears {question_texts.count(text)} times)")
print("=" * 80)

print("\n" + "=" * 80)
print("CHECKING ALL SKILLS FOR COMPREHENSIVE ASSESSMENT")
print("=" * 80)

all_questions = []
for skill in ['vocabulary', 'grammar', 'reading', 'listening', 'writing', 'speaking']:
    for level in ['beginner', 'intermediate', 'advanced']:
        questions = service._generate_fallback_questions(skill, level, 2)  # 2 per level as per comprehensive
        all_questions.extend(questions)

print(f"\nTotal questions for comprehensive assessment: {len(all_questions)}")
print(f"Expected: 36 (6 skills × 3 levels × 2 questions)")

# Check uniqueness
all_texts = [q['question_text'] for q in all_questions]
unique_all = set(all_texts)

print(f"Unique question texts: {len(unique_all)}")

if len(unique_all) == len(all_texts):
    print("✅ ALL QUESTIONS ARE UNIQUE!")
else:
    print(f"❌ WARNING: {len(all_texts) - len(unique_all)} duplicate questions found")
    print("\nDuplicates:")
    seen = set()
    for text in all_texts:
        if all_texts.count(text) > 1 and text not in seen:
            print(f"  - {text[:80]}... (appears {all_texts.count(text)} times)")
            seen.add(text)
