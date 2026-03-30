# LinkedIn JSON Output - Working Copy

This directory contains **filtered copies** of the original JSON files specifically for LinkedIn content generation.

## Purpose

- **Original files**: Kept in `processed_data/json_output/` (untouched)
- **LinkedIn copies**: This directory (filtered for LinkedIn posting)

## Filters Applied

### 1. Autonomous Vehicle Examples Removed
- All "Autonomous Vehicle" examples have been removed from these copies
- Original files retain all examples for other purposes
- 35 examples removed across 14 chapters

## Updating This Directory

If you update the original JSON files in `processed_data/json_output/`, run this script to update the LinkedIn copies:

```bash
cd /home/pankaj/cplusplus/proCplusplus

# Step 1: Copy updated originals
cp processed_data/json_output/*.json linkedin_automation/linkedin_json_output/

# Step 2: Apply filters
cd linkedin_automation/linkedin_json_output
python3 << 'EOF'
import json
import glob

for json_file in glob.glob('*.json'):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'topics' in data:
        for topic in data['topics']:
            if 'code_examples' in topic:
                topic['code_examples'] = [
                    e for e in topic['code_examples']
                    if 'Autonomous Vehicle' not in e.get('title', '')
                ]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Updated LinkedIn copies with filters applied")
EOF
```

## File Count

- **21 JSON files** (20 chapters + master_index.json)
- All filtered for LinkedIn content requirements

## Used By

- `generate_morning.py` - Morning post generator
- `generate_evening.py` - Evening post generator

---

**Last Updated:** March 27, 2026
