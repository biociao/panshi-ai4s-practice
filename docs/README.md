# 展示页与笔记站（`docs/`）

![展示页预览](preview.jpg)

[`index.html`](index.html) 是课程索引首页，[`notes/`](notes/index.html) 是站内笔记博客：学术纸面风格（衬线标题、暖米色纸底、赭石强调），静态 HTML/CSS/JS，无构建步骤，可直接用浏览器打开，也可以部署到 GitHub Pages。

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

源文件与输出：

| 源文件 | 输出 |
| --- | --- |
| `learning/notes/task1/illustrated-notes.md` | `docs/notes/task1-illustrated.html` |
| `learning/notes/task1/README.md` | `docs/notes/task1-text.html` |
| `courses/11-li-yuyang/README.md` | `docs/notes/11.html` |
| `learning/progress.md` | `docs/notes/progress.html` |

脚本会：

- 渲染 Markdown，生成二级/三级标题的目录（TOC）；
- 把笔记引用的图片压缩为 WebP，放到 `docs/assets/notes/<笔记>/`；
- 把图片转成带图注的 `figure`，表格包一层横向滚动容器；
- 重写链接：站内笔记互相链接，PDF 与其余仓库文件指回 GitHub；
- 生成笔记索引 `docs/notes/index.html` 与上一篇 / 下一篇。

依赖：`markdown`、`beautifulsoup4`、`Pillow`（当前环境已具备）。新增笔记时，在脚本顶部的 `NOTES` 列表补一项，并把对应路径加到 `PAGE_BY_SRC`；讲次状态在 `LECTURES` 中同步。

## 部署到 GitHub Pages

1. 把 `docs/` 提交到 `study` 分支并 push。
2. 仓库 **Settings → Pages → Build and deployment**：Source 选 **Deploy from a branch**，Branch 选 `study`，Folder 选 `/docs`。
3. 稍等片刻，访问 `https://<用户名>.github.io/panshi-ai4s-practice/`。

> 页面的 PDF 链接仍指向 GitHub 的 `study` 分支，避免把 103 MB 课件复制进站点；笔记正文、配图与进度已经是站内页面，随 `docs/` 一起发布。

## 目录结构

```
docs/
├── index.html                首页（课程索引 / 路线 / 进度 / 笔记入口 / 资料）
├── notes/
│   ├── index.html            笔记索引
│   ├── task1-illustrated.html
│   ├── task1-text.html
│   ├── 11.html
│   └── progress.html
├── assets/
│   ├── style.css             样式（学术纸面、深浅主题、文章排版）
│   ├── app.js                交互（主题、筛选、进度动画、移动端菜单）
│   ├── favicon.svg
│   ├── covers/01–11.webp     各讲 PDF 首页渲染的封面
│   └── notes/                笔记配图（WebP，按笔记分目录）
├── preview.jpg
└── .nojekyll

tools/
└── build_notes.py            Markdown → 笔记页 / 配图
```

## 更新数据

首页的讲次与进度是静态写死的；更新 `learning/progress.md` 后：

1. 运行 `python3 tools/build_notes.py`，重新生成 `docs/notes/`（进度页与索引会同步字数、日期）。
2. 同步修改 `docs/index.html` 中：
   - **顶部快照**：`74 / 334 页`、`2 / 11 讲`、`segbar` 与快照列表；
   - **学习路线**：四张 track 卡的讲次 / 页数 / 进度条 `data-fill`；
   - **课程目录**：每张 `.lec` 卡的状态 `badge`（`done` / `todo` / `reading`）；
   - **学习进度**：环形图 `data-ring`、分轨 `bar i[data-fill]`、统计数字；
   - **页脚**：更新日期。

## 说明

- 封面图从公开 PDF 首页以 PyMuPDF 渲染，只用于讲次识别；课件版权归原作者与讲师。
- 站内只放个人笔记与课程索引，不转载课件正文。
- 深色 / 浅色主题、`prefers-reduced-motion`、键盘焦点与移动端菜单均已适配。
