#!/usr/bin/env python3
"""Build the site's note pages from the Markdown sources.

Usage:
    python3 tools/build_notes.py

The site is a personal reading log. Course slides are not copied: each
figure becomes a short caption plus a link to the official PDF. Notes are
rendered into docs/notes/*.html and docs/notes/index.html.

Requires: markdown, beautifulsoup4.
"""

from __future__ import annotations

import html
import posixpath
import re
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path
from string import Template
from urllib.parse import quote, unquote

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NOTES_OUT = DOCS / "notes"

REPO = "https://github.com/biociao/panshi-ai4s-practice"
BRANCH = "study"
OFFICIAL = "https://github.com/TashanGKD/panshi-ai4s-practice"

PDF_FILES = {
    "01": "01_科学模型实训（一）_李文毅.pdf",
    "02": "02_科学模型实训（二）_李文毅.pdf",
    "03": "03_科研智能体实训（一）_陈希鸿.pdf",
    "04": "04_科研智能体实训（二）_刘子笑.pdf",
    "05": "05_科研智能体实训（三）_巩泽钊.pdf",
    "06": "06_智能体记忆与知识库_余宣庆.pdf",
    "07": "07_Harness实训_张健.pdf",
    "08": "08_磐石应用实训_王正帅.pdf",
    "09": "09_端到端闭环（一）_欧仕刚.pdf",
    "10": "10_端到端闭环（二）_欧仕刚.pdf",
    "11": "11_科学智能进阶_李瑀旸.pdf",
}

OFFICIAL_PDFS = {
    number: f"{OFFICIAL}/blob/main/pdf/{quote(filename)}"
    for number, filename in PDF_FILES.items()
}
OFFICIAL_PDF_BY_PATH = {
    f"pdf/{filename}": OFFICIAL_PDFS[number]
    for number, filename in PDF_FILES.items()
}

NOTES = [
    {
        "slug": "task1-illustrated",
        "src": "learning/notes/task1/illustrated-notes.md",
        "kicker": "Task 01 · 03 + 04 · 图文笔记",
        "short": "Task1 图文",
        "lecture": "03",
        "desc": "03 + 04 两讲的结构化精读：Harness 的六件事、一次文献检索的时序、ReAct 与 Workflow 的分工、Skill 的三段结构与调用机制。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task1/task1-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "task1-text",
        "src": "learning/notes/task1/README.md",
        "kicker": "Task 01 · 03 + 04 · 文字版",
        "short": "Task1 文字",
        "lecture": "03",
        "desc": "同一份笔记的文字版：表格、页码索引、速查与自测题，适合检索、复制和打印。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task1/task1-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "task2-illustrated",
        "src": "learning/notes/task2/illustrated-notes.md",
        "kicker": "Task 02 · 06 + 07 · 图文笔记",
        "short": "Task2 图文",
        "lecture": "06",
        "desc": "06 + 07 两讲的叙述式精读：RAG 的建库与检索、记忆的分层与代谢、实验记录的冲突处理，以及从论文到 AI-Ready 数据集的 Harness 与 Benchmark。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task2/task2-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "task2-text",
        "src": "learning/notes/task2/README.md",
        "kicker": "Task 02 · 06 + 07 · 文字版",
        "short": "Task2 文字",
        "lecture": "06",
        "desc": "同一份笔记的文字版：术语表、页码索引、方案横评、自测题与待办，适合检索、复制和打印。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task2/task2-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "task3-illustrated",
        "src": "learning/notes/task3/illustrated-notes.md",
        "kicker": "Task 03 · 01 + 02 + 05 · 图文笔记",
        "short": "Task3 图文",
        "lecture": "01",
        "desc": "01 + 02 + 05 三讲的叙述式精读：从一组参数（loss、梯度、划分）到一类结构（信息通路、六类数据、选型六问），再到流程里的一格（DFT 七节点与七个 AI 插入点）。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task3/task3-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "task3-text",
        "src": "learning/notes/task3/README.md",
        "kicker": "Task 03 · 01 + 02 + 05 · 文字版",
        "short": "Task3 文字",
        "lecture": "01",
        "desc": "同一份笔记的文字版：六问决策卡、数据表示说明书、插入点梯子、术语表、页码索引、24 道自测与待办。",
        "pdf": f"{REPO}/blob/{BRANCH}/{quote('learning/notes/task3/task3-illustrated-notes.pdf')}",
        "pdf_label": "笔记 PDF",
    },
    {
        "slug": "11",
        "src": "courses/11-li-yuyang/README.md",
        "kicker": "第 11 讲 · 科学智能进阶",
        "short": "第 11 讲",
        "lecture": "11",
        "desc": "29 节图文资料：领域基座模型、光变序列、SN Clock、StarWhisper 望远镜与 AI Scientist 的实验闭环。",
        "pdf": OFFICIAL_PDFS["11"],
        "pdf_label": "官方 PDF",
    },
    {
        "slug": "progress",
        "src": "learning/progress.md",
        "kicker": "课程进度",
        "short": "学习进度",
        "lecture": "",
        "desc": "11 讲的状态、页码、起止日期与笔记入口，随学习进度更新。",
        "pdf": "",
        "pdf_label": "",
    },
]

