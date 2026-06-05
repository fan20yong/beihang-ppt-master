# Beihang PPT Master

`beihang-ppt-master` is a Beihang/BUAA-oriented presentation skill for Codex. It helps create academic reports, group-meeting slides, thesis-defense decks, lab introductions, and aerospace research presentations in a Beihang-style PPT workflow.

## Based On

This skill is adapted from:

<https://github.com/hugohe3/ppt-master>

The Beihang version keeps the original `ppt-master` workflow and adds Beihang/BUAA presentation templates.

## Install

Install with the Codex skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo fan20yong/beihang-ppt-master \
  --path . \
  --name beihang-ppt-master
```

Then restart Codex.

## How To Use

After installation, ask Codex to use this skill when creating a Beihang/BUAA-style presentation.

Example prompts:

```text
Use beihang-ppt-master to create a BUAA academic report PPT from this PDF.
```

```text
用 beihang-ppt-master 做一个北航风格的组会汇报 PPT。
```

```text
请用北航 PPT 模板，把这份 Markdown 生成答辩汇报。
```

The main Beihang deck template is:

```text
templates/decks/beihang_university/
```

Native PowerPoint master templates are available at:

```text
templates/native_pptx/beihang/
```
