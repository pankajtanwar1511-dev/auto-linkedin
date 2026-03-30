#!/usr/bin/env python3
"""
Evening Post Generator: Practice Tasks + Interview Q&A + Quick Reference
Uses ACTUAL HEIGHT MEASUREMENT for perfect grouping - no truncation!
"""

import os
import sys
import json
import shutil
import tempfile
import re
from jinja2 import Environment, FileSystemLoader
import markdown
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfMerger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def load_topic_data(chapter_num=1, topic_num=1):
    """Load specified topic from any chapter from LinkedIn working copy"""
    # Map chapter numbers to JSON filenames
    chapter_map = {
        1: 'chapter_1_oops',
        2: 'chapter_2_mamory_management',
        3: 'chapter_3_smart_pointers',
        4: 'chapter_4_reference_copying_moving',
        5: 'chapter_5_operator_overloading',
        6: 'chapter_6_type_system_casting',
        7: 'chapter_7_templates_generics',
        8: 'chapter_8_stl_containers_algorithms',
        9: 'chapter_9_cpp11_features',
        10: 'chapter_10_raii_resource_management',
        11: 'chapter_11_multithreading',
        12: 'chapter_12_design_patterns',
        13: 'chapter_13_compile_time_magic',
        14: 'chapter_14_low_level_tricky',
        15: 'chapter_15_cpp14_features',
        16: 'chapter_16_cpp17_features',
        17: 'chapter_17_software_architecture',
        18: 'chapter_18_network_programming',
        19: 'chapter_19_cpp20_features',
        20: 'chapter_20_advanced_implementations'
    }

    if chapter_num not in chapter_map:
        raise ValueError(f"Chapter {chapter_num} not found. Must be 1-20")

    json_filename = chapter_map[chapter_num] + '.json'
    json_path = os.path.join(
        os.path.dirname(__file__),
        'linkedin_json_output',
        json_filename
    )

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    topic_index = topic_num - 1  # Convert to 0-based
    if topic_index < 0 or topic_index >= len(data['topics']):
        raise ValueError(f"Topic {topic_num} out of range for Chapter {chapter_num}. Must be 1-{len(data['topics'])}")

    return data['topics'][topic_index], chapter_num, topic_num

def process_markdown_to_html(text):
    """Convert markdown to HTML"""
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
    html = md.convert(text)

    # Replace emoji checkmarks/crosses with styled HTML for PDF compatibility
    # ✅ → Green circle with white checkmark (renders perfectly in PDF)
    html = html.replace('✅', '<span style="display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; background-color: #10b981; color: white; border-radius: 50%; font-weight: 700; font-size: 14px; font-family: Arial, sans-serif;">&#10003;</span>')
    # ❌ → Red circle with white X (renders perfectly in PDF)
    html = html.replace('❌', '<span style="display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; background-color: #ef4444; color: white; border-radius: 50%; font-weight: 700; font-size: 14px; font-family: Arial, sans-serif;">&#10005;</span>')

    return html