PAGE_BY_SRC = {
    "learning/notes/task1/illustrated-notes.md": "task1-illustrated.html",
    "learning/notes/task1/README.md": "task1-text.html",
    "learning/notes/task2/illustrated-notes.md": "task2-illustrated.html",
    "learning/notes/task2/README.md": "task2-text.html",
    "learning/notes/task3/illustrated-notes.md": "task3-illustrated.html",
    "learning/notes/task3/README.md": "task3-text.html",
    "learning/notes/01/README.md": "task3-illustrated.html",
    "learning/notes/02/README.md": "task3-illustrated.html",
    "learning/notes/03/README.md": "task1-illustrated.html",
    "learning/notes/04/README.md": "task1-illustrated.html",
    "learning/notes/05/README.md": "task3-illustrated.html",
    "learning/notes/06/README.md": "task2-illustrated.html",
    "learning/notes/07/README.md": "task2-illustrated.html",
    "learning/notes/11/README.md": "11.html",
    "learning/progress.md": "progress.html",
    "courses/11-li-yuyang/README.md": "11.html",
    "README.md": "../index.html#sources",
}

EMPTY_TEMPLATE = re.compile(r"^learning/notes/\d{2}/README\.md$")

STATUS = {"01": "task3", "02": "task3", "03": "task1", "04": "task1", "05": "task3", "06": "task2", "07": "task2", "11": "11"}

SITE_UPDATED = ""


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def slugify(value: str, separator: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff\-\s]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", separator, value).strip(separator)
    return value or "section"


def git_date(rel: str) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", rel],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.fromtimestamp((ROOT / rel).stat().st_mtime).strftime("%Y-%m-%d")


def cn_date(value: str) -> str:
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return f"{d.year} 年 {d.month} 月 {d.day} 日"
    except ValueError:
        return value


def github_url(rel: str, kind: str = "blob") -> str:
    return f"{REPO}/{kind}/{BRANCH}/{quote(rel, safe='/')}"


def source_url(rel: str) -> str:
    return github_url(rel, "blob")


def extract_title(text: str, fallback: str) -> tuple[str, str]:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if not match:
        return fallback, text
    return match.group(1).strip(), text[: match.start()] + text[match.end() :]


def resolve_repo_path(src_rel: str, href: str) -> str | None:
    path = unquote(href.split("#", 1)[0].split("?", 1)[0])
    if not path:
        return None
    if path.startswith("/"):
        return posixpath.normpath(path).lstrip("/")
    base = posixpath.dirname(src_rel)
    return posixpath.normpath(posixpath.join(base, path)).lstrip("/")


def figure_lecture(note: dict, src: str) -> str:
    if note["slug"] == "11":
        return "11"
    name = posixpath.basename(unquote(src))
    match = re.match(r"(\d{2})-", name)
    if match:
        return match.group(1)
    return note.get("lecture", "")


