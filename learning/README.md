# 学习工作区（本仓库非上游内容）

这是跟随《磐石·科学智能（AI for Science）实训营》课程学习时使用的本地跟踪目录，不属于上游仓库。

- [`progress.md`](progress.md)：11 讲学习进度总表 + 笔记索引。
- [`notes/`](notes/)：每讲一页笔记，已按讲次建好空模板。
- [`exercises/`](exercises/)：动手练习与复现代码。
- [`assets/`](assets/)：笔记用的截图/图片。

上游课件本身在 [`../README.md`](../README.md) 与 [`../pdf/`](../pdf/)。

## 常用操作

```bash
# 同步上游最新课件
git pull --ff-only

# 查看进度
cat learning/progress.md
```

> 本目录是否提交到 git 由你决定；若只想本地保留，把 `learning/` 加进 `.gitignore`
> （默认未忽略，可直接 commit 作为学习档案）。
