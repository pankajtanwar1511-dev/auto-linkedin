#!/usr/bin/env python3
"""
Evening Post Generator: Practice + Interview Q&A + Quick Reference
Generates evening practice content (40+ slides) - based on morning script logic
"""

import os
import sys
import json
import shutil
import tempfile
from jinja2 import Environment, FileSystemLoader
import markdown
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfMerger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def load_topic_data(chapter_num, topic_index):
    """Load specified topic from any chapter from LinkedIn working copy

    Args:
        chapter_num: Chapter number (1-20)
        topic_index: Topic index within chapter (0-based)

    Returns:
        Topic data dictionary
    """
    # Find the chapter file
    json_dir = os.path.join(os.path.dirname(__file__), 'linkedin_json_output')

    # List all chapter files and find the one matching chapter_num
    chapter_files = [f for f in os.listdir(json_dir) if f.startswith(f'chapter_{chapter_num}_') and f.endswith('.json')]

    if not chapter_files:
        raise ValueError(f"Chapter {chapter_num} not found in {json_dir}")

    json_path = os.path.join(json_dir, chapter_files[0])

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if topic_index < 0 or topic_index >= len(data['topics']):
        raise ValueError(f"Topic index {topic_index} out of range for chapter {chapter_num}. Must be 0-{len(data['topics'])-1}")

    return data['topics'][topic_index], data['chapter_name']

def split_long_code_blocks(markdown_text, max_lines=35):
    """
    Split code blocks longer than max_lines into multiple chunks.

    Args:
        markdown_text: Markdown content with code blocks
        max_lines: Maximum lines per code block (default 35)

    Returns:
        Modified markdown with split code blocks
    """
    import re

    # Find all code blocks
    code_block_pattern = r'```(\w+)?\n(.*?)```'

    def split_code_block(match):
        language = match.group(1) or 'cpp'
        code = match.group(2)
        lines = code.split('\n')

        # If code fits in max_lines, return as-is
        if len(lines) <= max_lines:
            return match.group(0)

        # Split into chunks
        chunks = []
        for i in range(0, len(lines), max_lines):
            chunk_lines = lines[i:i+max_lines]

            # Add continuation markers
            if i > 0:
                chunk_lines.insert(0, '// ...continued from previous slide')
            if i + max_lines < len(lines):
                chunk_lines.append('// ...continues on next slide')

            chunk = '\n'.join(chunk_lines)
            chunks.append(f'```{language}\n{chunk}\n```')

        # Join chunks with separator
        return '\n\n**[Code continues across slides]**\n\n'.join(chunks)

    # Replace all code blocks
    result = re.sub(code_block_pattern, split_code_block, markdown_text, flags=re.DOTALL)
    return result

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

def measure_actual_content_height(content_html, css, driver, section_name, topic_name):
    """
    Measure ACTUAL rendered height of content using real browser.
    Returns height in pixels.
    """
    # Modify CSS to let concept-body expand naturally for measurement
    css_for_measurement = css.replace(
        '/* Let concept-body take available space and show content */\n    .concept-body {\n        flex: 1;                  /* Take up remaining space in flex container */\n        overflow-y: auto;         /* Show scrollbar if content exceeds available space */\n        overflow-x: hidden;\n    }',
        '.concept-body {\n        height: auto;\n        overflow: visible;\n    }'
    ).replace(
        '/* Section containers should grow to fill space - ONLY inside slide-content */\n    .slide-content .section-practice,\n    .slide-content .section-interview,\n    .slide-content .section-quick-reference {\n        flex: 1;\n        display: flex;\n        flex-direction: column;\n        overflow: hidden;\n    }',
        '/* Measurement mode: let sections expand naturally */\n    .slide-content .section-practice,\n    .slide-content .section-interview,\n    .slide-content .section-quick-reference {\n        height: auto;\n    }'
    )

    section_class = f"section-{section_name.lower().replace(' ', '-')}"

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {css_for_measurement}
</head>
<body>
    <div class="slide">
        <div class="topic-header {section_class}">
            <div class="topic-name">{topic_name}</div>
            <div class="section-name">{section_name}</div>
        </div>
        <main class="slide-content">
            <div class="{section_class}">
                <div class="concept-title">
                    <span class="icon">📌</span>
                    <span>Measuring...</span>
                </div>
                <div class="concept-body">
                    {content_html}
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

        # Get concept-title height
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

