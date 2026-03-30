# LinkedIn C++ Learning Content Generator

Automated PDF carousel generator for C++ learning content covering all 88 topics across 20 chapters.

## 🎯 Current Status

**✅ PRODUCTION READY - All 88 Topics Generated**

- ✅ 88 individual morning PDFs (474MB total)
- ✅ 3 merged PDFs by chapter groups
- ✅ Multi-chapter batch generation system
- ✅ Clean, optimized codebase

---

## 🚀 Quick Start

### Generate All 88 Morning PDFs

```bash
# Generate all topics (Chapters 1-20, all 88 topics)
./generate_all_morning.sh

# Output: 88 PDFs in final_pdfs_collection/
```

### Generate Individual Topic

```bash
# Morning post for specific chapter/topic
python3 generate_morning.py

# Evening post (not yet batch-enabled)
python3 generate_evening.py
```

### Create Merged PDFs

```bash
# Create 3 grouped PDFs from 88 individual PDFs
python3 merge_pdfs_grouped.py

# Output:
# - Part1_Fundamentals_Ch01-10.pdf (131 MB, 32 topics)
# - Part2_Advanced_Ch11-17.pdf (74 MB, 30 topics)
# - Part3_Modern_Ch18-20.pdf (34 MB, 26 topics)
```

---

## 📁 Project Structure

```
linkedin_automation/
├── 📄 Core Scripts (Morning - Complete)
│   ├── generate_morning.py           # Core morning PDF generator
│   ├── generate_all_morning.sh       # Batch script (all 88 topics)
│   ├── generate_all_morning.py       # Python batch processor
│   └── merge_pdfs_grouped.py         # Create 3 merged PDFs
│
├── 📄 Core Scripts (Evening - Chapter 1 Only)
│   └── generate_evening.py           # Evening PDF generator (needs update)
│
├── 📂 Data & Output
│   ├── linkedin_json_output/         # Source JSON (20 chapters)
│   ├── final_pdfs_collection/        # 88 PDFs + 3 merged PDFs (474 MB)
│   └── topic_mapping.json            # Chapter-topic mapping
│
├── 📂 Templates
│   ├── styles.css                    # Main stylesheet
│   ├── prism.css                     # Syntax highlighting CSS
│   ├── prism.js                      # Prism library
│   └── prism-cpp.js                  # C++ language support
│
└── 📄 Documentation
    ├── README.md                     # This file
    ├── MORNING_VS_EVENING_COMPARISON.md  # Script comparison
    └── requirements.txt              # Python dependencies
```

---

## 📋 Approach Overview

### Two-Post Strategy (Morning/Evening)

**🌅 Morning Posts (Learn):**
- Theory sections with explanations
- Edge cases and common pitfalls
- Code examples with syntax highlighting
- ~25-35 slides per topic
- **Status:** ✅ All 88 topics generated

**🌙 Evening Posts (Practice):**
- Practice tasks with solutions
- Interview Q&A (Top 10 questions)
- Quick reference cheat sheets
- ~15-25 slides per topic
- **Status:** ❌ Only Chapter 1 available (needs update)

### Key Features

- ✅ Smart code splitting with binary search (morning)
- ✅ Greedy bin packing for Q&A grouping (evening)
- ✅ 850px content height validation (no overflow)
- ✅ Multi-chapter support (all 20 chapters)
- ✅ Batch generation system
- ✅ PDF merging by chapter groups
- ✅ Syntax highlighting with Prism.js
- ✅ Vector PDF output (2160×2160px, scales perfectly)

---

## 📊 Generated Content Stats

### Overall Statistics

| Metric | Count |
|--------|-------|
| **Total Topics** | 88 |
| **Total Chapters** | 20 |
| **Morning PDFs** | 88 individual + 3 merged |
| **Total Size** | 474 MB |
| **Total Pages** | ~2,970 pages |

### Content Distribution

| Group | Chapters | Topics | Pages | Size |
|-------|----------|--------|-------|------|
| **Part 1: Fundamentals** | Ch 1-10 | 32 | 1,090 | 131 MB |
| **Part 2: Advanced** | Ch 11-17 | 30 | 1,060 | 74 MB |
| **Part 3: Modern C++** | Ch 18-20 | 26 | 820 | 34 MB |

