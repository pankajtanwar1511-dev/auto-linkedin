# AutoLinkedIn - C++ Learning Content Automation

**Automated LinkedIn carousel slide generation for C++ learning content.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Overview

AutoLinkedIn generates professional carousel slides for LinkedIn posts from structured C++ learning content. It creates two types of posts per topic:

- **Morning Post**: Theory, Edge Cases, Code Examples
- **Evening Post**: Practice Tasks, Interview Q&A, Quick Reference

Each post is a multi-slide carousel (5-12 slides) optimized for LinkedIn's format.

---

## 🎯 Features

- ✅ **Dynamic Slide Splitting** - Large content automatically split across multiple slides
- ✅ **Smart Code Handling** - Binary search algorithm for optimal code block splitting
- ✅ **Multi-Chapter Support** - Works with all 20 C++ chapters (88 topics)
- ✅ **High-Quality PDFs** - Vector text at 2160×2160px for crisp display
- ✅ **Professional Design** - Matches C++ Master Pro app styling
- ✅ **Zero Truncation** - Intelligent height measurement prevents content overflow

---

## 📂 Project Structure

```
autolinkedin/
├── scripts/                         # Core generators
│   ├── generate_morning.py          # Morning slides (Theory/Examples)
│   ├── generate_evening.py          # Evening slides (Practice/Q&A)
│   └── generate_evening_from_morning.py  # Alternative approach
│
├── data/                            # JSON source data
│   ├── linkedin_json_output/        # 20 chapter JSON files
│   └── topic_mapping.json           # Chapter/topic metadata
│
├── templates/                       # HTML/CSS slide templates
│   ├── *.html                       # Jinja2 templates
│   └── *.css                        # Styling
│
├── output/                          # Generated PDFs (gitignored)
│   └── ch{N}_topic{M}/
│       ├── morning_theory/
│       └── evening_practice/
│
├── utils/                           # Helper scripts
│   ├── generate_all_morning.sh     # Batch generation
│   ├── cleanup_and_regenerate.sh   # Cleanup utility
│   └── merge_pdfs_grouped.py       # PDF merging
│
└── docs/                            # Documentation
    ├── MORNING_VS_EVENING_COMPARISON.md
    └── SESSION_SUMMARY_2026-03-29.md
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.10 or higher
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Generate Slides

**Morning Post (Chapter 12, Topic 6):**
```bash
cd ~/autolinkedin/scripts
python3 generate_morning.py 12 6
```

**Evening Post (Chapter 12, Topic 6):**
```bash
cd ~/autolinkedin/scripts
python3 generate_evening.py 12 6
```

**Output Location:**
```
~/autolinkedin/output/ch12_topic06/
├── morning_theory/
│   └── morning_theory_complete.pdf     # Combined carousel
└── evening_practice/
    └── evening_practice_complete.pdf   # Combined carousel
```

---

## 📊 Content Coverage

| Chapter | Topics | Content |
|---------|--------|---------|
| 1-20 | 88 total | OOP, Memory, Smart Ptrs, Templates, STL, Multithreading, Design Patterns, C++11-20 features |

Each topic generates:
- **Morning**: 40-80 slides (theory + examples)
- **Evening**: 40-70 slides (practice + Q&A)
- **Total**: ~9,000 slides across all topics

---

## 🎨 Design System

### Morning Post
- **Blue theme** (Theory)
- **Orange theme** (Edge Cases)
- **Purple theme** (Code Examples)

### Evening Post
- **Purple theme** (Practice Tasks)
- **Orange theme** (Interview Q&A)
- **Teal theme** (Quick Reference)

All designs feature:
- High-contrast colors for readability
- Syntax-highlighted code blocks
- Consistent typography
- Professional gradients

---

## 🔧 Technical Details

### Key Technologies
- **Python 3.10+**
- **Jinja2** - HTML templating
- **Playwright** - High-quality PDF generation
- **Selenium** - Browser-based height measurement
- **PyPDF2** - PDF merging
- **Markdown** - Content processing

### Smart Splitting Algorithm

The system uses **actual browser measurement** to ensure perfect fitting:

1. **Measure actual height** of rendered content
2. **Binary search** to find optimal code split points
3. **Recursive splitting** for very large items
4. **Continuation markers** across split slides

Example:
```python
# Answer with 4021px height (needs ~4 slides)
Testing A1: 1 items → 4021px (OVERFLOW)
⚠️  Answer 1 is too large - splitting into parts...
✂️  Split into 4 parts
```

---

## 📈 Usage Examples

### Generate Single Topic
```bash
# Morning: Chapter 5, Topic 1
python3 scripts/generate_morning.py 5 1

# Evening: Chapter 12, Topic 6
python3 scripts/generate_evening.py 12 6
```

### Generate All Topics (Chapter 1)
```bash
cd utils
./generate_all_morning.sh
```

### Clean and Regenerate
```bash
cd utils
./cleanup_and_regenerate.sh 12 6
```

---

## 📝 Output Specifications

### File Format
- **Format**: PDF (vector graphics)
- **Resolution**: 2160×2160px @ scale=2
- **Effective DPI**: 144
- **Size**: ~30-50KB per slide

### Slide Dimensions
- **Width**: 1080px
- **Height**: 1080px (LinkedIn carousel format)
- **Max Content Height**: 1050px (30px margin)

---

## 🔍 Recent Improvements

**March 29, 2026:**
- ✅ Added multi-chapter support (all 20 chapters)
- ✅ Implemented dynamic code splitting algorithm
- ✅ Fixed infinite recursion with depth limits
- ✅ Improved large answer handling
- ✅ Added recursion protection (max depth: 10)

**Results:**
- Before: 46 slides (20 truncated answers)
- After: 66 slides (40 properly split answers)
- Improvement: +43% more slides, zero truncation

---

## 🛠️ Development

### Project Status
- ✅ **Phase 1**: Core generators complete
- ✅ **Phase 2**: Smart splitting implemented
- 🔄 **Phase 3**: LinkedIn API integration (planned)
- ⏳ **Phase 4**: Automated scheduling (planned)

### Roadmap
1. LinkedIn OAuth integration
2. Automated daily posting
3. Progress tracking system
4. Analytics dashboard

---

## 📚 Documentation

- **[MORNING_VS_EVENING_COMPARISON.md](docs/MORNING_VS_EVENING_COMPARISON.md)** - Design comparison
- **[SESSION_SUMMARY_2026-03-29.md](docs/SESSION_SUMMARY_2026-03-29.md)** - Recent updates
- **[CODE_CONTINUATION_COMPARISON.md](docs/CODE_CONTINUATION_COMPARISON.md)** - Technical details

---

## 🤝 Contributing

This is a personal automation project. Feel free to fork and adapt for your own content!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📧 Contact

For questions or suggestions, contact via LinkedIn or GitHub.

---

**Last Updated:** March 30, 2026
**Version:** 1.0
**Status:** Production Ready
