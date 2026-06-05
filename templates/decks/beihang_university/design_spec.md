---
deck_id: beihang_university
kind: deck
summary: Beihang University academic reports, group meetings, thesis defenses, laboratory introductions, and aerospace research presentations.
canvas_format: ppt169
page_count: 5
primary_color: "#003B7A"
---

# Beihang University Template - Design Specification

> A privacy-safe Beihang academic presentation preset derived from sanitized master/layout assets only. It uses official-university visual cues without preserving any source report content.

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | Beihang University Academic Template |
| **Use Cases** | Group meeting reports, thesis defenses, laboratory introductions, research roadmaps, engineering project reviews |
| **Design Tone** | Academic, precise, aerospace-oriented, restrained |
| **Design Inspiration** | Beihang blue, disciplined university report layouts, flight-path geometry, aerospace engineering schematics |

### Design Features

1. **Beihang Blue Identity**: Deep blue headers and panels provide a stable academic identity.
2. **Aerospace Line Motif**: Thin orbit arcs, flight paths, and coordinate ticks reinforce aviation/aerospace context.
3. **Clean Research Hierarchy**: Large titles, compact evidence blocks, and clear footer metadata fit repeated group-meeting use.
4. **Red Precision Accent**: A small red accent is reserved for key states, warnings, progress markers, and important conclusions.

---

## II. Canvas Specification

| Property | Value |
| --- | --- |
| **Format** | Standard 16:9 |
| **Dimensions** | 1280 x 720 px |
| **viewBox** | `0 0 1280 720` |
| **Page Margins** | Left/right 64px, top/bottom 42px |
| **Content Safe Area** | x: 72-1208, y: 102-650 |

---

## III. Color Scheme

### Primary Colors

| Role | Value | Notes |
| --- | --- | --- |
| **Beihang Blue** | `#003B7A` | Main identity, title bars, chapter backgrounds |
| **Aerospace Navy** | `#0B1F3A` | Dark cover background and strong text |
| **Sky Blue** | `#2C7CC3` | Secondary panels, diagrams, soft emphasis |
| **Signal Red** | `#C8102E` | Small accent, section markers, urgent insights |
| **Cloud Gray** | `#EEF3F8` | Light page background and card surfaces |
| **White** | `#FFFFFF` | Negative space and text on dark panels |

### Text Colors

| Role | Value | Usage |
| --- | --- | --- |
| **Title Ink** | `#10233F` | Page titles on light pages |
| **Body Text** | `#24364E` | Main content |
| **Secondary Text** | `#66758A` | Captions, footers, labels |
| **Reverse Text** | `#FFFFFF` | Text on Beihang Blue / Navy |

### Gradient Scheme

```
Cover gradient: #0B1F3A -> #003B7A -> #2C7CC3
Subtle panel gradient: #FFFFFF -> #EEF3F8
Accent line: #C8102E -> #2C7CC3
```

---

## IV. Typography System

### Font Stack

**Font Stack**: `"Microsoft YaHei", "SimHei", "PingFang SC", "Arial", sans-serif`

### Font Size Hierarchy

| Level | Usage | Size | Weight | Notes |
| --- | --- | --- | --- | --- |
| H1 | Cover main title | 46px | Bold | Academic but high-impact |
| H2 | Page title | 30px | Bold | Used with top blue rule |
| H3 | Chapter title | 44px | Bold | Strong white title on blue field |
| H4 | Block heading | 21px | Bold | Evidence cards / sections |
| P | Body content | 16px | Regular | Compact academic prose |
| Data | Key number / metric | 34px | Bold | Research result emphasis |
| Caption | Figure labels / notes | 12px | Regular | Muted |
| Footer | Footer metadata | 11px | Regular | Low contrast |

---

## V. Core Visual Elements

### 1. Top Discipline Bar

Content pages use a slim blue title bar with a red tick at the left edge. This anchors each page while leaving most space for data, diagrams, or images.

### 2. Flight Path Geometry

Use thin, semi-transparent arcs and dotted paths as background structure:

```xml
<path d="M80,620 C360,470 760,470 1180,120" fill="none" stroke="#2C7CC3" stroke-opacity="0.18" stroke-width="2"/>
```

### 3. Engineering Grid

Light coordinate ticks can sit in corners or behind diagrams. Keep opacity low and never compete with content.

### 4. Research Footer

Footer format: left metadata / center separator line / right page number. Do not include personal contact details unless the user explicitly supplies public-facing text for that output deck.

---

## VI. Page Types

### 1. Cover Page (`01_cover.svg`)

**Layout Structure**:
- Full dark blue gradient background.
- Upper-left: Beihang-style text lockup placeholder.
- Center-left: Main title, subtitle, report category.
- Right side: flight path arcs and aerospace coordinate grid.
- Bottom: neutral placeholders for presenter role and date; no private defaults.

### 2. Table of Contents (`02_toc.svg`)

**Layout Structure**:
- Left vertical Beihang Blue rail with red section marker.
- Right content area with numbered agenda items.
- Background uses subtle flight path arc.

### 3. Chapter Page (`03_chapter.svg`)

**Layout Structure**:
- Full Beihang Blue background.
- Large chapter number in translucent outline.
- Chapter title centered-left.
- Thin red/sky-blue accent line.

### 4. Content Page (`04_content.svg`)

**Layout Structure**:
- Slim top title bar.
- Flexible two-column body with evidence cards and figure placeholder.
- Footer metadata area.
- Subtle grid marks in lower-right.

### 5. Ending Page (`05_ending.svg`)

**Layout Structure**:
- White-to-light-blue background.
- Center message area.
- Bottom blue band and flight arc motif.
- Generic closing text only.

---

## VII. SVG Page Roster

| File | Role | Description |
| --- | --- | --- |
| `01_cover.svg` | cover | Title slide for academic/research reports |
| `02_toc.svg` | toc | Agenda / report structure |
| `03_chapter.svg` | chapter | Section divider |
| `04_content.svg` | content | General research content page |
| `05_ending.svg` | ending | Closing / Q&A page |

---

## VIII. Native PPTX Master Assets

Sanitized master-only PPTX files are bundled under:

`templates/native_pptx/beihang/`

These files retain slide masters, layouts, themes, and template media. They intentionally remove original report slides, notes, comments, document properties, custom XML, embedded files, charts, diagrams, tags, and other content-bearing parts.
