#!/bin/bash
# Cleanup and regenerate evening slides for Chapter 12 Topic 6

cd /home/pankaj/cplusplus/proCplusplus/linkedin_automation

echo "🗑️  Deleting old evening practice files..."
rm -rf output/ch12_topic06/evening_practice

echo "✅ Old files deleted"
echo ""
echo "🔄 Regenerating fresh evening slides..."
python3 generate_evening_from_morning.py 12 6

echo ""
echo "✅ Done! Check output/ch12_topic06/evening_practice/"
