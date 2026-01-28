from app import create_app
from app.models.curriculum import LearningNode, CurriculumLevel

app = create_app('development')

with app.app_context():
    nodes = LearningNode.query.count()
    levels = CurriculumLevel.query.count()
    
    print(f'Learning Nodes: {nodes}')
    print(f'Curriculum Levels: {levels}')
    
    if nodes == 0:
        print("\n⚠️  NO LEARNING NODES FOUND!")
        print("You need to run: python seed_curriculum.py")
    else:
        print(f"\n✅ Database has {nodes} learning nodes")
        
        # Show first node
        first_node = LearningNode.query.first()
        if first_node:
            print(f"Sample node: {first_node.node_id} - {first_node.concept_name}")
