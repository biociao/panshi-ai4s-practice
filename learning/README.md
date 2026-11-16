# 学习工作区（本仓库非上游内容）

跟随《磐石·科学智能（AI for Science）实训营》课程学习时的本地跟踪目录，只存在于个人 fork 的 `study` 分支，不进入上游仓库。

- [`progress.md`](progress.md)：11 讲学习进度总表 + 笔记索引。
- [`notes/`](notes/)：每讲一页笔记，已按讲次建好模板。
- [`exercises/`](exercises/)：动手练习与复现代码。
- [`assets/`](assets/)：笔记用的截图/图片。
- [`../docs/`](../docs/)：静态展示页（讲次索引、学习进度、笔记入口），线上见 [biociao.github.io/panshi-ai4s-practice](https://biociao.github.io/panshi-ai4s-practice/)。

上游课件本身在 [`../README.md`](../README.md) 与 [`../pdf/`](../pdf/)。

## 仓库布局

| remote | 地址 | 用途 |
| --- | --- | --- |
| `origin` | `https://github.com/biociao/panshi-ai4s-practice.git` | 个人 fork，推笔记到这里 |
| `upstream` | `https://github.com/TashanGKD/panshi-ai4s-practice.git` | 原课程仓库，只读同步 |

`main` 跟踪 `origin/main`（fork 主线，保持与上游一致）；学习笔记在 `study` 分支上提交。

## 常用操作

```bash
# 提交一次学习进度
git add learning && git commit -m "learn: 第 NN 讲笔记" && git push

# 同步上游最新课件（课程更新时）
git fetch upstream
git checkout main && git merge --ff-only upstream/main && git push origin main
git checkout study && git merge main      # 把新增课件带进 study

# 查看进度
cat learning/progress.md
```

> 若想用 GitHub 网页端同步，也可以在 fork 页面点 **Sync fork**，再本地 `git pull`。
