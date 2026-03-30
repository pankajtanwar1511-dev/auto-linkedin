#!/usr/bin/env python3
"""
Batch Morning Post Generator: Generate PDFs for all 88 topics
"""

import os
import json
import sys
import shutil
import subprocess
from datetime import datetime

# Import from generate_morning
from generate_morning import load_topic_data, generate_morning_post

def main():
    # Load topic mapping
    if not os.path.exists('topic_mapping.json'):
        print("❌ topic_mapping.json not found. Run generate_all_morning.sh first")
        sys.exit(1)

    with open('topic_mapping.json', 'r') as f:
        mapping = json.load(f)

    total_topics = len(mapping)
    print(f"📚 Found {total_topics} topics across all chapters\n")

    # Create final collection directory
    final_dir = 'final_pdfs_collection'
    os.makedirs(final_dir, exist_ok=True)

    # Clean up old output directory
    if os.path.exists('output'):
        print("🗑️  Cleaning old output directory...")
        shutil.rmtree('output')

    template_dir = os.path.join(os.path.dirname(__file__), 'templates')

    successful = 0
    failed = []

    for item in mapping:
        global_num = item['global_num']
        chapter_num = item['chapter']
        topic_index = item['topic_index']
        topic_name = item['topic_name']

        print(f"\n{'='*80}")
        print(f"📖 Topic {global_num}/{total_topics}: Ch{chapter_num}, Topic{topic_index+1}")
        print(f"   {topic_name}")
        print(f"{'='*80}")

        try:
            # Load topic data
            topic, chapter_name = load_topic_data(chapter_num, topic_index)

            # Output directory for this topic
            output_base = os.path.join(
                os.path.dirname(__file__),
                'output',
                f'ch{chapter_num}_topic{topic_index+1}'
            )
            os.makedirs(output_base, exist_ok=True)

            # Generate PDFs
            slides_count, output_dir = generate_morning_post(topic, template_dir, output_base)

            # Copy final PDF to collection
            src_pdf = os.path.join(output_dir, 'morning_learn_complete.pdf')
            dest_pdf = os.path.join(
                final_dir,
                f'ch{chapter_num:02d}_topic{topic_index+1:02d}_morning.pdf'
            )

            if os.path.exists(src_pdf):
                shutil.copy(src_pdf, dest_pdf)
                file_size = os.path.getsize(dest_pdf) / (1024 * 1024)  # MB
                print(f"\n   ✅ Success: {slides_count} slides, {file_size:.1f} MB")
                print(f"   📄 Saved to: {dest_pdf}")
                successful += 1
            else:
                print(f"\n   ❌ Failed: PDF not found at {src_pdf}")
                failed.append((global_num, topic_name))

        except Exception as e:
            print(f"\n   ❌ Error: {str(e)}")
            failed.append((global_num, topic_name))

    # Summary
    print(f"\n\n{'='*80}")
    print(f"🎉 BATCH GENERATION COMPLETE!")
    print(f"{'='*80}")
    print(f"✅ Successful: {successful}/{total_topics}")

    if failed:
        print(f"❌ Failed: {len(failed)}")
        for num, name in failed:
            print(f"   - Topic {num}: {name}")
    else:
        print(f"✨ All topics generated successfully!")

    print(f"\n📂 Final PDFs location: {os.path.abspath(final_dir)}/")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