def process_figure_refs(soup: BeautifulSoup, note: dict) -> int:
    """Replace embedded course screenshots with caption + official PDF link."""
    refs = 0

    for img in list(soup.find_all("img")):
        alt = (img.get("alt") or "").strip()
        src = img.get("src") or ""
        parent = img.parent
        caption_html = alt
        following_p = None

        if (
            parent
            and parent.name == "p"
            and len(parent.find_all("img", recursive=False)) == 1
            and not parent.get_text(strip=True)
        ):
            following = parent.find_next_sibling()
            if following and following.name == "p":
                em = following.find("em")
                if em and following.get_text(strip=True) == em.get_text(strip=True):
                    caption_html = em.decode_contents()
                    following_p = following

        lecture = figure_lecture(note, src)
        url = OFFICIAL_PDFS.get(lecture, note.get("pdf", ""))

        block = soup.new_tag("div")
        block["class"] = "figure-ref"

        label = soup.new_tag("span")
        label["class"] = "ref-label"
        label.string = "图注"
        block.append(label)

        text = soup.new_tag("span")
        text["class"] = "ref-text"
        if caption_html:
            if following_p:
                text.append(BeautifulSoup(caption_html, "html.parser"))
            else:
                text.string = caption_html
        else:
            text.string = "课件图"
        block.append(text)

        if url:
            link = soup.new_tag("a", href=url, target="_blank", rel="noopener")
            link.string = f"官方课件 {lecture} ↗" if lecture else "官方课件 ↗"
            block.append(link)

        if parent and parent.name == "p":
            parent.replace_with(block)
        else:
            img.replace_with(block)

        if following_p:
            following_p.decompose()
        refs += 1

    return refs


def process_links(soup: BeautifulSoup, src_rel: str) -> None:
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        if href.startswith(("http://", "https://")):
            a["target"] = "_blank"
            a["rel"] = "noopener"
            continue

        repo_path = resolve_repo_path(src_rel, href)
        if not repo_path:
            continue

        fragment = "#" + href.split("#", 1)[1] if "#" in href else ""
        target = PAGE_BY_SRC.get(repo_path)

        if target:
            if fragment and "#" not in target:
                target += fragment
            a["href"] = target
            a.attrs.pop("target", None)
            a.attrs.pop("rel", None)
            continue

        if EMPTY_TEMPLATE.match(repo_path):
            a["href"] = "index.html#lecture-notes"
            continue

        local = ROOT / repo_path
        if repo_path in OFFICIAL_PDF_BY_PATH:
            a["href"] = OFFICIAL_PDF_BY_PATH[repo_path]
        elif repo_path == "pdf":
            a["href"] = f"{OFFICIAL}/tree/main/pdf"
        elif repo_path.endswith(".pdf") and repo_path.startswith("pdf/"):
            a["href"] = f"{OFFICIAL}/blob/main/{quote(repo_path, safe='/')}"
        elif repo_path.endswith(".pdf"):
            a["href"] = github_url(repo_path, "blob")
        elif local.is_dir():
            a["href"] = github_url(repo_path, "tree")
        elif local.exists() or repo_path.startswith(("learning/", "courses/")):
            a["href"] = github_url(repo_path, "blob")
        else:
            continue

        a["target"] = "_blank"
        a["rel"] = "noopener"


def process_tables(soup: BeautifulSoup) -> None:
    for table in soup.find_all("table"):
        if len(table.find_all("th")) >= 6:
            table["class"] = list(table.get("class", [])) + ["wide"]
        wrapper = soup.new_tag("div")
        wrapper["class"] = "table-wrap"
        table.wrap(wrapper)


def add_heading_anchors(soup: BeautifulSoup) -> None:
    for heading in soup.find_all(["h2", "h3", "h4"]):
        hid = heading.get("id")
        if not hid:
            continue
        anchor = soup.new_tag("a")
        anchor["class"] = "heading-anchor"
        anchor["href"] = f"#{hid}"
        anchor["aria-label"] = "链接到本节"
        anchor.string = "#"
        heading.append(anchor)


def build_toc(tokens: list) -> str:
    items = []
    for token in tokens:
        if token.get("level") not in (2, 3):
            continue
        children = [c for c in token.get("children", []) if c.get("level") == 3]
        sub = ""
        if children:
            sub = "<ol>" + "".join(
                f'<li><a href="#{escape(c["id"])}">{escape(c["name"])}</a></li>'
                for c in children
            ) + "</ol>"
        items.append(
            f'<li><a href="#{escape(token["id"])}">{escape(token["name"])}</a>{sub}</li>'
        )
    return "<ol>" + "".join(items) + "</ol>" if items else ""


def count_words(soup: BeautifulSoup) -> int:
    text = soup.get_text(" ", strip=True)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", text))
    return cjk + latin