### Chapter Breakdown

- Chapter 1: OOP (7 topics)
- Chapter 2: Memory Management (1 topic)
- Chapter 3: Smart Pointers (1 topic)
- Chapter 4: References, Copying, Moving (4 topics)
- Chapter 5: Operator Overloading (1 topic)
- Chapter 6: Type System & Casting (2 topics)
- Chapter 7: Templates & Generics (2 topics)
- Chapter 8: STL Containers & Algorithms (6 topics)
- Chapter 9: C++11 Features (5 topics)
- Chapter 10: RAII & Resource Management (3 topics)
- Chapter 11: Multithreading (7 topics)
- Chapter 12: Design Patterns (8 topics)
- Chapter 13: Compile-Time Magic (1 topic)
- Chapter 14: Low-Level & Tricky (2 topics)
- Chapter 15: C++14 Features (1 topic)
- Chapter 16: C++17 Features (4 topics)
- Chapter 17: Software Architecture (7 topics)
- Chapter 18: Network Programming (6 topics)
- Chapter 19: C++20 Features (6 topics)
- Chapter 20: Advanced Implementations (14 topics)

---

## 🎨 Visual Design

### Morning Post Design
- **Color:** Blue (`#3b82f6`)
- **Icon:** 🌅 Sunrise
- **Sections:** Theory → Edge Cases → Code Examples
- **Focus:** Learning, conceptual understanding

### Evening Post Design
- **Color:** Purple (`#a855f7`)
- **Icon:** 🌙 Moon
- **Sections:** Practice Tasks → Interview Q&A → Quick Reference
- **Focus:** Practice, hands-on problem solving

### PDF Specifications
- **Dimensions:** 2160×2160 pixels (1620×1620 PDF points)
- **Format:** Vector PDF (scales perfectly)
- **Scale:** 2× for high quality
- **LinkedIn Compatible:** Yes (accepts up to 2160×2160)

---

## 🔧 Technical Details

### Morning Script Features

**Smart Code Splitting (`generate_morning.py`):**
- Binary search algorithm to find optimal split points
- Preserves atomic units (headers with their content)
- Uses 850px available height (not MAX_HEIGHT)
- Greedy fill strategy for space optimization
- Continuation markers for split code blocks

**Key Functions:**
- `load_topic_data(chapter_num, topic_index)` - Multi-chapter support
- `smart_split_code_block()` - Binary search code splitting
- `measure_actual_content_height()` - Real browser measurements
- `generate_morning_post()` - Main generation function

### Evening Script Features

**Q&A Grouping (`generate_evening.py`):**
- Greedy bin packing for multiple items per slide
- Separate question and answer slides
- Conservative grouping to prevent truncation
- Question: compact format, Answer: verbose format

**Key Functions:**
- `group_items_with_actual_measurement()` - Q&A grouping
- `estimate_grouped_height()` - Height estimation
- `create_interview_question_html()` - Question rendering
- `create_interview_answer_html()` - Answer rendering

---

## 💻 Requirements

```bash
# Python packages
pip install -r requirements.txt

# Required packages:
# - Jinja2 (HTML templating)
# - playwright (PDF generation)
# - selenium (height measurement)
# - PyPDF2 (PDF merging)
```

---

## 📖 Usage Guide

### 1. Generate All Morning PDFs

```bash
./generate_all_morning.sh
```

**What it does:**
1. Builds `topic_mapping.json` from all 20 chapters
2. Generates 88 individual PDFs
3. Saves to `final_pdfs_collection/`
4. Reports success/failure for each topic

**Time:** ~30-45 minutes for all 88 topics

### 2. Create Merged PDFs

```bash
python3 merge_pdfs_grouped.py
```

**Output:**
- `Part1_Fundamentals_Ch01-10.pdf`
- `Part2_Advanced_Ch11-17.pdf`
- `Part3_Modern_Ch18-20.pdf`

### 3. Generate Individual Topic

