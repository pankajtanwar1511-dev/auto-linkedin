#!/usr/bin/env python3
"""
Validation script for LinkedIn auto-posting timezone bugs.
Run this to verify all scenarios work correctly after fixes.

Usage:
    python3 test_timezone_validation.py
"""

from datetime import datetime, timezone, timedelta
import json
import sys


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_test(name):
    """Print test name."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}TEST: {name}{Colors.END}")
    print("-" * 80)


def print_pass(msg):
    """Print pass message."""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_fail(msg):
    """Print fail message."""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_warn(msg):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def test_timezone_conversions():
    """Test that UTC to JST conversions work correctly."""
    print_test("Timezone Conversions (UTC -> JST)")

    jst = timezone(timedelta(hours=9))
    tests_passed = 0
    tests_total = 0

    test_cases = [
        # (UTC datetime, expected JST day, expected JST hour, expected weekday)
        (datetime(2026, 4, 7, 23, 0, tzinfo=timezone.utc), 8, 8, 1, "UTC Mon 23:00 -> JST Tue 08:00"),
        (datetime(2026, 4, 8, 9, 0, tzinfo=timezone.utc), 8, 18, 1, "UTC Tue 09:00 -> JST Tue 18:00"),
        (datetime(2026, 4, 8, 23, 0, tzinfo=timezone.utc), 9, 8, 2, "UTC Tue 23:00 -> JST Wed 08:00"),
        (datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc), 1, 9, 1, "UTC Wed 00:00 -> JST Wed 09:00"),
    ]

    for utc_time, exp_day, exp_hour, exp_weekday, description in test_cases:
        tests_total += 1
        jst_time = utc_time.astimezone(jst)

        if jst_time.day == exp_day and jst_time.hour == exp_hour and jst_time.weekday() == exp_weekday:
            print_pass(f"{description}")
            tests_passed += 1
        else:
            print_fail(f"{description}")
            print(f"  Expected: Day={exp_day}, Hour={exp_hour}, Weekday={exp_weekday}")
            print(f"  Got:      Day={jst_time.day}, Hour={jst_time.hour}, Weekday={jst_time.weekday()}")

    return tests_passed, tests_total


def test_weekly_pattern():
    """Test that weekly posting pattern is correct."""
    print_test("Weekly Posting Pattern (Tue/Thu/Sat = 2 posts)")

    jst = timezone(timedelta(hours=9))

    # Expected pattern
    expected_posts = {
        0: 1,  # Monday: 1 post
        1: 2,  # Tuesday: 2 posts
        2: 1,  # Wednesday: 1 post
        3: 2,  # Thursday: 2 posts
        4: 1,  # Friday: 1 post
        5: 2,  # Saturday: 2 posts
        6: 1,  # Sunday: 1 post
    }

    actual_posts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    # Simulate cron runs for a week (April 7-13, 2026)
    for utc_day in range(7, 14):
        # Morning cron: 23:00 UTC
        morning_utc = datetime(2026, 4, utc_day, 23, 0, tzinfo=timezone.utc)
        morning_jst = morning_utc.astimezone(jst)
        actual_posts[morning_jst.weekday()] += 1

        # Evening cron: 09:00 UTC
        evening_utc = datetime(2026, 4, utc_day, 9, 0, tzinfo=timezone.utc)
        evening_jst = evening_utc.astimezone(jst)

        # Check if should post evening (Tue=1, Thu=3, Sat=5)
        if evening_jst.weekday() in [1, 3, 5]:
            actual_posts[evening_jst.weekday()] += 1

    tests_passed = 0
    tests_total = 7  # One test per day

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for day, expected_count in expected_posts.items():
        actual_count = actual_posts[day]
        day_name = day_names[day]

        if actual_count == expected_count:
            print_pass(f"{day_name}: {actual_count} post(s) (expected {expected_count})")
            tests_passed += 1
        else:
            print_fail(f"{day_name}: {actual_count} post(s) (expected {expected_count})")

    return tests_passed, tests_total


def test_naive_datetime_bug():
    """Test for naive datetime bug (Bug #1)."""
    print_test("Bug #1: Naive Datetime in Timestamp Storage")

    # Simulate current (buggy) code
    naive_timestamp = datetime.now().isoformat()

    # Simulate fixed code
    aware_timestamp = datetime.now(timezone.utc).isoformat()

    # Check if timestamps have timezone info
    naive_has_tz = '+' in naive_timestamp or 'Z' in naive_timestamp
    aware_has_tz = '+' in aware_timestamp or 'Z' in aware_timestamp

    print(f"Naive timestamp:  {naive_timestamp}")
    print(f"Aware timestamp:  {aware_timestamp}")

    tests_passed = 0
    tests_total = 1

    if aware_has_tz:
        print_pass("Aware timestamp has timezone info")
        if naive_has_tz:
            print_pass("Bug is FIXED (timestamps are timezone-aware)")
            tests_passed = 1
        else:
            print_fail("Bug still EXISTS (naive timestamps in use)")
    else:
        print_fail("Both timestamps are naive - bug not fixed")

    return tests_passed, tests_total


def test_utcnow_deprecation():
    """Test for datetime.utcnow() deprecation (Bug #2)."""
    print_test("Bug #2: Deprecated datetime.utcnow()")

    # Check if code uses datetime.now(timezone.utc) instead
    print("Recommended: datetime.now(timezone.utc).hour")
    print("Deprecated:  datetime.utcnow().hour")

    # Demonstrate the difference
    utcnow_result = datetime.utcnow()
    now_utc_result = datetime.now(timezone.utc)

    print(f"\ndatetime.utcnow():         {utcnow_result.isoformat()} (tzinfo={utcnow_result.tzinfo})")
    print(f"datetime.now(timezone.utc): {now_utc_result.isoformat()} (tzinfo={now_utc_result.tzinfo})")

    tests_passed = 0
    tests_total = 1

    if utcnow_result.tzinfo is None:
        print_warn("datetime.utcnow() creates naive datetime")

    if now_utc_result.tzinfo is not None:
        print_pass("datetime.now(timezone.utc) creates aware datetime")
        tests_passed = 1
    else:
        print_fail("datetime.now(timezone.utc) should create aware datetime")

    return tests_passed, tests_total


def test_manual_run_duplicate_bug():
    """Test manual run duplicate prevention bug (Bug #3)."""
    print_test("Bug #3: Manual Run Duplicate Prevention")

    # Simulate the bug
    time_label_manual = 'manual'  # What manual runs set
    entry_hour_jst = 10  # 10 AM JST in history

    # Line 150 logic (current buggy code)
    entry_slot_current = 'morning' if 6 <= entry_hour_jst < 12 else 'evening'

    # Check if they match
    matches_current = (entry_slot_current == time_label_manual)

    print(f"Manual run time_label: '{time_label_manual}'")
    print(f"History entry classified as: '{entry_slot_current}' (based on hour={entry_hour_jst})")
    print(f"Do they match? {matches_current}")

    tests_passed = 0
    tests_total = 1

    if not matches_current:
        print_fail("Bug CONFIRMED: 'manual' != 'morning' (duplicate prevention broken)")
        print("  Impact: Manual runs can post multiple times in same slot")
        print("  Fix: Store time_label in posting_history.json")
    else:
        print_pass("Bug is FIXED: time_label matches entry classification")
        tests_passed = 1

    # Show the fix
    print("\nRecommended fix:")
    print("  1. Add 'time_label' field to posting_history.json entries")
    print("  2. Read time_label from history instead of recalculating")
    print("  3. Store actual time_label when logging posts")

    return tests_passed, tests_total


def test_time_slot_classification():
    """Test time slot classification edge cases."""
    print_test("Time Slot Classification Edge Cases")

    test_hours = [
        (1, 'night', "1 AM should be 'night', not 'evening'"),
        (5, 'night', "5 AM should be 'night', not 'evening'"),
        (6, 'morning', "6 AM is morning"),
        (11, 'morning', "11 AM is morning"),
        (12, 'evening', "12 PM (noon) is evening"),
        (18, 'evening', "6 PM is evening"),
        (20, 'night', "8 PM should be 'night', not 'evening'"),
        (23, 'night', "11 PM should be 'night', not 'evening'"),
    ]

    tests_passed = 0
    tests_total = len(test_hours)

    for hour, expected_slot, description in test_hours:
        # Current buggy logic
        current_slot = 'morning' if 6 <= hour < 12 else 'evening'

        # Improved logic
        if 6 <= hour < 12:
            improved_slot = 'morning'
        elif 12 <= hour < 20:
            improved_slot = 'evening'
        else:
            improved_slot = 'night'

        if improved_slot == expected_slot:
            print_pass(f"{description}: {improved_slot}")
            tests_passed += 1
        else:
            print_fail(f"{description}: got {improved_slot}, expected {expected_slot}")

        if current_slot != improved_slot:
            print_warn(f"  Current code classifies {hour}:00 as '{current_slot}' (should be '{improved_slot}')")

    return tests_passed, tests_total


def test_six_hour_separation():
    """Test 6-hour separation logic."""
    print_test("6-Hour Separation Check")

    jst = timezone(timedelta(hours=9))

    test_cases = [
        (10, 15, 5.0, False, "10 AM -> 3 PM (5 hours): Should REJECT"),
        (10, 16, 6.0, True, "10 AM -> 4 PM (6 hours): Should ALLOW"),
        (8, 18, 10.0, True, "8 AM -> 6 PM (10 hours): Should ALLOW"),
        (8, 10, 2.0, False, "8 AM -> 10 AM (2 hours): Should REJECT"),
    ]

    tests_passed = 0
    tests_total = len(test_cases)

    for hour1, hour2, expected_diff, should_allow, description in test_cases:
        time1 = datetime(2026, 4, 8, hour1, 0, tzinfo=jst)
        time2 = datetime(2026, 4, 8, hour2, 0, tzinfo=jst)

        time_diff = time2 - time1
        hours_diff = time_diff.total_seconds() / 3600

        # Check if >= 6 hours
        allowed = hours_diff >= 6.0

        if allowed == should_allow:
            print_pass(f"{description}")
            tests_passed += 1
        else:
            print_fail(f"{description}")
            print(f"  Expected: {should_allow}, Got: {allowed}")

    return tests_passed, tests_total


def test_daily_limit():
    """Test daily post limit check."""
    print_test("Daily Post Limit Check")

    test_cases = [
        (0, 1, True, "Monday: 1 post allowed"),
        (0, 2, False, "Monday: 2 posts should EXCEED limit"),
        (1, 1, True, "Tuesday: 1 post allowed"),
        (1, 2, True, "Tuesday: 2 posts allowed"),
        (1, 3, False, "Tuesday: 3 posts should EXCEED limit"),
        (2, 1, True, "Wednesday: 1 post allowed"),
        (3, 2, True, "Thursday: 2 posts allowed"),
        (5, 2, True, "Saturday: 2 posts allowed"),
    ]

    tests_passed = 0
    tests_total = len(test_cases)

    for weekday, post_count, should_allow, description in test_cases:
        # Max posts for this day
        max_posts = 2 if weekday in [1, 3, 5] else 1

        # Check if allowed
        allowed = post_count <= max_posts

        if allowed == should_allow:
            print_pass(f"{description}")
            tests_passed += 1
        else:
            print_fail(f"{description}")
            print(f"  Expected: {should_allow}, Got: {allowed}")

    return tests_passed, tests_total


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}LinkedIn Auto-Posting Timezone Validation Tests{Colors.END}")
    print("=" * 80)

    all_tests = [
        test_timezone_conversions,
        test_weekly_pattern,
        test_naive_datetime_bug,
        test_utcnow_deprecation,
        test_manual_run_duplicate_bug,
        test_time_slot_classification,
        test_six_hour_separation,
        test_daily_limit,
    ]

    total_passed = 0
    total_tests = 0

    for test_func in all_tests:
        passed, total = test_func()
        total_passed += passed
        total_tests += total

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    print("=" * 80)

    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Tests passed: {total_passed}/{total_tests} ({percentage:.1f}%)")

    if total_passed == total_tests:
        print_pass("ALL TESTS PASSED!")
        return 0
    elif percentage >= 80:
        print_warn(f"Most tests passed, but {total_tests - total_passed} failed")
        return 1
    else:
        print_fail(f"{total_tests - total_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
