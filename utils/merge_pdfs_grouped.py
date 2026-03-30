#!/usr/bin/env python3
"""
Merge individual topic PDFs into 3 grouped PDFs:
1. Chapters 1-10 (Fundamentals)
2. Chapters 11-17 (Advanced Topics)
3. Chapters 18-20 (Modern C++)
"""

import os
import json
from PyPDF2 import PdfMerger

def main():
    # Load topic mapping
    if not os.path.exists('topic_mapping.json'):
        print("❌ topic_mapping.json not found")
        return

    with open('topic_mapping.json', 'r') as f:
        mapping = json.load(f)

    # Define chapter groups
    groups = [
        {
            'name': 'Part1_Fundamentals_Ch01-10',
            'chapters': range(1, 11),  # Chapters 1-10
            'description': 'Chapters 1-10: C++ Fundamentals'
        },
        {
            'name': 'Part2_Advanced_Ch11-17',
            'chapters': range(11, 18),  # Chapters 11-17
            'description': 'Chapters 11-17: Advanced Topics'
        },
        {
            'name': 'Part3_Modern_Ch18-20',
            'chapters': range(18, 21),  # Chapters 18-20
            'description': 'Chapters 18-20: Modern C++ & Implementations'
        }
    ]

    collection_dir = 'final_pdfs_collection'

    # Create merged PDFs for each group
    for group in groups:
        print(f"\n{'='*80}")
        print(f"📚 Creating: {group['name']}.pdf")
        print(f"   {group['description']}")
        print(f"{'='*80}")

        merger = PdfMerger()
        topic_count = 0
        total_pages = 0

        # Filter topics for this chapter range
        for item in mapping:
            chapter = item['chapter']
            if chapter in group['chapters']:
                topic_index = item['topic_index']
                global_num = item['global_num']
                topic_name = item['topic_name']

                # PDF filename
                pdf_file = f'ch{chapter:02d}_topic{topic_index+1:02d}_morning.pdf'
                pdf_path = os.path.join(collection_dir, pdf_file)

                if os.path.exists(pdf_path):
                    print(f"   ✅ Adding Topic {global_num}: Ch{chapter}, Topic{topic_index+1} - {topic_name[:50]}...")
                    merger.append(pdf_path)
                    topic_count += 1

                    # Count pages
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    pages = len(reader.pages)
                    total_pages += pages
                else:
                    print(f"   ⚠️  Missing: {pdf_file}")

        # Write merged PDF
        output_path = os.path.join(collection_dir, f'{group["name"]}.pdf')
        merger.write(output_path)
        merger.close()

        # Get file size
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB

        print(f"\n   ✅ Created: {group['name']}.pdf")
        print(f"   📊 Topics: {topic_count}")
        print(f"   📄 Pages: {total_pages}")
        print(f"   💾 Size: {file_size:.1f} MB")

    print(f"\n\n{'='*80}")
    print(f"🎉 ALL MERGED PDFs CREATED!")
    print(f"{'='*80}")
    print(f"📂 Location: {os.path.abspath(collection_dir)}/")
    print(f"\n📚 Files created:")
    for group in groups:
        pdf_path = os.path.join(collection_dir, f'{group["name"]}.pdf')
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path) / (1024 * 1024)
            print(f"   ✅ {group['name']}.pdf ({size:.1f} MB)")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
