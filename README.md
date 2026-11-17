# agent-skills

**日常开发里反复用到的 13 个 Agent 技能：提交前复核、写 Issue、学习沉淀、任务交接等。**

Agent skills I use daily with Codex and Claude Code. Each skill is a folder with a `SKILL.md`.

## 安装

装全部，或用 `--skill` 只装一个：

```bash
npx skills add bmdy6/agent-skills
npx skills add bmdy6/agent-skills --skill pr-delivery-review
```

也可以直接把 `skills/<名字>/` 拷到 `~/.codex/skills/` 或 `~/.claude/skills/`。

## 技能

| 技能 | 用在什么时候 |
| --- | --- |
| [`challenging-decisions`](skills/challenging-decisions/SKILL.md) | 用于重大架构、共享契约、跨模块、外部集成或难逆转决策 |
| [`flutter-ui-reader`](skills/flutter-ui-reader/SKILL.md) | 用于 Android Flutter App 的界面自动化，`uiautomator dump` 读不到文字，或需要按界面文字精确定位、点击时 |
| [`learning-knowledge-workflow`](skills/learning-knowledge-workflow/SKILL.md) | 用于学习、训练、复习、暂存知识素材、批次整理、记录待学问题、整理调研或沉淀个人知识 |
| [`pr-delivery-review`](skills/pr-delivery-review/SKILL.md) | 用于 commit、push、开 PR、标记 ready 或决定合并前的独立复核 |
| [`project-director`](skills/project-director/SKILL.md) | 当任务涉及已核实的个人项目，并需要产品、网站、服务、集成、改版或多模块完整交付时使用 |
| [`project-materials`](skills/project-materials/SKILL.md) | 仅用于用户明确要求为某个项目生成结构化调研素材包（项目快照、方向、证据、manifest），供调查员判断问题真伪与优先级 |
| [`replay-pi-session-request`](skills/replay-pi-session-request/SKILL.md) | 当 PI 会话反复出现上游 400、context、quota 或结构错误，需要把真实 session JSONL 重建成 API 请求并通过前缀/消息二分定位触发变量时使用 |
| [`resolving-merge-conflicts`](skills/resolving-merge-conflicts/SKILL.md) | 用于当前 git merge 或 rebase 存在冲突时 |
| [`siltop-health`](skills/siltop-health/SKILL.md) | 用 siltop 只读检查 Apple Silicon Mac 的内存、应用占用、CPU 和热状态，适用于电脑卡顿、内存异常、后台进程累计及清理后的复查 |
| [`task-handoff`](skills/task-handoff/SKILL.md) | 仅在用户明确要求交接、接力、续接上下文或使用 task-handoff 时手动触发 |
| [`unify-ci-model-review`](skills/unify-ci-model-review/SKILL.md) | 用于同一账号下多个仓库各自维护一份模型审查 CI、出现模型/通道/密钥漂移，需要收敛成一份可复用工作流由各仓库调用时 |
| [`using-codegraph`](skills/using-codegraph/SKILL.md) | 用于跨文件调用链、跨模块影响分析或受影响测试 |
| [`writing-issues`](skills/writing-issues/SKILL.md) | 已确认要把一个具体问题写成 GitHub Issue 时使用：判断一条还是拆分、组织文档/情报/现状/trace/截图证据、把“需要确认”写成产品能判断的业务问题并给验收 |

## 说明

- 这些技能从我的个人技能库导出，写的是我自己的工作习惯，触发条件偏保守，拿去用前建议按自己的流程改。
- 部分技能会提到这里没有收录的其他技能（如 `handling-code-review`），缺了不影响单独使用。
- `learning-knowledge-workflow` 依赖 [knowledge-mcp](https://github.com/bmdy6/knowledge-mcp)。

## 许可

[MIT](LICENSE)
