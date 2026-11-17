---
name: project-materials
description: "【素材/仅用户点名】仅用于用户明确要求为某个项目生成结构化调研素材包（项目快照、方向、证据、manifest），供调查员判断问题真伪与优先级；普通调研、单文件分析、代码实现不使用。"
disable-model-invocation: true
---

# 项目素材生成（源码解耦）

把本地任意代码仓库"解耦"成一份结构化素材包，供 Agent 调查问题、辨别真伪、排优先级时作为输入。只读扫描，不调模型、不修改项目、不创建任务。

## 何时使用

- 需要开始调查一个项目里"有什么值得处理的问题"时，先生成素材。
- 收到候选问题但缺少证据上下文时，用素材包补齐方向、文档、Git、worktree 证据。
- 作为调查 Agent（Codex）的输入起点：先读素材，再决定读哪些源码、是否复现、问题真假与优先级。

## 命令

```bash
# 从基础设施层仓库根目录执行，避免依赖本机绝对路径
REPO_ROOT=$(git rev-parse --show-toplevel)
MATERIALS_API="$REPO_ROOT/project-intelligence/src/materials-api.mjs"

# 任意项目绝对路径（通用）
node "$MATERIALS_API" \
  --cli --repo /绝对/路径/到/项目 --out /tmp/materials.json

# 配置内项目名快捷方式（见 examples.project-sources.json）
node "$MATERIALS_API" --cli --project xcc --out /tmp/materials.json

# 只取某个方向（id 或标题）
node "$MATERIALS_API" --cli --project xcc --direction 'alias:任务进度' --out /tmp/materials.json

# 不带 --out 则直接打印 JSON
```

## 输出结构

```jsonc
{
  "ok": true,
  "materials": {
    "schemaVersion": 1,
    "project": { "id": "...", "name": "...", "repo": "..." },
    "generatedAt": "...",
    "projectEvidence": { "issues": [], "pendingChecks": [], "recentChanges": [], "worktrees": [] },
    "directions": [ { "id": "...", "title": "...", "featureDocs": [], "researchRuns": [], "worktrees": [] } ],
    "manifests": [ { "directionId": "...", "manifest": { "evidence": [] } } ]
  }
}
```

## 调查流程建议

1. 运行命令生成素材到 `/tmp/`。
2. 读 `materials.projectEvidence` 与 `directions`：找出有证据的方向（文档、Git 改动、worktree、pending checks）。
3. 对每个方向读对应 `manifest.evidence`，再按路径深入源码。
4. 判断问题真伪、可复现性、优先级，输出结论（区分"已确认/初步判断/未知"）。
5. 不得直接把候选线索当成已确认 Bug；不得绕过证据直接改代码。

## 注意

- `--repo` 必须是本机存在的绝对路径；`--project` 只认配置内 id/name。
- 素材里不含源码正文与密钥；证据只含摘要。
- 该命令只读；调查阶段的修改一律放在临时 worktree，不直接改主仓库。