SHELL = Template(
    """<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$page_title</title>
  <meta name="description" content="$description">
  <meta name="theme-color" content="#17130f">
  <meta name="author" content="biociao">
  <link rel="icon" href="$upassets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="$upassets/style.css">
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('ai4s-theme');
        var theme = saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
        document.documentElement.dataset.theme = theme;
      } catch (e) {
        document.documentElement.dataset.theme = 'dark';
      }
      document.documentElement.classList.add('js');
    })();
  </script>
</head>
<body class="$body_class">
  <a class="skip-link" href="#main">跳到正文</a>
  $nav
  <main id="main" class="article-main">
    <div class="wrap article-wrap">
      $content
    </div>
  </main>
  $footer
  <button class="to-top" type="button" data-to-top aria-label="回到页面顶部">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>
  </button>
  <script src="$upassets/app.js" defer></script>
</body>
</html>
"""
)

NAV = Template(
    """<header class="nav" id="site-nav">
    <div class="wrap nav-inner">
      <a class="brand" href="${up}index.html" aria-label="磐石 AI4S 学习笔记，回到首页">
        <svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true">
          <defs>
            <linearGradient id="brandGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#d9b28c"/><stop offset="1" stop-color="#b08463"/>
            </linearGradient>
          </defs>
          <rect width="64" height="64" rx="12" fill="#231f1a"/>
          <rect x="1" y="1" width="62" height="62" rx="11" fill="none" stroke="url(#brandGrad)" stroke-opacity=".55"/>
          <circle cx="32" cy="32" r="14.5" fill="none" stroke="url(#brandGrad)" stroke-width="2.5"/>
          <circle cx="32" cy="32" r="4" fill="#f6f1e7"/>
          <circle cx="46" cy="18" r="3.2" fill="url(#brandGrad)"/>
        </svg>
        <span class="brand-text"><strong>磐石 AI4S</strong><em>学习笔记</em></span>
      </a>

      <nav class="nav-links" id="site-menu" aria-label="页面导航">
        <a href="index.html" class="$notes_class"$notes_current>笔记</a>
        <a href="${up}index.html#progress">进度</a>
        <a href="${up}index.html#sources">课程来源</a>
        <a href="${up}index.html#resources">资料</a>
      </nav>

      <div class="nav-actions">
        <a class="repo-link" href="$repo" target="_blank" rel="noopener">GitHub<span aria-hidden="true">↗</span></a>
        <button class="icon-btn theme-btn" type="button" data-theme-toggle aria-label="切换深浅色主题">
          <svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
        </button>
        <button class="icon-btn menu-btn" type="button" data-menu-toggle aria-expanded="false" aria-controls="site-menu" aria-label="打开导航菜单">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>
  </header>"""
)

FOOTER = Template(
    """<footer class="footer">
    <div class="wrap footer-inner">
      <div class="footer-brand">
        <svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true">
          <defs>
            <linearGradient id="footGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#d9b28c"/><stop offset="1" stop-color="#b08463"/>
            </linearGradient>
          </defs>
          <rect width="64" height="64" rx="12" fill="#231f1a"/>
          <rect x="1" y="1" width="62" height="62" rx="11" fill="none" stroke="url(#footGrad)" stroke-opacity=".55"/>
          <circle cx="32" cy="32" r="14.5" fill="none" stroke="url(#footGrad)" stroke-width="2.5"/>
          <circle cx="32" cy="32" r="4" fill="#f6f1e7"/>
          <circle cx="46" cy="18" r="3.2" fill="url(#footGrad)"/>
        </svg>
        <div>
          <strong>磐石 AI4S · 学习笔记</strong>
          <span>个人学习记录与课程引用</span>
        </div>
      </div>
      <nav class="footer-links" aria-label="页脚链接">
        <a href="index.html">笔记</a>
        <a href="${up}index.html#progress">进度</a>
        <a href="${up}index.html#sources">课程来源</a>
        <a href="$repo" target="_blank" rel="noopener">GitHub</a>
      </nav>
    </div>
    <div class="wrap footer-bottom">
      <span>整理 biociao · 更新于 ${date} · 个人学习记录</span>
      <span>排版 原生 HTML / CSS · 无第三方依赖</span>
    </div>
  </footer>"""
)