def measure_raw_html_height(html_content, driver):
    """
    Measure just the raw HTML element height without slide chrome.
    Returns height in pixels.
    """
    simple_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
        p {{ margin: 6px 0; line-height: 1.5; font-size: 18px; }}
        strong {{ color: #3b82f6; font-weight: 600; }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 12px;
            border-radius: 6px;
            margin: 8px 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }}
        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="content">{html_content}</div>
</body>
</html>"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(simple_html)
        temp_file = f.name

    try:
        driver.get(f'file://{temp_file}')
        content_div = driver.find_element(By.ID, 'content')
        height = driver.execute_script('return arguments[0].scrollHeight;', content_div)
        return height
    finally:
        os.unlink(temp_file)

def smart_split_code_block(code_html, available_height, css, driver, section_name, topic_name, prepend_header=None):
    """
    Intelligently split a code block based on ACTUAL available height.
    Returns (first_part, remainder) where first_part fits in available_height.

    Args:
        code_html: HTML code block to split
        available_height: Available vertical space in pixels
        prepend_header: Optional header HTML to prepend to FIRST part (not remainder!)
    """
    import re

    # Extract code content
    match = re.search(r'<pre><code[^>]*>(.*?)</code></pre>', code_html, re.DOTALL)
    if not match:
        return code_html, None

    code_content = match.group(1)
    lines = code_content.split('\n')

    # Binary search to find MAXIMUM split point that fits
    left, right = 1, len(lines)
    best_split = 1

    while left <= right:
        mid = (left + right) // 2

        # Test if first 'mid' lines fit
        test_lines = lines[:mid]
        test_code = '\n'.join(test_lines)
        test_html = f'<pre><code class="language-cpp">{test_code}\n// ...continues on next slide</code></pre>'

        # Measure just the raw code height (not full slide structure)
        test_height = measure_raw_html_height(test_html, driver)

        if test_height <= available_height:
            best_split = mid
            left = mid + 1  # Try to fit more lines
        else:
            right = mid - 1  # Too tall, reduce

    # If we can't fit even 1 line, return as-is
    if best_split < 1:
        return code_html, None

    # Split at best point
    first_part_lines = lines[:best_split]
    remainder_lines = lines[best_split:]

    # Check if remainder is essentially empty (only whitespace/braces/semicolons)
    # If so, TRY to fit everything in first part (but verify it actually fits!)
    remainder_code = '\n'.join(remainder_lines).strip()
    if len(remainder_code) < 10 or all(c in ' \n\t{};' for c in remainder_code):
        # Remainder is tiny - check if we can keep everything together
        print(f"         🔍 DEBUG: Remainder too small ({len(remainder_code)} chars), checking if all fits...")

        # Measure if ALL lines fit (without continuation marker)
        all_code = '\n'.join(lines)
        all_html = f'<pre><code class="language-cpp">{all_code}</code></pre>'
        all_height = measure_raw_html_height(all_html, driver)

        if all_height <= available_height:
            # All fits! Keep together
            print(f"         ✅ DEBUG: All lines fit ({all_height}px <= {available_height}px), keeping together")
            if prepend_header:
                first_part = f'{prepend_header}\n{all_html}'
            else:
                first_part = all_html
            return first_part, None
        else:
            # Doesn't fit - must split even with tiny remainder
            print(f"         ⚠️  DEBUG: All lines don't fit ({all_height}px > {available_height}px), accepting split with tiny remainder")

    # Add continuation markers
    first_part_lines.append('// ...continues on next slide')
    remainder_lines.insert(0, '// ...continued from previous slide')

    first_part_code = f'<pre><code class="language-cpp">{chr(10).join(first_part_lines)}</code></pre>'

    # Header goes with FIRST part, not remainder!
    if prepend_header:
        first_part = f'{prepend_header}\n{first_part_code}'
    else:
        first_part = first_part_code

    # Remainder has continuation marker but NO header
    remainder = f'<p><strong>[Code continues across slides]</strong></p>\n<pre><code class="language-cpp">{chr(10).join(remainder_lines)}</code></pre>'

    return first_part, remainder

