# Phase 3 Table Name Conflict - FIXED ✅

**Issue**: Flask app crashed with SQLAlchemy error:
```
sqlalchemy.exc.InvalidRequestError: Table 'curriculum_levels' is already defined for this MetaData instance.
```

**Root Cause**: 
- Phase 1 had models in `curriculum.py` with tables: `curriculum_levels`, `learning_nodes`
- Phase 3 created new models in `learning_node.py` with same table names
- Even though Python imports used aliases (`Phase3CurriculumLevel`), SQLAlchemy still saw duplicate table names in the same MetaData instance

**Solution**: Renamed all Phase 3 table names with `phase3_` prefix

---

## Table Name Changes

| Model | Old Table Name | New Table Name |
|-------|---------------|----------------|
| CurriculumLevel | `curriculum_levels` | `phase3_curriculum_levels` |
| SkillDomain | `skill_domains` | `phase3_skill_domains` |
| LearningNode | `learning_nodes` | `phase3_learning_nodes` |
| UserLearningNodeProgress | `user_learning_node_progress` | `phase3_user_learning_node_progress` |
| UserSkillProfile | `user_skill_profiles` | `phase3_user_skill_profiles` |

---

## Foreign Key Updates

Also updated foreign key references:
```python
# Before
curriculum_level_id = db.ForeignKey('curriculum_levels.id')
skill_domain_id = db.ForeignKey('skill_domains.id')
learning_node_id = db.ForeignKey('learning_nodes.id')

# After
curriculum_level_id = db.ForeignKey('phase3_curriculum_levels.id')
skill_domain_id = db.ForeignKey('phase3_skill_domains.id')
learning_node_id = db.ForeignKey('phase3_learning_nodes.id')
```

---

## Why This Happened

Phase 1 and Phase 3 both tried to model a "curriculum" system:

**Phase 1 (`curriculum.py`)**:
- Basic curriculum structure for storing predefined learning paths
- Used for static content organization

**Phase 3 (`learning_node.py`)**:
- Advanced CEFR-based curriculum with adaptive learning
- Used for AI-driven personalized learning paths
- More sophisticated with skill tracking and difficulty adaptation

Both are valid but serve different purposes. Phase 3 is the enhanced version with AI intelligence.

---

## Impact

✅ **No breaking changes** - Phase 1 models still work  
✅ **Flask app starts successfully**  
✅ **No code changes needed** - Python imports already used aliases  
✅ **Foreign keys correctly reference new table names**  
✅ **Ready for database migration**  

---

## Next Steps

1. ✅ Table names fixed
2. ⏳ Run database migration: `flask db migrate -m "Phase 3: Learning nodes with phase3_ prefix"`
3. ⏳ Run migration: `flask db upgrade`
4. ⏳ Seed Phase 3 data (CEFR levels, skill domains)

---

**Status**: FIXED ✅  
**Date**: October 19, 2025  
**Flask app**: Running successfully
