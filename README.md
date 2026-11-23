# agent-skills

**日常开发里反复用到的 17 个 Agent 技能：提交前复核、写 Issue、学习沉淀、任务交接等。**

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
| [`design-from-sites`](skills/design-from-sites/SKILL.md) | 从参考网站提取可追溯的设计规范 |
| [`readme-from-code`](skills/readme-from-code/SKILL.md) | 读源码、验证命令并生成 README |
| [`style-polish`](skills/style-polish/SKILL.md) | 从本地会话生成口吻档案并润色 |
| [`bot-keepalive`](skills/bot-keepalive/SKILL.md) | 检查远程会话并在授权时限内保活 |

## 新迁入技能的安装

上述 `npx` 安装命令需要 Node.js/npx 和网络。

每个技能保留原仓库的脚本、测试、文档和许可证，位于 `skills/<名字>/`。

| 技能 | 安装命令 | 运行依赖 |
| --- | --- | --- |
| `design-from-sites` | `npx skills add bmdy6/agent-skills --skill design-from-sites` | Node.js 20+；在技能目录运行 `npm ci` |
| `readme-from-code` | `npx skills add bmdy6/agent-skills --skill readme-from-code` | Node.js 20+；在技能目录运行 `npm ci` |
| `style-polish` | `npx skills add bmdy6/agent-skills --skill style-polish` | Python 3.9+；仅标准库，无需 pip |
| `bot-keepalive` | `npx skills add bmdy6/agent-skills --skill bot-keepalive` | Python 3；可选 Bash/Tailscale，按技能说明配置 |

手动安装可先克隆本仓，再把对应的完整 `skills/<名字>/` 复制到 Agent 的 skills 目录。Node 技能的 `npm ci` 要在该技能目录运行，不在本仓根目录运行。

## 历史 release 与 tag

历史提交通过不 squash 的 Git subtree 保留。原仓库的 tag 和 release 仍属于原仓库；新路径、固定版本安装方法与待追加的旧 release 说明见 [迁移对照](docs/migrations-20261123.md)。本 PR 不创建 tag、不发布 release；已发布版本不变。

## 说明

- 这些技能从我的个人技能库导出，写的是我自己的工作习惯，触发条件偏保守，拿去用前建议按自己的流程改。
- 部分技能会提到这里没有收录的其他技能（如 `handling-code-review`），缺了不影响单独使用。
- `learning-knowledge-workflow` 依赖 [knowledge-mcp](https://github.com/bmdy6/knowledge-mcp)。

## 许可

[MIT](LICENSE)
