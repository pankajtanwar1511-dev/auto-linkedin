#!/usr/bin/env python3
"""
Test script to verify improved posting_history.json structure.
Verifies the new fields: post_number, calendar_date_jst, time_label
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

def test_improved_logging_structure():
    """Test the improved logging structure in posting_history.json"""
    print("\n" + "="*60)
    print("Testing Improved Logging Structure")
    print("="*60)

    history_file = Path(__file__).parent / "linkedin_app" / "logs" / "posting_history.json"

    if not history_file.exists():
        print("❌ FAIL: posting_history.json not found")
        return False

    with open(history_file, 'r') as f:
        history = json.load(f)

    if not history:
        print("❌ FAIL: posting_history.json is empty")
        return False

    print(f"\n✅ Found {len(history)} entries in posting_history.json\n")

    # Test each entry
    all_pass = True
    for i, entry in enumerate(history, 1):
        print(f"Entry {i}:")
        print(f"  Timestamp: {entry.get('timestamp', 'MISSING')}")

        # Check for improved fields
        checks = {
            'post_number': entry.get('post_number'),
            'calendar_date_jst': entry.get('calendar_date_jst'),
            'time_label': entry.get('time_label')
        }

        for field, value in checks.items():
            if value is not None:
                print(f"  ✅ {field}: {value}")
            else:
                print(f"  ⚠️  {field}: MISSING (old format)")
                if field == 'post_number' and 'day' in entry:
                    print(f"     (has old 'day' field: {entry['day']})")

        # Check timezone awareness
        timestamp = entry.get('timestamp', '')
        if '+' in timestamp or 'Z' in timestamp:
            print(f"  ✅ Timezone-aware timestamp")
        else:
            print(f"  ⚠️  Naive timestamp (no timezone)")

        print()

    # Analyze calendar dates
    print("="*60)
    print("Calendar Date Analysis:")
    print("="*60)

    dates = {}
    for entry in history:
        if 'calendar_date_jst' in entry:
            date = entry['calendar_date_jst']
            post_num = entry.get('post_number', entry.get('day', '?'))
            time_slot = entry.get('time_label', '?')

            if date not in dates:
                dates[date] = []
            dates[date].append((post_num, time_slot))

    for date, posts in sorted(dates.items()):
        print(f"\n📅 {date}:")
        for post_num, time_slot in posts:
            print(f"   Post {post_num} - {time_slot}")

        if len(posts) > 1:
            print(f"   ✅ {len(posts)} posts on same day (visible!)")

    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    has_new_fields = any('post_number' in e and 'calendar_date_jst' in e and 'time_label' in e for e in history)
    has_timezone = any('+' in e.get('timestamp', '') or 'Z' in e.get('timestamp', '') for e in history)

    if has_new_fields:
        print("✅ New improved fields present (post_number, calendar_date_jst, time_label)")
    else:
        print("⚠️  Still using old format (day field without calendar_date_jst)")

    if has_timezone:
        print("✅ Timezone-aware timestamps present")
    else:
        print("⚠️  Naive timestamps (no timezone)")

    if has_new_fields and has_timezone:
        print("\n🎉 LOGGING STRUCTURE IMPROVED! ✅")
        print("\nBenefits:")
        print("  • Clear post numbering (post_number instead of day)")
        print("  • Visible calendar dates in JST")
        print("  • Time slot labels (morning/evening/manual)")
        print("  • Timezone-aware timestamps")
        print("  • Easy to see multiple posts on same day!")
        return True
    else:
        print("\n⚠️  Still using legacy format")
        print("New posts will use improved format.")
        return False

def main():
    """Run the test"""
    try:
        result = test_improved_logging_structure()
        return 0 if result else 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
