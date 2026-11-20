# 个人笔记博客（`docs/`）

![展示页预览](preview.jpg)

[`index.html`](index.html) 是个人学习笔记博客首页，[`notes/`](notes/index.html) 是站内笔记页：学术纸面风格（衬线标题、暖米色纸底、赭石强调），静态 HTML/CSS/JS，无需前端构建。

首页以笔记更新为主：最近笔记、学习进度、课程来源引用。课程正文、课件图片与封面不在站内转载，只保留个人理解、必要引用和指向官方资料的链接。

## 线上地址

<https://biociao.github.io/panshi-ai4s-practice/>

已通过 GitHub Pages 发布：**Deploy from a branch**，`study` 分支 / `/docs` 目录（legacy build）。

## 本地预览

```bash
cd docs
python3 -m http.server 8765
# 首页：http://127.0.0.1:8765/
# 笔记：http://127.0.0.1:8765/notes/
```

## 笔记页生成

笔记不是手写 HTML，而是由 [`../tools/build_notes.py`](../tools/build_notes.py) 从 Markdown 生成：

```bash
python3 tools/build_notes.py
```

| 源文件 | 输出 |
| --- | --- |
| `learning/notes/task1/illustrated-notes.md` | `docs/notes/task1-illustrated.html` |
| `learning/notes/task1/README.md` | `docs/notes/task1-text.html` |
| `learning/notes/task2/illustrated-notes.md` | `docs/notes/task2-illustrated.html` |
| `learning/notes/task2/README.md` | `docs/notes/task2-text.html` |
| `courses/11-li-yuyang/README.md` | `docs/notes/11.html` |
| `learning/progress.md` | `docs/notes/progress.html` |

脚本会：

- 渲染 Markdown，生成二级/三级标题的目录（TOC）；
- 把课件截图替换成「图注 + 官方 PDF 链接」，不复制课件图片；
- 把表格包一层横向滚动容器，处理代码块与引用；
- 重写链接：站内笔记互相链接，课程 PDF 指向官方 `TashanGKD/panshi-ai4s-practice`；
- 生成笔记索引 `docs/notes/index.html` 与上一篇 / 下一篇。

依赖：`markdown`、`beautifulsoup4`。新增笔记时，在脚本顶部的 `NOTES` 列表补一项，并把对应路径加到 `PAGE_BY_SRC`；讲次状态在 `STATUS` 中同步。

## 部署到 GitHub Pages

1. 把 `docs/` 提交到 `study` 分支并 push。
2. 仓库 **Settings → Pages → Build and deployment**：Source 选 **Deploy from a branch**，Branch 选 `study`，Folder 选 `/docs`。
3. 稍等片刻，访问 `https://<用户名>.github.io/panshi-ai4s-practice/`。

## 目录结构

```
docs/
├── index.html                博客首页（最近笔记 / 进度 / 课程来源引用）
├── notes/
│   ├── index.html            笔记索引
│   ├── task1-illustrated.html
│   ├── task1-text.html
│   ├── task2-illustrated.html
│   ├── task2-text.html
│   ├── 11.html
│   └── progress.html
├── assets/
│   ├── style.css             样式（学术纸面、深浅主题、文章排版）
│   ├── app.js                交互（主题、导航、进度动画、移动端菜单）
│   └── favicon.svg
├── preview.jpg
└── .nojekyll

tools/
└── build_notes.py            Markdown → 笔记页
```

## 更新数据

首页的笔记列表与进度是静态写死的。更新 `learning/progress.md` 或新增笔记后：

1. 运行 `python3 tools/build_notes.py`，重新生成 `docs/notes/`。
2. 同步修改 `docs/index.html` 中：
   - **写作概况**：篇数、最近更新、`segbar` 与笔记列表；
   - **笔记更新**：每篇文章的日期、标题、摘要、字数、图注数与链接；
   - **学习进度**：百分比、页数、`progress-line` 的 `data-fill`、覆盖格子；
   - **页脚**：更新日期。

## 说明

- 课程内容、课件、封面与图表版权归磐石·科学智能实训营及各讲讲师所有。
- 站内不转载课件正文与图片；笔记中的「图注」只引用官方课件的标题与页码，并链接到官方 PDF。
- 笔记为个人理解，可能与官方表述有出入；以官方课件为准。
- 深色 / 浅色主题、`prefers-reduced-motion`、键盘焦点与移动端菜单均已适配。
