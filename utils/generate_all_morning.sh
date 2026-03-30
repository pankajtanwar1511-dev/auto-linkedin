#!/bin/bash
# Generate morning PDFs for all 88 topics across all chapters

# Build chapter-topic mapping from JSON files
python3 << 'EOF'
import json
import os

json_dir = 'linkedin_json_output'
chapters = sorted([f for f in os.listdir(json_dir) if f.startswith('chapter_') and f.endswith('.json')])

# Build mapping: global_topic_num -> (chapter_num, topic_index, topic_name)
mapping = []
global_num = 1

for chapter_file in chapters:
    chapter_num = int(chapter_file.split('_')[1])

    with open(os.path.join(json_dir, chapter_file), 'r') as f:
        data = json.load(f)

    for topic_idx, topic in enumerate(data['topics']):
        mapping.append({
            'global_num': global_num,
            'chapter': chapter_num,
            'topic_index': topic_idx,
            'topic_name': topic['topic']
        })
        global_num += 1

# Save mapping
with open('topic_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)

print(f"✅ Created mapping for {len(mapping)} topics")
for item in mapping[:5]:
    print(f"   Topic {item['global_num']}: Ch{item['chapter']}, Topic{item['topic_index']+1} - {item['topic_name'][:50]}...")
print(f"   ...")
for item in mapping[-2:]:
    print(f"   Topic {item['global_num']}: Ch{item['chapter']}, Topic{item['topic_index']+1} - {item['topic_name'][:50]}...")
EOF

echo ""
echo "🚀 Starting batch generation of all 88 topics..."
echo ""

# Generate all topics
python3 generate_all_morning.py

echo ""
echo "✅ All morning PDFs generated!"
echo "📂 Output location: final_pdfs_collection/"