def get_headless_browser():
    """Initialize headless Chrome browser for height measurement"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1080,2000')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def measure_raw_html_height(html_content, driver):
    """
    Measure height of raw HTML content WITHOUT full slide wrapper.
    Used for measuring code blocks and content fragments during splitting.
    """
    simple_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            width: 1010px;  /* Match slide content width */
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-size: 18px;
            line-height: 1.5;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 12px;
            border-radius: 6px;
            margin: 8px 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
        }}
        p {{
            margin: 6px 0;
            line-height: 1.5;
        }}
        strong {{
            color: #ec4899;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(simple_html)
        temp_file = f.name

    try:
        driver.get(f'file://{temp_file}')
        body = driver.find_element(By.TAG_NAME, 'body')
        height = driver.execute_script('return arguments[0].scrollHeight;', body)
        return height
    finally:
        os.unlink(temp_file)

def measure_actual_content_height(html_content, css, driver, show_concept_title=True):
    """
    Measure ACTUAL rendered height of content using real browser.
    Returns height in pixels.

    Args:
        html_content: The content HTML to measure
        css: CSS styles
        driver: Selenium WebDriver instance
        show_concept_title: Whether to include concept-title in measurement (True for questions, False for answers)
    """
    # Modify CSS to let concept-body expand naturally for measurement
    # We'll measure its natural height, then check if it fits in the constrained space
    css_for_measurement = css.replace(
        '/* Simplified: Let concept-body take available space and show content */\n    .concept-body {\n        flex: 1;                  /* Take up remaining space in flex container */\n        overflow-y: auto;\n        overflow-x: hidden;\n    }',
        '.concept-body {\n        height: auto;\n        overflow: visible;\n    }'
    ).replace(
        '/* Section containers should grow to fill space - ONLY inside slide-content */\n    .slide-content .section-practice,\n    .slide-content .section-interview,\n    .slide-content .section-quick-reference {\n        flex: 1;\n        display: flex;\n        flex-direction: column;\n        overflow: hidden;\n    }',
        '/* Measurement mode: let sections expand naturally */\n    .slide-content .section-practice,\n    .slide-content .section-interview,\n    .slide-content .section-quick-reference {\n        height: auto;\n    }'
    )

    # Include concept-title only if it will be shown in actual render
    concept_title_html = ""
    if show_concept_title:
        concept_title_html = """
                <div class="concept-title">
                    <span class="icon">❓</span>
                    <span>Practice Questions</span>
                </div>"""

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {css_for_measurement}
</head>
<body>
    <div class="slide">
        <div class="topic-header section-practice">
            <div class="topic-name">Classes, Structs, and Access Specifiers</div>
            <div class="section-name">Practice Tasks</div>
        </div>
        <main class="slide-content">
            <div class="section-practice">{concept_title_html}
                <div class="concept-body">
                    {html_content}
                </div>
            </div>
        </main>
    </div>
</body>
</html>"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(full_html)
        temp_file = f.name

    try:
        # Load in browser and measure
        driver.get(f'file://{temp_file}')

        # Get the natural height of concept-body (with height:auto)
        concept_body = driver.find_element(By.CLASS_NAME, 'concept-body')
        content_height = driver.execute_script('return arguments[0].scrollHeight;', concept_body)

        # Get topic-header height
        header = driver.find_element(By.CLASS_NAME, 'topic-header')
        header_height = header.size['height']

        # Get concept-title height if it exists
        concept_title_height = 0
        if show_concept_title:
            concept_title = driver.find_element(By.CLASS_NAME, 'concept-title')
            concept_title_height = concept_title.size['height']

        # Calculate total height needed
        # Slide-content has 40px padding (20px top + 20px bottom)
        # Total = header + concept_title + content + padding
        total_needed = header_height + concept_title_height + content_height + 40

        return total_needed
    finally:
        # Clean up temp file
        os.unlink(temp_file)

def smart_split_code_block(code_html, available_height, driver):
    """
    Intelligently split a code block using binary search to find optimal split point.
    Returns (first_part_html, remainder_html) or (code_html, None) if fits.
    """
    # Extract code content from <pre><code>...</code></pre>
    match = re.search(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', code_html, re.DOTALL)
    if not match:
        return code_html, None

    code_content = match.group(1)
    lines = code_content.split('\n')

    if len(lines) <= 1:
        return code_html, None

    # Binary search to find MAXIMUM split point that fits
    left, right = 1, len(lines)
    best_split = 1

    while left <= right:
        mid = (left + right) // 2
        test_lines = lines[:mid]
        test_code = '\n'.join(test_lines) + '\n// ...continues on next slide'
        test_html = f'<pre><code>{test_code}</code></pre>'

        test_height = measure_raw_html_height(test_html, driver)

        if test_height <= available_height:
            best_split = mid
            left = mid + 1
        else:
            right = mid - 1

    if best_split >= len(lines):
        return code_html, None

    # Split at best point
    first_part_lines = lines[:best_split]
    remainder_lines = lines[best_split:]

    first_part_lines.append('// ...continues on next slide')
    remainder_lines.insert(0, '// ...continued from previous slide')

    first_part_html = f'<pre><code>{chr(10).join(first_part_lines)}</code></pre>'
    remainder_html = f'<pre><code>{chr(10).join(remainder_lines)}</code></pre>'

    return first_part_html, remainder_html

def split_large_answer(item, css, driver, depth=0, max_depth=10):
    """
    Split a large answer into multiple parts that fit on separate slides.
    Returns list of items, each fitting within MAX_HEIGHT.

    Args:
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops
    """
    MAX_HEIGHT = 1050
    AVAILABLE_HEIGHT = 850  # Leave room for header

    # Prevent infinite recursion
    if depth >= max_depth:
        print(f"      ⚠️  Max recursion depth reached at depth {depth} - returning item as-is")
        return [item]

    # Process the full_content to HTML
    if item.get('full_content'):
        content_html = process_markdown_to_html(item['full_content'])
    else:
        # Build from parts
        parts = []
        if item.get('answer'):
            parts.append(f"<p><strong>Answer:</strong> {item['answer']}</p>")
        if item.get('explanation'):
            parts.append(process_markdown_to_html(item['explanation']))
        if item.get('solution'):
            parts.append(f'<p><strong>Solution:</strong></p>\n<pre><code>{item["solution"]}</code></pre>')
        content_html = '\n\n'.join(parts)

    # Check if it fits
    full_height = measure_actual_content_height(content_html, css, driver, show_concept_title=False)
    if full_height <= MAX_HEIGHT:
        return [item]

    # Need to split - find code blocks
    code_pattern = re.compile(r'<pre><code>(.*?)</code></pre>', re.DOTALL)
    codes = list(code_pattern.finditer(content_html))

    if not codes:
        # No code blocks - split at paragraph boundaries
        parts = content_html.split('</p>')
        result_items = []
        current_html = ''
        part_num = 1

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            test_html = current_html + part + '</p>'
            test_height = measure_actual_content_height(test_html, css, driver, show_concept_title=False)

            if test_height <= MAX_HEIGHT:
                current_html = test_html
            else:
                if current_html:
                    new_item = item.copy()
                    new_item['full_content'] = f"[Part {part_num}]\n\n" + current_html
                    result_items.append(new_item)
                    part_num += 1
                current_html = part + '</p>'

        if current_html:
            new_item = item.copy()
            new_item['full_content'] = f"[Part {part_num}]\n\n" + current_html
            result_items.append(new_item)

        return result_items if result_items else [item]

    # Has code blocks - split the largest one
    largest_code = max(codes, key=lambda m: len(m.group(1)))
    code_html = largest_code.group(0)

    # Get parts before and after code
    before_code = content_html[:largest_code.start()]
    after_code = content_html[largest_code.end():]

    # Try to split the code
    first_code, remainder_code = smart_split_code_block(code_html, AVAILABLE_HEIGHT, driver)

    if remainder_code:
        # Code needs splitting
        result_items = []

        # First part: everything before + first part of code
        item1 = item.copy()
        item1['full_content'] = before_code + '\n\n' + first_code
        result_items.append(item1)

        # Remaining parts: rest of code + everything after
        item2 = item.copy()
        item2['full_content'] = remainder_code + '\n\n' + after_code

        # Recursively split the remainder if still too large
        remainder_parts = split_large_answer(item2, css, driver, depth=depth+1, max_depth=max_depth)
        result_items.extend(remainder_parts)

        # Update part numbers
        for idx, part in enumerate(result_items, 1):
            if 'full_content' in part:
                if not part['full_content'].startswith('[Part'):
                    part['full_content'] = f"[Part {idx}/{len(result_items)}]\n\n" + part['full_content']

        return result_items
    else:
        # Code fits but overall doesn't - split before/after code
        result_items = []

        if before_code.strip():
            item1 = item.copy()
            item1['full_content'] = before_code
            result_items.append(item1)

        item2 = item.copy()
        item2['full_content'] = code_html + '\n\n' + after_code

        # Check if item2 still needs splitting
        test_height = measure_actual_content_height(
            process_markdown_to_html(item2['full_content']),
            css, driver, show_concept_title=False
        )

        if test_height <= MAX_HEIGHT:
            result_items.append(item2)
        else:
            remainder_parts = split_large_answer(item2, css, driver, depth=depth+1, max_depth=max_depth)
            result_items.extend(remainder_parts)

        # Update part numbers
        for idx, part in enumerate(result_items, 1):
            if 'full_content' in part:
                if not part['full_content'].startswith('[Part'):
                    part['full_content'] = f"[Part {idx}/{len(result_items)}]\n\n" + part['full_content']

        return result_items

def estimate_grouped_height(items, is_question=True):
    """
    Estimate height of grouped questions or answers.
    Questions: Optimized to fit 2-3 per slide
    Answers: Conservative to prevent truncation
    """
    total_height = 0
    for item in items:
        if is_question:
            # Question: title + description + code (11px) - OPTIMIZED for 2-3 per slide
            total_height += 50  # Title/number
            if item.get('description'):
                total_height += len(item['description']) * 0.22  # Realistic estimate
            if item.get('code'):
                code_lines = item['code'].count('\n') + 1
                total_height += 35 + code_lines * 14  # 11px code + line-height 1.25
            total_height += 15  # Separator/margins
        else:
            # Answer: answer + explanation + solution + key concept - CONSERVATIVE
            total_height += 50  # "Answer:" label
            if item.get('answer'):
                total_height += 40
            if item.get('explanation'):
                total_height += len(item['explanation']) * 0.18
            if item.get('full_content'):
                total_height += len(item['full_content']) * 0.15
            if item.get('solution'):
                code_lines = item.get('solution', '').count('\n') + 1
                total_height += 40 + code_lines * 16  # Conservative for answers
            if item.get('key_concept'):
                total_height += 30
            total_height += 50  # Separator

    return int(total_height)

def group_items_with_actual_measurement(items, is_question=True, css="", driver=None, content_type="practice"):
    """
    Group items using ACTUAL browser measurement - the greedy bin-packing approach!

    Algorithm:
    1. Start with empty slide
    2. Keep adding items one by one
    3. After each addition, measure ACTUAL rendered height
    4. If height > 1050px, remove last item and start new slide
    5. Repeat until all items grouped

    MAX_HEIGHT = 1050px (leaves 30px margin at bottom)

    Args:
        items: List of items to group
        is_question: True for questions, False for answers
        css: CSS styles
        driver: Selenium WebDriver instance
        content_type: "practice" or "interview" - determines which HTML generator to use
    """
    MAX_HEIGHT = 1050
    groups = []
    current_group = []

    # Close and reopen browser if needed
    need_to_close = False
    if driver is None:
        driver = get_headless_browser()
        need_to_close = True

    try:
        for idx, item in enumerate(items):
            # Try adding this item to current group
            test_group = current_group + [item]

            # Generate HTML for test group - USE THE CORRECT GENERATOR!
            if is_question:
                if content_type == "interview":
                    test_html = create_interview_question_html(test_group)
                else:
                    test_html = create_grouped_questions_html(test_group, "Practice")
            else:
                if content_type == "interview":
                    test_html = create_interview_answer_html(test_group)
                else:
                    test_html = create_grouped_answers_html(test_group)

            # Measure actual height (checks if content overflows)
            # Questions show concept-title, answers don't
            actual_height = measure_actual_content_height(test_html, css, driver, show_concept_title=is_question)

            is_overflow = actual_height > MAX_HEIGHT
            status = f"{actual_height}px ({'OVERFLOW' if is_overflow else 'fits'})"

            print(f"      Testing {'Q' if is_question else 'A'}{item.get('question_number', '?')}: "
                  f"{len(test_group)} items → {status}")

            if not is_overflow:
                # Fits! Add to current group
                current_group.append(item)
            else:
                # Doesn't fit!
                if current_group:
                    # Save current group (without new item)
                    groups.append(current_group)
                    print(f"      → Slide full! Moving {'Q' if is_question else 'A'}{item.get('question_number', '?')} to next slide")
                    current_group = []

                # Check if this single item needs splitting
                if not is_question:  # Only split answers, not questions
                    single_item_html = create_grouped_answers_html([item]) if content_type == "practice" else create_interview_answer_html([item])
                    single_height = measure_actual_content_height(single_item_html, css, driver, show_concept_title=False)

                    if single_height > MAX_HEIGHT:
                        # This single item is too large - split it!
                        print(f"      ⚠️  Answer {item.get('question_number', '?')} is too large ({single_height}px) - splitting into parts...")
                        split_parts = split_large_answer(item, css, driver)
                        print(f"      ✂️  Split into {len(split_parts)} parts")

                        # Each split part becomes its own group
                        for part in split_parts:
                            groups.append([part])
                        continue

                # Item fits by itself - start new group with it
                current_group = [item]

        # Add last group
        if current_group:
            groups.append(current_group)

        return groups
    finally:
        if need_to_close:
            driver.quit()

def create_grouped_questions_html(items, section_name="Practice"):
    """Create HTML for grouped questions"""
    html = f'<div style="font-size: 18px;">\n'  # Increased from 13px

    for idx, item in enumerate(items):
        q_num = item.get('question_number', '?')

        # Question header - just Q number
        html += f'<div style="margin-bottom: 14px;">\n'
        html += f'<p style="font-size: 20px; font-weight: 700; color: #3b82f6; margin-bottom: 8px;">'  # Increased from 14px
        html += f'Q{q_num}:</p>\n'

        # Question description
        if item.get('description'):
            html += f'<p style="margin: 8px 0;">{item["description"]}</p>\n'

        # Question code - show FULL code
        if item.get('code'):
            html += f'<pre style="background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 6px; '
            html += f'font-size: 14px; margin: 8px 0; line-height: 1.4;"><code>{item["code"]}</code></pre>\n'  # Increased from 11px

        # Expected output
        if item.get('expected_output'):
            html += f'<p style="margin: 6px 0; font-size: 16px;"><strong>Expected:</strong> <code>{item["expected_output"]}</code></p>\n'  # Increased from 12px

        # Add separator between questions (not after last one)
        if idx < len(items) - 1:
            html += '<div style="border-top: 1px dashed #cbd5e1; margin: 10px 0;"></div>\n'

        html += '</div>\n'

    html += '</div>'
    return html

def create_grouped_answers_html(items):
    """Create HTML for grouped answers"""
    html = '<div style="font-size: 18px;">\n'  # Increased from 13px

    for idx, item in enumerate(items):
        q_num = item.get('question_number', '?')

        html += f'<div style="margin-bottom: 14px;">\n'

        # Answer header
        html += f'<p style="font-size: 19px; font-weight: 700; color: #10b981; margin-bottom: 8px;">'  # Increased from 13px
        html += f'A{q_num}:</p>\n'

        # Use full_content if available
        if item.get('full_content'):
            content_html = process_markdown_to_html(item['full_content'])
            html += content_html
        else:
            # Fallback: build from parts
            if item.get('answer'):
                html += f'<p style="margin: 5px 0;"><strong>Answer:</strong> {item["answer"]}</p>\n'

            if item.get('explanation'):
                html += f'<p style="margin: 5px 0;"><strong>Explanation:</strong></p>\n'
                explanation_html = process_markdown_to_html(item['explanation'])
                html += explanation_html

            if item.get('solution'):
                # Show FULL solution code
                html += f'<p style="margin: 6px 0; font-size: 16px;"><strong>Solution:</strong></p>\n'  # Increased from 12px
                html += f'<pre style="background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 6px; '
                html += f'font-size: 14px; margin: 8px 0; line-height: 1.4;"><code>{item["solution"]}</code></pre>\n'  # Increased from 11px

            if item.get('key_concept'):
                html += f'<p style="margin: 6px 0; font-style: italic; color: #6366f1; font-size: 16px;">'  # Increased from 12px
                html += f'<strong>Key:</strong> {item["key_concept"]}</p>\n'

        # Add separator between answers (not after last one)
        if idx < len(items) - 1:
            html += '<div style="border-top: 2px double #94a3b8; margin: 10px 0;"></div>\n'

        html += '</div>\n'

    html += '</div>'
    return html

def create_interview_question_html(items):
    """Create HTML for grouped interview questions - compact format"""
    html = '<div style="font-size: 17px;">\n'  # Increased from 12px

    for idx, item in enumerate(items):
        q_num = item.get('question_number', '?')
        question = item.get('question', '')

        html += f'<div style="margin-bottom: 12px;">\n'

        # Question - compact format
        html += f'<p style="font-size: 18px; font-weight: 700; color: #3b82f6; margin-bottom: 5px;">'  # Increased from 13px
        html += f'Q{q_num}: {question}</p>\n'

        # Metadata - single line, smaller
        difficulty = item.get('difficulty', [])
        if isinstance(difficulty, list):
            difficulty = ', '.join(difficulty)

        category = item.get('category', [])
        if isinstance(category, list):
            category = ', '.join(category)

        html += f'<p style="font-size: 13px; color: #64748b; margin: 3px 0;">'  # Increased from 9px
        html += f'{difficulty} | {category}</p>\n'

        # Separator - thinner
        if idx < len(items) - 1:
            html += '<div style="border-top: 1px dashed #e5e7eb; margin: 8px 0;"></div>\n'

        html += '</div>\n'

    html += '</div>'
    return html

def create_interview_answer_html(items):
    """Create HTML for grouped interview answers - includes question text"""
    html = '<div style="font-size: 18px;">\n'  # Increased from 13px

    for idx, item in enumerate(items):
        q_num = item.get('question_number', '?')
        question_text = item.get('question', '')

        html += f'<div style="margin-bottom: 14px;">\n'

        # Question text - shown above answer for context
        if question_text:
            html += f'<p style="font-size: 18px; font-weight: 700; color: #3b82f6; margin-bottom: 6px;">'  # Increased from 13px
            html += f'Q{q_num}: {question_text}</p>\n'

        # Answer header
        html += f'<p style="font-size: 19px; font-weight: 700; color: #10b981; margin-bottom: 6px;">'  # Increased from 13px
        html += f'A{q_num}:</p>\n'

        # Answer
        if item.get('answer'):
            html += f'<p style="margin: 6px 0; font-size: 16px;"><strong>Answer:</strong> {item["answer"]}</p>\n'

        # Explanation
        if item.get('explanation'):
            explanation_html = process_markdown_to_html(item['explanation'])
            html += f'<div style="margin: 8px 0; font-size: 16px;">{explanation_html}</div>\n'

        # Code examples - show FULL code with 14px font (increased from 11px), limit to 1 example for space
        if item.get('code_examples'):
            for code_idx, code in enumerate(item['code_examples'][:1], 1):  # Limit to 1 example
                html += f'<pre style="background: #1e293b; color: #e2e8f0; padding: 12px; border-radius: 6px; '
                html += f'font-size: 14px; margin: 8px 0; line-height: 1.4;"><code>{code}</code></pre>\n'

        # Key takeaway
        if item.get('key_takeaway'):
            html += f'<p style="margin: 6px 0; font-style: italic; color: #6366f1; font-size: 16px;">'
            html += f'<strong>Key:</strong> {item["key_takeaway"]}</p>\n'

        # Separator
        if idx < len(items) - 1:
            html += '<div style="border-top: 2px double #94a3b8; margin: 10px 0;"></div>\n'

        html += '</div>\n'

    html += '</div>'
    return html

def create_improved_css():
    """CSS for evening posts with optimized text rendering"""
    return """