def split_content_with_measurement(content_md, section_name, topic_name, css, driver):
    """
    Split content using ACTUAL browser measurement.
    If content exceeds 1020px, splits to multiple slides.
    Keeps table headers WITH their tables.
    Intelligently splits code blocks only when needed based on actual height.
    """
    MAX_HEIGHT = 1050  # Leaves 30px margin at bottom for safety

    content_html = process_markdown_to_html(content_md)

    # DON'T pre-split code! Let measurement decide if splitting is needed
    # Measure actual height FIRST
    actual_height = measure_actual_content_height(content_html, css, driver, section_name, topic_name)

    # If fits, return as single slide (even if code has 40+ lines!)
    if actual_height <= MAX_HEIGHT:
        return [content_html]

    # Content too tall - need to split intelligently
    import re

    # Parse content into logical units, keeping headers WITH their tables/code
    # Continuation markers are NOT treated as headers (allows natural code splitting)
    parts = []
    remaining = content_html

    while remaining:
        # Find next major element
        table_match = re.search(r'<table.*?</table>', remaining, re.DOTALL)
        pre_match = re.search(r'<pre.*?</pre>', remaining, re.DOTALL)

        next_table = table_match.start() if table_match else float('inf')
        next_pre = pre_match.start() if pre_match else float('inf')

        # Find next element (table or code)
        next_element = min(next_table, next_pre)

        if next_element == float('inf'):
            # No more tables or code blocks
            if remaining.strip():
                parts.append(('text', remaining))
            break

        # Get content before element
        before = remaining[:int(next_element)]

        # Check if there's a paragraph immediately before table/code (likely a header)
        # BUT: Exclude continuation markers from being treated as headers!
        last_para_match = re.search(r'<p><strong>.*?</strong></p>\s*$', before)

        if last_para_match:
            header_para = last_para_match.group(0)
            header_text = re.sub(r'<[^>]+>', '', header_para)  # Strip HTML tags to check text

            # Check if this is a continuation marker, NOT a real header
            if '[Code continues' in header_text or 'continued from previous' in header_text.lower():
                # This is a separator paragraph, NOT a header - treat as normal text
                if before.strip():
                    parts.append(('text', before))

                # Add element alone
                if next_element == next_table:
                    parts.append(('table', table_match.group(0)))
                    remaining = remaining[table_match.end():]
                else:
                    parts.append(('code', pre_match.group(0)))
                    remaining = remaining[pre_match.end():]
            else:
                # Real header - attach to element
                before_para = before[:last_para_match.start()]

                if before_para.strip():
                    parts.append(('text', before_para))

                # Add element WITH its header
                if next_element == next_table:
                    element = table_match.group(0)
                    parts.append(('table_with_header', header_para + element))
                    remaining = remaining[table_match.end():]
                else:
                    element = pre_match.group(0)
                    parts.append(('code_with_header', header_para + element))
                    remaining = remaining[pre_match.end():]
        else:
            # No header found, add content before element normally
            if before.strip():
                parts.append(('text', before))

            # Add element alone
            if next_element == next_table:
                parts.append(('table', table_match.group(0)))
                remaining = remaining[table_match.end():]
            else:
                parts.append(('code', pre_match.group(0)))
                remaining = remaining[pre_match.end():]

    # Now group parts into slides that fit
    slides = []
    current_slide = ""

    # Use index-based iteration so we can insert remainder parts
    i = 0
    while i < len(parts):
        part_type, part_content = parts[i]
        test_html = current_slide + part_content
        test_height = measure_actual_content_height(test_html, css, driver, section_name, topic_name)

        if test_height <= MAX_HEIGHT:
            # Fits
            current_slide = test_html
        else:
            # Doesn't fit - need to split
            import re

            # Check if part_content has a header attached (header + code/table unit)
            has_header_attached = part_type in ['code_with_header', 'table_with_header']

            # Check if current_slide ends with orphaned header
            orphaned_header = None
            if current_slide:
                header_at_end = re.search(r'(<p><strong>.*?</strong></p>)\s*$', current_slide)
                if header_at_end:
                    header_text = re.sub(r'<[^>]+>', '', header_at_end.group(1))
                    # Only treat as orphaned if it's NOT a continuation marker
                    if not ('[Code continues' in header_text or 'continued from previous' in header_text.lower()):
                        orphaned_header = header_at_end.group(1)
                        current_slide = current_slide[:header_at_end.start()].rstrip()

            # Greedy fill strategy:
            # ONLY applies to standalone code (NOT code_with_header or table_with_header)
            # Header + content units must stay together - don't break them apart!
            if current_slide and not has_header_attached and part_type == 'code' and re.search(r'<pre.*?</pre>', part_content, re.DOTALL):
                # Calculate remaining space on current slide
                current_height = measure_actual_content_height(current_slide, css, driver, section_name, topic_name)
                remaining_space = MAX_HEIGHT - current_height
                print(f"      🔍 DEBUG: Greedy fill check - remaining space: {remaining_space}px (part type: {part_type})")

                # Try to split code to fill remaining space (reduced threshold to 100px)
                if remaining_space > 100:  # At least 100px space for code to be worth it
                    print(f"      ✂️  DEBUG: Attempting greedy fill split (standalone code, no header)")
                    # Split standalone code (no header attached)
                    first_part, remainder = smart_split_code_block(
                        part_content, remaining_space, css, driver, section_name, topic_name
                    )

                    if remainder:
                        # Successfully split - fill current slide greedily
                        print(f"      ✅ DEBUG: Greedy split successful - filled current slide")
                        current_slide = current_slide + first_part
                        slides.append(current_slide)
                        # Add remainder as next part to process
                        parts.insert(i + 1, ('code', remainder))
                        current_slide = ""
                        i += 1
                        continue
                    else:
                        print(f"      ❌ DEBUG: Greedy split failed - code too small to split")
                else:
                    print(f"      ⏭️  DEBUG: Skipping greedy fill - not enough space ({remaining_space}px < 100px)")
            elif has_header_attached:
                print(f"      🔒 DEBUG: Preserving atomic unit - type: {part_type} (has header attached)")

            # Standard behavior: save current slide, move content to next
            if current_slide.strip():
                slides.append(current_slide)
            current_slide = ""

            # If we found an orphaned header, prepend it to part_content
            if orphaned_header:
                if not part_content.strip().startswith(orphaned_header.strip()):
                    part_content = orphaned_header + part_content

            # Check if single element is too big for a slide
            part_height = measure_actual_content_height(part_content, css, driver, section_name, topic_name)
            if part_height > MAX_HEIGHT:
                print(f"      ⚠️  DEBUG: Oversized element detected ({part_height}px > {MAX_HEIGHT}px)")
                # Single element too big - try to split if it's code
                import re
                if re.search(r'<pre.*?</pre>', part_content, re.DOTALL):
                    # It's a code block - split it intelligently!
                    # Extract header if this has one (header goes with FIRST part!)
                    header_to_prepend = None
                    code_to_split = part_content

                    if has_header_attached:
                        header_match = re.search(r'^(<p><strong>.*?</strong></p>)\s*', part_content)
                        if header_match:
                            header_to_prepend = header_match.group(1)
                            code_to_split = part_content[header_match.end():]
                            print(f"      📎 DEBUG: Extracted header for FIRST part: {header_to_prepend[:60]}...")

                    # Calculate ACTUAL available height for content (not total slide height!)
                    # Total slide: 1080px, slide chrome (topic-header + concept-title + padding): ~216px
                    # Available for content body: ~864px (conservative: use 850px for safety margin)
                    available_for_content = 850  # Conservative estimate
                    print(f"      📐 DEBUG: Using {available_for_content}px available height for content (not MAX_HEIGHT)")

                    print(f"      ✂️  DEBUG: Splitting oversized code block...")
                    first_part, remainder = smart_split_code_block(
                        code_to_split, available_for_content, css, driver, section_name, topic_name,
                        prepend_header=header_to_prepend  # Header goes with FIRST part!
                    )
                    if remainder:
                        # Successfully split
                        print(f"      ✅ DEBUG: Split successful - header on FIRST part, no header on continuation")
                        slides.append(first_part)
                        # Add remainder as next part to process
                        parts.insert(i + 1, ('code', remainder))
                        current_slide = ""
                    else:
                        # Couldn't split (very rare) - add as-is
                        slides.append(part_content)
                        current_slide = ""
                else:
                    # Not code (table?) - add as-is
                    slides.append(part_content)
                    current_slide = ""
            else:
                current_slide = part_content

        i += 1  # Move to next part

    if current_slide:
        slides.append(current_slide)

    # Filter out slides that only contain <hr/> or whitespace
    slides = [s for s in slides if s.strip() and s.strip() not in ['<hr />', '<hr/>', '<hr>']]

    return slides if slides else [content_html]

