# 2026-11-23 技能迁移对照

这四个仓库通过 `git subtree add`（不 squash）迁入。Git 历史保留，历史 tag 不改写。

| 来源仓库 | 来源 main 最后提交 | 新路径 | 原 tag |
| --- | --- | --- | --- |
| [bmdy6/skill-design-from-sites](https://github.com/bmdy6/skill-design-from-sites) | `130334aab8b9e4e07a03a032d4504b4b1614bdcb` | [`skills/design-from-sites/`](../skills/design-from-sites/) | 无 |
| [bmdy6/skill-readme-from-code](https://github.com/bmdy6/skill-readme-from-code) | `7a9f5d7c7f7c0082bbfad70234c9f8f1c19e3cc4` | [`skills/readme-from-code/`](../skills/readme-from-code/) | `v0.3.0`, `v0.4.0`, `v0.4.1` |
| [bmdy6/skill-style-polish](https://github.com/bmdy6/skill-style-polish) | `d5d2c83aeec8ee0be882e37c0b30b62ab348e325` | [`skills/style-polish/`](../skills/style-polish/) | 无 |
| [bmdy6/skill-bot-keepalive](https://github.com/bmdy6/skill-bot-keepalive) | `285a58f79ead849489a6ff0085cb0774c0a44ce7` | [`skills/bot-keepalive/`](../skills/bot-keepalive/) | 无 |

### skill-design-from-sites：待追加到旧 release/tag 说明

已迁移到 https://github.com/bmdy6/agent-skills/tree/main/skills/design-from-sites 。后续更新在新路径维护；本版本的历史源码与 tag 保持原样。安装使用 `npx skills add bmdy6/agent-skills --skill design-from-sites`。

### skill-readme-from-code：待追加到旧 release/tag 说明

已迁移到 https://github.com/bmdy6/agent-skills/tree/main/skills/readme-from-code 。后续更新在新路径维护；本版本的历史源码与 tag 保持原样。安装使用 `npx skills add bmdy6/agent-skills --skill readme-from-code`。

原版本复现：在旧仓库选择对应 tag；该版本的文件在旧仓库根目录，不在新仓子目录。若要固定迁移后的版本，请在本 PR 合并后取合并提交 SHA，用 `npx skills add https://github.com/bmdy6/agent-skills/tree/<合并提交SHA>/skills/readme-from-code` 安装，不把旧 tag 当作新仓 tag。

### skill-style-polish：待追加到旧 release/tag 说明

已迁移到 https://github.com/bmdy6/agent-skills/tree/main/skills/style-polish 。后续更新在新路径维护；本版本的历史源码与 tag 保持原样。安装使用 `npx skills add bmdy6/agent-skills --skill style-polish`。

### skill-bot-keepalive：待追加到旧 release/tag 说明

已迁移到 https://github.com/bmdy6/agent-skills/tree/main/skills/bot-keepalive 。后续更新在新路径维护；本版本的历史源码与 tag 保持原样。安装使用 `npx skills add bmdy6/agent-skills --skill bot-keepalive`。

`skill-readme-from-code` 的现有 release：[v0.3.0](https://github.com/bmdy6/skill-readme-from-code/releases/tag/v0.3.0)、[v0.4.0](https://github.com/bmdy6/skill-readme-from-code/releases/tag/v0.4.0)、[v0.4.1](https://github.com/bmdy6/skill-readme-from-code/releases/tag/v0.4.1)。上面的迁移文案可分别追加到这三个 release 的说明；第一阶段仅提交此对照，不修改已发布 release。