<style>
    * {
        /* High-quality text rendering for all elements */
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
        font-smooth: always;
    }

    html, body {
        margin: 0;
        padding: 0;
        overflow: hidden;
        width: 1080px;
        height: 1080px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }

    .slide {
        width: 1080px;
        height: 1080px;
        display: flex;
        flex-direction: column;
        background: white;
    }

    .slide-header {
        display: none;  /* Hide old header */
    }

    .topic-header {
        flex-shrink: 0;
        padding: 20px 35px 10px 35px;
    }

    /* Section-specific colors for evening */
    .topic-header.section-practice {
        border-bottom: 3px solid #a855f7;  /* Purple */
    }

    .topic-header.section-interview {
        border-bottom: 3px solid #f97316;  /* Orange */
    }

    .topic-header.section-quick-reference {
        border-bottom: 3px solid #14b8a6;  /* Teal */
    }

    .topic-name {
        font-size: 28px;          /* Increased from 20px for better readability */
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 5px 0;
        line-height: 1.3;
    }

    .section-name {
        font-size: 20px;          /* Increased from 15px */
        font-weight: 600;
        margin: 0;
    }

    .section-practice .section-name {
        color: #a855f7;
    }

    .section-interview .section-name {
        color: #f97316;
    }

    .section-quick-reference .section-name {
        color: #14b8a6;
    }

    .slide-content {
        flex: 1;
        padding: 20px 35px;
        overflow: hidden;
        font-size: 18px;          /* Increased from 13px for better readability */
        line-height: 1.5;
    }

    .slide-footer {
        display: none;  /* Hide footer */
    }

    .title-slide-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        text-align: center;
        padding: 40px;
    }

    .title-icon {
        font-size: 80px;
        margin-bottom: 20px;
    }

    .title-main {
        font-size: 42px;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 15px 0;
    }

    .title-subtitle {
        font-size: 28px;
        font-weight: 600;
        color: #3b82f6;
        margin: 0 0 30px 0;
        line-height: 1.3;
    }

    .concept-title {
        background: linear-gradient(135deg, #ec4899 0%, #d946ef 100%);
        color: white;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;          /* Increased from 16px */
        font-weight: 600;
        flex-shrink: 0;           /* Prevent shrinking when content is large */
    }

    /* Section-specific concept title colors */
    .section-practice .concept-title {
        background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
    }

    .section-interview .concept-title {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    }

    .section-quick-reference .concept-title {
        background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
    }

    /* Simplified: Let concept-body take available space and show content */
    .concept-body {
        flex: 1;                  /* Take up remaining space in flex container */
        overflow-y: auto;
        overflow-x: hidden;
    }

    /* Ensure slide-content is a flex container */
    .slide-content {
        display: flex;
        flex-direction: column;
    }

    /* Section containers should grow to fill space - ONLY inside slide-content */
    .slide-content .section-practice,
    .slide-content .section-interview,
    .slide-content .section-quick-reference {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .slide-content table {
        font-size: 16px;          /* Increased from 12px */
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-radius: 6px;
        overflow: hidden;
    }

    .slide-content th,
    .slide-content td {
        padding: 10px 12px;       /* Increased padding */
        border: 1px solid #e5e7eb;
        text-align: left;
        line-height: 1.6;
    }

    .slide-content th {
        background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
        color: white;
        font-weight: 600;
        font-size: 17px;          /* Increased from 13px */
    }

    .slide-content tr:nth-child(even) {
        background: #f9fafb;
    }

    .slide-content tr:hover {
        background: #f0fdfa;
    }

    .table-separator {
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
    }

    .table-separator::before {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #14b8a6 50%, transparent 100%);
    }

    .slide-content pre {
        background: #1e293b;
        color: #e2e8f0;
        padding: 12px;            /* Increased from 8px */
        border-radius: 6px;
        overflow-x: hidden;
        margin: 8px 0;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;          /* Increased from 11px */
        line-height: 1.4;
    }

    .slide-content code {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;          /* Increased from 11px */
    }

    .slide-content p {
        margin: 6px 0;
        line-height: 1.5;
    }

    .slide-content strong {
        color: #ec4899;
        font-weight: 600;
    }

    .slide-content ul, .slide-content ol {
        margin-left: 18px;
        margin-top: 6px;
    }

    .slide-content li {
        margin-bottom: 5px;
        line-height: 1.4;
    }

    .sections-list {
        max-width: 700px;
        margin: 30px auto;
    }

    .section-item {
        display: flex;
        align-items: center;
        padding: 20px 25px;
        margin: 15px 0;
        background: white;
        border-left: 4px solid;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .section-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .section-item.practice {
        border-left-color: #a855f7;
    }

    .section-item.interview {
        border-left-color: #f97316;
    }

    .section-item.reference {
        border-left-color: #14b8a6;
    }

    .section-icon {
        font-size: 36px;
        margin-right: 20px;
    }

    .section-details {
        flex: 1;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin: 0 0 5px 0;
    }

    .section-item.practice .section-title {
        color: #a855f7;
    }

    .section-item.interview .section-title {
        color: #f97316;
    }

    .section-item.reference .section-title {
        color: #14b8a6;
    }

    .section-count {
        font-size: 16px;
        color: #64748b;
        margin: 0;
    }
</style>
"""

def generate_evening_post(topic, template_dir, output_dir):
    """Generate evening post: Practice + Interview Q&A + Quick Reference"""

    print("\n" + "="*80)
    print("🌙 EVENING POST: Practice C++ - " + topic['topic'])
    print("="*80)

    env = Environment(loader=FileSystemLoader(template_dir))

    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="styles.css">
    {{ extra_css | safe }}
</head>
<body>
    <div class="slide">
        <header class="slide-header theme-{{ theme }}">
            <div class="header-left">
                <span class="header-icon">{{ header_icon }}</span>
                <span class="header-title">C++ Weekly Learning</span>
            </div>
            <div class="header-right">{{ header_right }}</div>
        </header>

        <div class="topic-header {{ section_class }}">
            <div class="topic-name">{{ full_topic_name }}</div>
            {% if slide_type != 'title' %}
            <div class="section-name">{{ section_type }}</div>
            {% endif %}
        </div>

        <main class="slide-content">
            {% if slide_type == 'title' %}
            <div class="title-slide-content">
                <div class="title-icon">{{ emoji }}</div>
                <h1 class="title-main">{{ session_name }}</h1>
                <h2 class="title-subtitle">{{ topic_name }}</h2>
                {% if subtitle %}
                <p style="font-size: 18px; color: #64748b; margin: 10px 0;">{{ subtitle }}</p>
                {% endif %}
            </div>
            {% elif slide_type == 'overview' %}
            <div class="title-slide-content">
                <div class="title-icon">{{ emoji }}</div>
                <h1 class="title-main">{{ session_name }}</h1>
                <h2 class="title-subtitle">{{ topic_name }}</h2>
                <div class="sections-list">
                    {{ sections_html | safe }}
                </div>
            </div>
            {% else %}
            <div class="{{ section_class }}">
                {% if show_concept_title %}
                <div class="concept-title">
                    <span class="icon">{{ icon }}</span>
                    <span>{{ concept_title }}</span>
                </div>
                {% endif %}
                <div class="concept-body">
                    {{ content_html | safe }}
                </div>
            </div>
            {% endif %}
        </main>

        <footer class="slide-footer">
            <div class="footer-brand">C++ Master Pro</div>
            <div class="footer-counter">[{{ slide_num }}/{{ total_slides }}]</div>
        </footer>
    </div>
</body>
</html>
"""

    template_path = os.path.join(template_dir, 'evening_template.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)

    template = env.get_template('evening_template.html')

    slides = []
    slide_num = 1

    # ===== COLLECT COUNTS =====
    practice_tasks = topic['practice_tasks']
    all_interview_qa = topic['interview_qa']
    top_10_qa = all_interview_qa[:10]
    quick_ref = topic['quick_reference']

    # Create sections HTML for overview slide
    sections_html = f'''
    <div class="section-item practice">
        <div class="section-icon">✍️</div>
        <div class="section-details">
            <h3 class="section-title">Practice Tasks</h3>
            <p class="section-count">{len(practice_tasks)} Questions & Answers</p>
        </div>
    </div>
    <div class="section-item interview">
        <div class="section-icon">💡</div>
        <div class="section-details">
            <h3 class="section-title">Interview Q&A</h3>
            <p class="section-count">Top {len(top_10_qa)} Questions & Answers</p>
        </div>
    </div>
    <div class="section-item reference">
        <div class="section-icon">📋</div>
        <div class="section-details">
            <h3 class="section-title">Quick Reference</h3>
            <p class="section-count">Essential Cheat Sheet</p>
        </div>
    </div>
    '''

    # Overview slide - shows all sections
    slides.append({
        'file': f'evening_slide_{slide_num:02d}_overview.html',
        'data': {
            'theme': 'practice', 'header_right': 'Evening Practice',
            'slide_num': slide_num, 'total_slides': 0,
            'title': f'Evening: {topic["topic"]}',
            'slide_type': 'overview',
            'section_class': 'section-practice',
            'full_topic_name': topic['topic'],
            'session_name': 'Evening Practice',
            'topic_name': topic['topic'],
            'emoji': '🌙',
            'header_icon': '🌙',
            'sections_html': sections_html,
            'extra_css': create_improved_css()
        }
    })
    slide_num += 1

    # Initialize browser once for all measurements
    print(f"\n   🔍 Using ACTUAL browser measurement for perfect grouping...")
    driver = get_headless_browser()
    css = create_improved_css()

    try:
        # Group questions using actual measurement
        print(f"\n   📝 Grouping Practice Questions (measuring actual heights)...")
        question_groups = group_items_with_actual_measurement(practice_tasks, is_question=True, css=css, driver=driver)
        print(f"   📝 Practice Tasks: {len(practice_tasks)} questions → {len(question_groups)} question slides")

        for group_idx, group in enumerate(question_groups, 1):
            q_numbers = [item['question_number'] for item in group]
            q_range = f"Q{q_numbers[0]}-Q{q_numbers[-1]}" if len(q_numbers) > 1 else f"Q{q_numbers[0]}"

            content_html = create_grouped_questions_html(group, "Practice")

            slides.append({
                'file': f'evening_slide_{slide_num:02d}_practice_q{group_idx}.html',
                'data': {
                    'theme': 'practice', 'header_right': 'Evening Practice',
                    'slide_num': slide_num, 'total_slides': 0,
                    'title': f'Evening: {topic["topic"]}',
                    'slide_type': 'concept',
                    'section_class': 'section-practice',
                    'full_topic_name': topic['topic'],
                    'section_type': 'Practice Tasks',
                    'concept_title': f'Practice Questions: {q_range}',
                    'content_html': content_html,
                    'icon': '❓',
                    'header_icon': '🌙',
                    'show_concept_title': True,  # Show for questions
                    'extra_css': create_improved_css()
                }
            })
            slide_num += 1

        # Group answers using actual measurement
        print(f"\n   📝 Grouping Practice Answers (measuring actual heights)...")
        answer_groups = group_items_with_actual_measurement(practice_tasks, is_question=False, css=css, driver=driver)
        print(f"   📝 Practice Tasks: {len(practice_tasks)} answers → {len(answer_groups)} answer slides")

        for group_idx, group in enumerate(answer_groups, 1):
            q_numbers = [item['question_number'] for item in group]
            q_range = f"A{q_numbers[0]}-A{q_numbers[-1]}" if len(q_numbers) > 1 else f"A{q_numbers[0]}"

            content_html = create_grouped_answers_html(group)

            slides.append({
                'file': f'evening_slide_{slide_num:02d}_practice_a{group_idx}.html',
                'data': {
                    'theme': 'practice', 'header_right': 'Evening Practice',
                    'slide_num': slide_num, 'total_slides': 0,
                    'title': f'Evening: {topic["topic"]}',
                    'slide_type': 'concept',
                    'section_class': 'section-practice',
                    'full_topic_name': topic['topic'],
                    'section_type': 'Practice Tasks',
                    'concept_title': f'Practice Answers: {q_range}',
                    'content_html': content_html,
                    'icon': '✅',
                    'header_icon': '🌙',
                    'show_concept_title': False,  # HIDE for answers
                    'extra_css': create_improved_css()
                }
            })
            slide_num += 1

        # ===== INTERVIEW Q&A (Top 10) =====
        # Group interview questions using actual measurement
        print(f"\n   💡 Grouping Interview Questions (measuring actual heights)...")
        interview_q_groups = group_items_with_actual_measurement(top_10_qa, is_question=True, css=css, driver=driver, content_type="interview")
        print(f"   💡 Interview Q&A: {len(top_10_qa)} questions → {len(interview_q_groups)} question slides")

        for group_idx, group in enumerate(interview_q_groups, 1):
            q_numbers = [item['question_number'] for item in group]
            q_range = f"Q{q_numbers[0]}-Q{q_numbers[-1]}" if len(q_numbers) > 1 else f"Q{q_numbers[0]}"

            content_html = create_interview_question_html(group)

            slides.append({
                'file': f'evening_slide_{slide_num:02d}_interview_q{group_idx}.html',
                'data': {
                    'theme': 'interview', 'header_right': 'Evening Practice',
                    'slide_num': slide_num, 'total_slides': 0,
                    'title': f'Evening: {topic["topic"]}',
                    'slide_type': 'concept',
                    'section_class': 'section-interview',
                    'full_topic_name': topic['topic'],
                    'section_type': 'Interview Q&A',
                    'concept_title': f'Interview Questions: {q_range}',
                    'content_html': content_html,
                    'icon': '❓',
                    'header_icon': '🌙',
                    'show_concept_title': True,  # Show for questions
                    'extra_css': create_improved_css()
                }
            })
            slide_num += 1

        # Group interview answers using actual measurement
        print(f"\n   💡 Grouping Interview Answers (measuring actual heights)...")
        interview_a_groups = group_items_with_actual_measurement(top_10_qa, is_question=False, css=css, driver=driver, content_type="interview")
        print(f"   💡 Interview Q&A: {len(top_10_qa)} answers → {len(interview_a_groups)} answer slides")

        for group_idx, group in enumerate(interview_a_groups, 1):
            q_numbers = [item['question_number'] for item in group]
            q_range = f"A{q_numbers[0]}-A{q_numbers[-1]}" if len(q_numbers) > 1 else f"A{q_numbers[0]}"

            content_html = create_interview_answer_html(group)

            slides.append({
                'file': f'evening_slide_{slide_num:02d}_interview_a{group_idx}.html',
                'data': {
                    'theme': 'interview', 'header_right': 'Evening Practice',
                    'slide_num': slide_num, 'total_slides': 0,
                    'title': f'Evening: {topic["topic"]}',
                    'slide_type': 'concept',
                    'section_class': 'section-interview',
                    'full_topic_name': topic['topic'],
                    'section_type': 'Interview Q&A',
                    'concept_title': f'Interview Answers: {q_range}',
                    'content_html': content_html,
                    'icon': '✅',
                    'header_icon': '🌙',
                    'show_concept_title': False,  # HIDE for answers
                    'extra_css': create_improved_css()
                }
            })
            slide_num += 1

        # ===== QUICK REFERENCE =====
        # Split QR tables into 2 slides to prevent overflow
        if 'tables' in quick_ref and quick_ref['tables']:
            # Slide 1: First 2 tables (struct vs class, inheritance types)
            if len(quick_ref['tables']) >= 2:
                slide1_html = ''
                for idx in range(2):
                    table_html = process_markdown_to_html(quick_ref['tables'][idx])
                    slide1_html += table_html
                    if idx < 1:  # Add separator between first two tables
                        slide1_html += '<div class="table-separator"></div>\n'

                slides.append({
                    'file': f'evening_slide_{slide_num:02d}_qr_tables_1.html',
                    'data': {
                        'theme': 'reference', 'header_right': 'Evening Practice',
                        'slide_num': slide_num, 'total_slides': 0,
                        'title': f'Evening: {topic["topic"]}',
                        'slide_type': 'concept',
                        'section_class': 'section-quick-reference',
                        'full_topic_name': topic['topic'],
                        'section_type': 'Quick Reference',
                        'concept_title': 'Reference Tables (1/2)',
                        'content_html': slide1_html,
                        'icon': '📋',
                        'header_icon': '🌙',
                        'show_concept_title': True,
                        'extra_css': create_improved_css()
                    }
                })
                slide_num += 1

            # Slide 2: Third table (access specifiers)
            if len(quick_ref['tables']) >= 3:
                slide2_html = process_markdown_to_html(quick_ref['tables'][2])

                slides.append({
                    'file': f'evening_slide_{slide_num:02d}_qr_tables_2.html',
                    'data': {
                        'theme': 'reference', 'header_right': 'Evening Practice',
                        'slide_num': slide_num, 'total_slides': 0,
                        'title': f'Evening: {topic["topic"]}',
                        'slide_type': 'concept',
                        'section_class': 'section-quick-reference',
                        'full_topic_name': topic['topic'],
                        'section_type': 'Quick Reference',
                        'concept_title': 'Reference Tables (2/2)',
                        'content_html': slide2_html,
                        'icon': '📋',
                        'header_icon': '🌙',
                        'show_concept_title': True,
                        'extra_css': create_improved_css()
                    }
                })
                slide_num += 1

        print(f"\n   📋 Quick Reference: {len(quick_ref.get('tables', []))} tables → 2 slides")

    finally:
        # Close the browser
        driver.quit()
        print(f"\n   ✅ Browser measurement complete")

    # Update totals
    for slide in slides:
        slide['data']['total_slides'] = len(slides)

    # Generate HTML
    evening_dir = os.path.join(output_dir, 'evening_practice')
    os.makedirs(evening_dir, exist_ok=True)

    # Copy CSS
    for file in ['styles.css', 'prism.css', 'prism.js', 'prism-cpp.js']:
        src = os.path.join(template_dir, file)
        dst = os.path.join(evening_dir, file)
        if os.path.exists(src):
            shutil.copy(src, dst)

    # Write HTML files
    for slide in slides:
        html = template.render(**slide['data'])
        with open(os.path.join(evening_dir, slide['file']), 'w', encoding='utf-8') as f:
            f.write(html)

    print(f"\n   ✅ Generated {len(slides)} HTML slides")

    # Generate PDFs directly with Playwright (preserves vector text!)
    print(f"   📄 Generating high-quality PDFs with Playwright...")
    print(f"   ℹ️  Using 2160x2160px @ scale=2 (4× effective resolution for quality)")

    html_files = sorted([f for f in os.listdir(evening_dir) if f.endswith('.html')])

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set viewport to match PDF output (2160×2160) to prevent empty space
        page.set_viewport_size({'width': 2160, 'height': 2160})

        for html_file in html_files:
            pdf_name = html_file.replace('.html', '.pdf')
            html_path = os.path.join(evening_dir, html_file)
            pdf_path = os.path.join(evening_dir, pdf_name)

            # Load HTML file
            page.goto(f'file://{html_path}')

            # Wait for content to be fully rendered
            page.wait_for_load_state('networkidle')

            # Generate PDF at 2× size with 2× scale = 4× effective resolution
            # 2160px = 30 inches @ 72 DPI, with scale=2 → effectively 4320px @ 144 DPI
            page.pdf(
                path=pdf_path,
                width='2160px',          # 2× native HTML size
                height='2160px',
                scale=2,                 # Max allowed scale (2× rendering quality)
                print_background=True,   # Include background colors/images
                prefer_css_page_size=False  # Use our custom size
            )

        browser.close()

    print(f"   ✅ Generated {len(html_files)} individual PDFs with vector text")

    # Merge all PDFs into one combined file
    print(f"\n   📚 Merging all PDFs into single carousel file...")
    combined_pdf_path = os.path.join(evening_dir, 'evening_practice_complete.pdf')
    merger = PdfMerger()

    # Get all PDF files in order (excluding any previous combined file)
    pdf_files = sorted([f for f in os.listdir(evening_dir)
                       if f.startswith('evening_slide_') and f.endswith('.pdf')])

    for pdf_file in pdf_files:
        pdf_path = os.path.join(evening_dir, pdf_file)
        merger.append(pdf_path)

    merger.write(combined_pdf_path)
    merger.close()

    print(f"   ✅ Created combined PDF with {len(pdf_files)} slides")
    print(f"   📄 Combined PDF: evening_practice_complete.pdf (ready for LinkedIn!)")
    print(f"\n   📂 Output: {evening_dir}")

    return len(slides), evening_dir

def main():
    # Parse command-line arguments
    chapter_num = 1  # default chapter
    topic_num = 1    # default topic

    if len(sys.argv) > 1:
        try:
            chapter_num = int(sys.argv[1])
            if chapter_num < 1 or chapter_num > 20:
                print("❌ Chapter number must be 1-20")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid chapter number. Usage: python3 generate_evening.py [CHAPTER] [TOPIC]")
            print("   Example: python3 generate_evening.py 12 6  # Generate for chapter 12, topic 6")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            topic_num = int(sys.argv[2])
            if topic_num < 1:
                print("❌ Topic number must be >= 1")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid topic number. Usage: python3 generate_evening.py [CHAPTER] [TOPIC]")
            print("   Example: python3 generate_evening.py 12 6  # Generate for chapter 12, topic 6")
            sys.exit(1)

    topic, chapter_num, topic_num = load_topic_data(chapter_num, topic_num)
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    output_base = os.path.join(os.path.dirname(__file__), 'output', f'ch{chapter_num}_topic{topic_num:02d}')
    os.makedirs(output_base, exist_ok=True)

    slides_count, output_dir = generate_evening_post(topic, template_dir, output_base)

    print("\n" + "="*80)
    print("🎉 EVENING POST COMPLETE!")
    print("="*80)
    print(f"✅ Total slides: {slides_count}")
    print(f"📂 Location: {output_dir}")
    print("="*80)

if __name__ == '__main__':
    main()