def create_improved_css():
    """CSS optimized for maximum content utilization"""
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
        display: none;  /* Hide the old header */
    }

    .topic-header {
        flex-shrink: 0;
        padding: 20px 35px 10px 35px;
    }

    /* Section-specific colors */
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

    /* Title slide styles */
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
        display: none;  /* Hide emoji */
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

    .title-points {
        list-style: none;
        padding: 0;
        margin: 0 0 30px 0;
        font-size: 20px;
        color: #475569;
    }

    .title-points li {
        margin: 12px 0;
        padding-left: 30px;
        position: relative;
    }

    .title-points li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #10b981;
        font-weight: bold;
        font-size: 22px;
    }

    .title-cta {
        font-size: 18px;
        color: #64748b;
        font-style: italic;
        margin-top: 20px;
    }

    /* Content slide styles */
    .concept-title {
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

    /* Let concept-body take available space and show content */
    .concept-body {
        flex: 1;                  /* Take up remaining space in flex container */
        overflow-y: auto;         /* Show scrollbar if content exceeds available space */
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
        font-size: 16px;          /* Increased from 10px */
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
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        font-size: 17px;          /* Increased from 13px */
    }

    .slide-content tr:nth-child(even) {
        background: #f9fafb;
    }

    .slide-content tr:hover {
        background: #eff6ff;
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

    .slide-content pre code {
        background: transparent;
        color: inherit;
        padding: 0;
    }

    .slide-content p {
        margin: 6px 0;
        line-height: 1.5;
    }

    .slide-content strong {
        color: #3b82f6;
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

        {% if slide_type != 'title' %}
        <div class="topic-header {{ section_class }}">
            <div class="topic-name">{{ full_topic_name }}</div>
            <div class="section-name">{{ section_type }}</div>
        </div>
        {% endif %}

        <main class="slide-content">
            {% if slide_type == 'title' %}
            <div class="title-slide-content">
                <div class="title-icon">{{ emoji }}</div>
                <h1 class="title-main">{{ session_name }}</h1>
                <h2 class="title-subtitle">{{ topic_name }}</h2>
                <ul class="title-points">
                    {% for point in key_points %}
                    <li>{{ point }}</li>
                    {% endfor %}
                </ul>
                <p class="title-cta">→ Swipe to learn →</p>
            </div>
            {% else %}
            <div class="{{ section_class }}">
                <div class="concept-title">
                    <span class="icon">📌</span>
                    <span>{{ concept_title }}</span>
                </div>
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

    # Collect all subsections
    subsections = []

    # Practice Tasks
    practice_tasks = topic['practice_tasks']
    for idx, item in enumerate(practice_tasks, 1):
        # Use actual JSON structure: title, description, full_content, code
        content = f"**{item['title']}**\n\n"
        if item.get('description'):
            content += f"{item['description']}\n\n"
        if item.get('full_content'):
            content += f"{item['full_content']}"
        if item.get('code'):
            content += f"\n\n```cpp\n{item['code']}\n```"

        subsections.append({
            'title': f"Q{idx}",
            'content': content,
            'section': 'Practice Tasks'
        })

    # Interview Q&A
    interview_qa = topic['interview_qa']
    for idx, item in enumerate(interview_qa, 1):
        # Use actual JSON structure: question, difficulty, category, concepts
        # Full content is already in the 'question' field as formatted markdown
        content = item['question']  # This contains the full formatted Q&A

        # Extract just the question text for the title (first line)
        question_text = content.split('\n')[0] if '\n' in content else content
        question_text = question_text.replace('**', '').replace('Q:', '').strip()

        subsections.append({
            'title': f"Q{idx}: {question_text[:50]}...",
            'content': content,
            'section': 'Interview Questions'
        })

    # Quick Reference
    quick_ref = topic['quick_reference']
    # Quick reference is a dict with 'content' and 'tables' keys
    if quick_ref and isinstance(quick_ref, dict):
        content = quick_ref.get('content', '')
        if content:
            subsections.append({
                'title': 'Cheat Sheet',
                'content': content,
                'section': 'Quick Reference'
            })

    # Key points for title
    key_points = []
    for sub in subsections[:5]:
        title = sub['title']
        if '- ' in title:
            title = title.split('- ', 1)[-1]
        elif '. ' in title and title[0].isdigit():
            title = title.split('. ', 1)[-1]
        key_points.append(title[:60])

    # Title slide
    slides.append({
        'file': f'evening_slide_{slide_num:02d}_title.html',
        'data': {
            'theme': 'practice', 'header_right': 'Evening Practice',
            'slide_num': slide_num, 'total_slides': 0,
            'title': f'Evening: {topic["topic"]}',
            'slide_type': 'title',
            'session_name': topic['topic'],  # Topic name as main title
            'topic_name': 'Practice, Interview Q&A & Quick Reference',  # Section types as subtitle
            'key_points': key_points,
            'emoji': '🌙',
            'header_icon': '🌙',
            'extra_css': create_improved_css()
        }
    })
    slide_num += 1

    # Initialize browser for height measurement
    print(f"\n   🔍 Using ACTUAL browser measurement for perfect splitting...")
    css = create_improved_css()
    driver = get_headless_browser()

    try:
        # Content slides
        for subsec_idx, subsection in enumerate(subsections, 1):
            title = subsection['title']
            content = subsection['content']
            section = subsection['section']

            # Measure and split using ACTUAL heights
            slide_htmls = split_content_with_measurement(
                content, section, topic['topic'], css, driver
            )

            print(f"   {section} - {title[:40]}...: {len(slide_htmls)} slides")

            for slide_idx, content_html in enumerate(slide_htmls, 1):
                if len(slide_htmls) == 1:
                    slide_title = title
                else:
                    slide_title = f"{title} ({slide_idx}/{len(slide_htmls)})"

                # Convert section name to CSS class
                section_class = f"section-{section.lower().replace(' ', '-')}"

                slides.append({
                    'file': f'evening_slide_{slide_num:02d}_subsec{subsec_idx}_{slide_idx}.html',
                    'data': {
                        'theme': 'practice', 'header_right': 'Evening Practice',
                        'slide_num': slide_num, 'total_slides': 0,
                        'title': f'Evening: {topic["topic"]}',
                        'slide_type': 'concept',
                        'concept_title': slide_title,
                        'content_html': content_html,
                        'header_icon': '🌙',
                        'full_topic_name': topic['topic'],  # Add topic name
                        'section_type': section,  # Add section type
                        'section_class': section_class,  # Add section CSS class
                        'extra_css': create_improved_css()
                    }
                })
                slide_num += 1
    finally:
        driver.quit()
        print(f"   ✅ Browser measurement complete")

    # Summary slide
    summary_points = [point[:70] for point in key_points[:4]]
    slides.append({
        'file': f'evening_slide_{slide_num:02d}_summary.html',
        'data': {
            'theme': 'practice', 'header_right': 'Evening Practice',
            'slide_num': slide_num, 'total_slides': slide_num,
            'title': f'Evening: {topic["topic"]}',
            'slide_type': 'title',
            'session_name': 'What You Learned',
            'topic_name': 'Key Takeaways',
            'key_points': summary_points,
            'emoji': '✅',
            'header_icon': '🌙',
            'extra_css': create_improved_css()
        }
    })

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
    if len(sys.argv) < 3:
        print("❌ Invalid arguments. Usage: python3 generate_evening_from_morning.py CHAPTER TOPIC")
        print("   Example: python3 generate_evening_from_morning.py 12 6  # Chapter 12 Topic 6")
        sys.exit(1)

    try:
        chapter_num = int(sys.argv[1])
        topic_index = int(sys.argv[2]) - 1  # Convert to 0-based index
        if chapter_num < 1 or topic_index < 0:
            print("❌ Chapter and topic numbers must be >= 1")
            sys.exit(1)
    except ValueError:
        print("❌ Invalid numbers. Usage: python3 generate_evening_from_morning.py CHAPTER TOPIC")
        print("   Example: python3 generate_evening_from_morning.py 12 6  # Chapter 12 Topic 6")
        sys.exit(1)

    topic, chapter_name = load_topic_data(chapter_num, topic_index)
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    output_base = os.path.join(os.path.dirname(__file__), 'output', f'ch{chapter_num}_topic{topic_index + 1:02d}')
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