def render_shell(page_title: str, description: str, content: str, body_class: str) -> str:
    nav = NAV.substitute(
        up="../",
        notes_class="active",
        notes_current=' aria-current="page"',
        repo=REPO,
    )
    footer = FOOTER.substitute(up="../", repo=REPO, date=SITE_UPDATED)
    return SHELL.substitute(
        page_title=escape(page_title),
        description=escape(description),
        body_class=body_class,
        upassets="../assets",
        nav=nav,
        content=content,
        footer=footer,
    )


def prepare_note(note: dict) -> dict:
    src_rel = note["src"]
    src_path = ROOT / src_rel
    raw = src_path.read_text(encoding="utf-8")
    title, raw = extract_title(raw, note["short"])

    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={"toc": {"slugify": slugify, "permalink": False}},
    )
    body_html = md.convert(raw)
    soup = BeautifulSoup(body_html, "html.parser")

    refs = process_figure_refs(soup, note)
    process_links(soup, src_rel)
    process_tables(soup)
    add_heading_anchors(soup)

    words = count_words(soup)
    date = git_date(src_rel)

    return {
        "slug": note["slug"],
        "title": title,
        "kicker": note["kicker"],
        "short": note["short"],
        "desc": note["desc"],
        "body": str(soup),
        "toc": build_toc(md.toc_tokens),
        "words": words,
        "minutes": max(1, round(words / 400)),
        "refs": refs,
        "date": date,
        "date_cn": cn_date(date),
        "source": source_url(src_rel),
        "pdf": note["pdf"],
        "pdf_label": note["pdf_label"],
    }


def make_article(page: dict, prev_page: dict | None, next_page: dict | None) -> str:
    crumbs = f'''<nav class="breadcrumb" aria-label="面包屑">
      <a href="../index.html">首页</a><span class="sep">/</span>
      <a href="index.html">笔记</a><span class="sep">/</span>
      <span aria-current="page">{escape(page["short"])}</span>
    </nav>'''

    meta = [f'<span>更新于 {escape(page["date_cn"])}</span>', f'<span>约 {page["words"]:,} 字</span>', f'<span>约 {page["minutes"]} 分钟</span>']
    if page["refs"]:
        meta.append(f'<span>{page["refs"]} 处图注</span>')

    head = f'''<header class="article-head">
      <p class="eyebrow">{escape(page["kicker"])}</p>
      <h1>{escape(page["title"])}</h1>
      <p class="article-meta">{"".join(meta)}</p>
      <p class="article-source">源文件：<a href="{escape(page["source"])}" target="_blank" rel="noopener">GitHub</a> · <a href="index.html">全部笔记</a></p>
    </header>'''

    callout = ""
    if page["refs"]:
        callout = (
            '<div class="article-callout article-callout--top">'
            "本文为个人学习笔记；文中「图注」指官方课件的对应页，原图与课件请以官方发布为准。"
            "本站不转载课件图片。"
            "</div>"
        )

    toc_html = page["toc"]
    toc_mobile = ""
    toc_aside = ""
    layout_class = "article-body article-body--single"
    if toc_html:
        toc_mobile = f'<details class="toc-mobile"><summary>目录</summary><nav class="toc" aria-label="本页目录">{toc_html}</nav></details>'
        toc_aside = f'<nav class="toc" aria-label="本页目录"><p class="toc-title">目录</p>{toc_html}</nav>'
        layout_class = "article-body"

    body = f'<article class="{layout_class}">{page["body"]}</article>'

    if toc_aside:
        layout = f'<div class="article-layout">{toc_aside}{body}</div>'
    else:
        layout = body

    nav_parts = []
    if prev_page:
        nav_parts.append(
            f'<a class="prev" href="{prev_page["slug"]}.html"><span class="label">上一篇</span>{escape(prev_page["short"])}</a>'
        )
    if next_page:
        nav_parts.append(
            f'<a class="next" href="{next_page["slug"]}.html"><span class="label">下一篇</span>{escape(next_page["short"])}</a>'
        )
    article_nav = '<nav class="article-nav" aria-label="笔记翻页">' + "".join(nav_parts) + "</nav>"

    content = crumbs + head + callout + toc_mobile + layout + article_nav
    body_class = "page-note note-wide" if page["slug"] == "progress" else "page-note"
    return render_shell(f'{page["title"]} · 磐石 AI4S', page["desc"], content, body_class)


