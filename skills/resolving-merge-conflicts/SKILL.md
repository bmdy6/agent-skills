---
name: resolving-merge-conflicts
description: "【门禁/阶段必用】用于当前 git merge 或 rebase 存在冲突时；没有冲突时不使用。"
---

# 解决合并冲突（Resolving Merge Conflicts）

进行中的 git merge/rebase 冲突，按以下标准流程处理：

1. **查看当前状态**：看 git 历史和冲突文件，搞清楚 merge/rebase 进行到哪一步。

2. **找出每个冲突的主源**：深入理解每个改动为什么存在、原始意图是什么。读 commit message、查 PR、查原始 issue/任务单。

3. **逐个解决每个 hunk**：尽可能同时保留双方的意图。不兼容时，选与 merge 既定目标一致的那一方，并记下取舍。**不要发明新行为。** 永远解决冲突，绝不 `--abort`。

4. **找出项目的自动化检查并运行**——通常是类型检查、测试、格式化。修复 merge 弄坏的任何东西。

5. **完成 merge/rebase**：暂存所有改动并提交。如果是 rebase，继续 rebase 流程直到所有 commit 都 rebase 完成。