```bash
# Edit generate_morning.py to set chapter/topic
python3 generate_morning.py
```

---

## 🔍 Morning vs Evening Comparison

See `MORNING_VS_EVENING_COMPARISON.md` for detailed comparison:

| Feature | Morning | Evening |
|---------|---------|---------|
| **Content** | Theory + Edge Cases + Examples | Practice + Interview + Reference |
| **Algorithm** | Binary search splitting | Greedy bin packing |
| **Slides/Topic** | ~25-35 | ~15-25 |
| **Approach** | Split content within topics | Group multiple Q&A items |
| **Performance** | Slower (precise) | Faster (good enough) |

---

## 📈 Workflow Summary

### Current Workflow (Morning - Complete)

```
1. Run: ./generate_all_morning.sh
   ↓
2. Generates: 88 individual PDFs
   ↓
3. Run: python3 merge_pdfs_grouped.py
   ↓
4. Output: 3 merged PDFs by chapter groups
```

### Future: Evening PDFs (Pending)

```
1. Update generate_evening.py (add multi-chapter support)
2. Create generate_all_evening.sh
3. Generate all 88 evening PDFs
4. Create evening PDF merger
```

---

## 🎯 Next Steps

### Morning PDFs (Complete ✅)
- ✅ All 88 topics generated
- ✅ Multi-chapter batch system
- ✅ Merged PDFs created
- ✅ Production ready

### Evening PDFs (Pending ❌)
- ❌ Update `generate_evening.py` for multi-chapter support
- ❌ Create batch generation scripts
- ❌ Generate all 88 evening PDFs
- ❌ Create evening PDF merger

### LinkedIn Posting (Future)
1. Upload PDFs to LinkedIn as carousels
2. Schedule 2 posts/day (morning + evening)
3. 88-day posting schedule
4. Engagement strategy

---

## 📝 File Naming Convention

### Individual PDFs
```
ch{XX}_topic{YY}_morning.pdf

Examples:
- ch01_topic01_morning.pdf
- ch10_topic03_morning.pdf
- ch20_topic14_morning.pdf
```

### Merged PDFs
```
Part{N}_{Description}_Ch{XX}-{YY}.pdf

Examples:
- Part1_Fundamentals_Ch01-10.pdf
- Part2_Advanced_Ch11-17.pdf
- Part3_Modern_Ch18-20.pdf
```

---

## 🐛 Troubleshooting

### Issue: Overflow on slides (content cut off)

**Fix:** Adjusted `smart_split_code_block()` to use 850px available height instead of MAX_HEIGHT (1020px). The 850px accounts for slide chrome (headers, padding, etc.).

### Issue: Missing chapters

**Fix:** Updated `load_topic_data()` to accept `chapter_num` parameter and dynamically load any chapter's JSON file.

### Issue: Batch generation fails

**Fix:** Ensure `topic_mapping.json` exists. Run the shell script which generates it automatically.

---

## 📚 Documentation Files

- **README.md** (this file) - Main documentation
- **MORNING_VS_EVENING_COMPARISON.md** - Detailed script comparison
- **requirements.txt** - Python dependencies
- **topic_mapping.json** - Auto-generated chapter-topic mapping

---

## 🏁 Project History

### March 29, 2026 - Cleanup & Optimization
- Removed 9 obsolete generation scripts
- Cleaned up 6 obsolete directories (577MB freed)
- Removed 19 obsolete files
- Cleaned templates folder (52KB freed)
- Updated documentation

### March 29, 2026 - Batch Generation
- Added multi-chapter support to morning script
- Created batch generation system
- Generated all 88 morning PDFs
- Created 3 merged PDFs by chapter groups

### March 28, 2026 - Overflow Fix
- Fixed slide 7 overflow issue
- Changed from MAX_HEIGHT to 850px available height
- Binary search code splitting optimization

### March 27, 2026 - Initial Development
- Created morning and evening generators
- Implemented smart code splitting
- Added Q&A grouping algorithm

---

**Status:** ✅ Morning PDFs Complete | ⏳ Evening PDFs Pending

**Last Updated:** March 29, 2026