def make_index(pages: list[dict], title_date: str) -> str:
    entries = []
    for page in pages:
        meta = [f'约 {page["words"]:,} 字']
        if page["refs"]:
            meta.append(f'{page["refs"]} 处图注')
        meta.append(f'更新于 {escape(page["date_cn"])}')
        if page["pdf"]:
            meta.append(
                f'<a href="{escape(page["pdf"])}" target="_blank" rel="noopener">{escape(page["pdf_label"])}</a>'
            )
        entries.append(
            f'''<article class="note-entry">
        <p class="note-entry-kicker">{escape(page["kicker"])}</p>
        <h2><a href="{page["slug"]}.html">{escape(page["title"])}</a></h2>
        <p>{escape(page["desc"])}</p>
        <p class="note-entry-meta">{" · ".join(meta)}</p>
      </article>'''
        )

    rows = []
    for number in [f"{i:02d}" for i in range(1, 12)]:
        kind = STATUS.get(number)
        if kind == "task3":
            note = '<a href="task3-illustrated.html">Task3 图文</a> · <a href="task3-text.html">文字版</a>'
        elif kind == "task1":
            note = '<a href="task1-illustrated.html">Task1 图文</a> · <a href="task1-text.html">文字版</a>'
        elif kind == "task2":
            note = '<a href="task2-illustrated.html">Task2 图文</a> · <a href="task2-text.html">文字版</a>'
        elif kind == "11":
            note = '<a href="11.html">图文资料</a>'
        else:
            note = '<span class="todo">待补</span>'
        rows.append(f"<tr><td>{number}</td><td>{note}</td></tr>")

    content = f'''<nav class="breadcrumb" aria-label="面包屑">
      <a href="../index.html">首页</a><span class="sep">/</span>
      <span aria-current="page">笔记</span>
    </nav>

    <header class="article-head">
      <p class="eyebrow">笔记索引</p>
      <h1>学习笔记</h1>
      <p class="article-lede">每讲一页，只写自己的理解，不抄原文。长文带目录与图注；源文件都在 <code>learning/notes</code>，课程内容与课件请以官方发布为准。</p>
      <p class="article-meta"><span>{len(pages)} 篇</span><span>7 讲已整理（Task1 03+04 · Task2 06+07 · Task3 01+02+05）</span><span>更新于 {escape(title_date)}</span></p>
      <p class="article-source">源目录：<a href="{REPO}/tree/{BRANCH}/learning/notes" target="_blank" rel="noopener">learning/notes</a> · <a href="../index.html">返回首页</a></p>
    </header>

    <div class="note-list">
      {"".join(entries)}
    </div>

    <div class="article-body">
      <h2 id="lecture-notes">各讲笔记状态</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>讲次</th><th>笔记</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
      <div class="article-callout">
        <strong>关于引用：</strong>笔记页由 <code>tools/build_notes.py</code> 从 Markdown 生成；文中图注只引用官方课件的标题与页码，并链接到官方 PDF，不转载课件图片。尚未动笔的讲次保留模板，不生成空页。
      </div>
    </div>'''

    return render_shell("学习笔记 · 磐石 AI4S", "磐石 AI4S 个人学习笔记索引：Task1、Task2、Task3 图文与文字笔记、第 11 讲图文资料与学习进度。", content, "page-note notes-index")


def main() -> None:
    NOTES_OUT.mkdir(parents=True, exist_ok=True)
    pages = [prepare_note(note) for note in NOTES]

    latest = max(page["date"] for page in pages)
    global SITE_UPDATED
    SITE_UPDATED = cn_date(latest)

    for index, page in enumerate(pages):
        prev_page = pages[index - 1] if index > 0 else None
        next_page = pages[index + 1] if index + 1 < len(pages) else None
        out = NOTES_OUT / f'{page["slug"]}.html'
        out.write_text(make_article(page, prev_page, next_page), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")

    (NOTES_OUT / "index.html").write_text(make_index(pages, cn_date(latest)), encoding="utf-8")
    print(f"wrote {(NOTES_OUT / 'index.html').relative_to(ROOT)}")
    print(f"{len(pages)} note pages · no course images copied")


if __name__ == "__main__":
    main()
