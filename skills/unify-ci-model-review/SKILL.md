---
name: unify-ci-model-review
description: "【能力/按需】用于同一账号下多个仓库各自维护一份模型审查 CI、出现模型/通道/密钥漂移，需要收敛成一份可复用工作流由各仓库调用时；只改单个仓库的审查配置不适用。"
---

# 收敛多仓库的模型审查 CI

把 N 份各自维护的模型审查 workflow 收敛成 1 份 `on: workflow_call` 实现，各仓库只留薄调用。主 Agent 可独立完成，不需要子代理。

## 什么时候用

- 同一账号（个人或组织）下多个仓库都有模型/LLM 审查 job，但模型、通道、密钥策略、门禁方式各不相同。
- 用户表达"所有 CI 的模型应该是一个""能不能统一维护、都调用"这类诉求。

## 第 0 步：数清真实仓库边界

目录名不等于仓库。先判定哪些目录其实是同一仓库的兄弟 worktree：

```bash
git -C <dir> rev-parse --git-common-dir    # 指向主仓库 .git ⇒ 同一仓库的 worktree
git -C <dir> worktree list                 # 或直接列
```

`git rev-parse --show-toplevel` 在 linked worktree 里返回它自己，**不能**用来判边界。误判会让"批量修复 N 个仓库"变成改 1 个仓库——反过来也会把 1 份实现当成 N 份，把错误结论写进 PR 描述。

读仓库真源用 `git show origin/<default>:<file>` 或 GitHub API，不看工作区文件（主工作区常停在别人的 feature 分支上）。

## 第 1 步：写中心实现

在中心仓库新增 `.github/workflows/<name>.yml`：

- `on: workflow_call`，inputs 全部给默认值（提示词路径、diff 范围、模型、`enforce_gate`），secrets 第一把 `required: true`、备用 `required: false`。
- 拆成 `review` / `publish` / `gate` 三个 job：`review` 出 `final_message` 和 `status`，`publish` 发 PR 评论（复用已有评论），`gate` 按结论放行或阻止。
- 数据边界用 input 表达：`diff_paths` 留空=全量 diff，有值=只外发这些路径。
- 多密钥回退链：每把 key 保留一次自身重试（抗网络抖动）+ 单次超时上限，全失败才报错退出。

## 第 2 步：开跨仓库访问

```bash
gh api repos/<owner>/<central>/actions/permissions/access          # 先看当前值
gh api -X PUT repos/<owner>/<central>/actions/permissions/access -f access_level=user
```

个人账号用 `user`（同账号仓库可调用）；默认 `none` 时调用直接失败。

## 第 3 步：各仓库换薄调用

```yaml
  review:
    if: github.event.pull_request.head.repo.full_name == github.repository
    uses: <owner>/<central>/.github/workflows/<name>.yml@main
    permissions: { contents: read, pull-requests: write, issues: write }
    secrets:
      KEY_1: ${{ secrets.KEY_1 }}
      KEY_2: ${{ secrets.KEY_2 }}
      KEY_3: ${{ secrets.KEY_3 }}
```

- 用**显式** secrets：`secrets: inherit` 只在同 org/enterprise 内可用，个人账号跨仓库会校验失败。
- 仓库自己的秒级格式校验留在调用方另起 job；不要塞进中心实现。
- 中心仓库自己也可以是调用方（`uses: ./.github/workflows/<name>.yml`）。
- 密钥按真源给每个调用仓库写：`printf '%s' "$value" | gh secret set NAME --repo <owner>/<repo>`，不打印明文。

## 第 4 步：同步文档与模板

模板目录、README 一起改成薄调用形态，写明：维护点分工、需要的 secret 名、开访问级别这一步、check 名会变成 `<调用方 job> / <被调 job>`。

## 第 5 步：验证

1. **本地桩测通道循环**：假端点至少覆盖截断回退、上游 4xx/5xx、未配密钥、总预算耗尽、URL 自动补后缀、请求形状；不调真模型。
2. **静态契约检查**：中心必须保留唯一输出契约；模块 prompt 只保留领域规则/专属阻塞口径，不能重新复制 `## 结论` 等模板；路径过滤要覆盖自检脚本和模块 review prompt 自身。
3. **真 PR 验证**：给真实 PR 打 `review` 标签，确认 `review / publish / gate` 链正常、评论能发出、结论可解析。改模型/effort/超时配置时必须用真实 PR 提示词测，不拿重复假 diff 估延迟。
4. 日志里记录实际通道、`finish_reason`、usage；不要打印 key 明文。

## 坑（都踩过）

- **长任务分阶段汇报进度**：跨仓改 workflow、权限、secret 可能持续很久；按仓库/阶段报已完成和下一步，不要长时间静默。
- **0 个 job / 无 check**：优先查 reusable workflow 访问级别和 `uses:` 路径，不先怀疑 YAML/密钥。
- reusable workflow 调用 job 只能放 `if / needs / permissions / secrets / with / strategy / concurrency`；不能塞 `steps`、`timeout-minutes`。个人账号跨仓不用 `secrets: inherit`，secret 要显式传。
- **单通道单 key 也要重试**：不要把 `retries` 设 0；每次尝试有独立超时，同时设整条回退链总预算，避免 `key 数 × timeout` 顶穿 job。
- **推理审查必须流式**：`stream: true`，否则长推理可能在网关 100s 左右无字节时被 524/HTTP 000 截断；需要 token 统计时同时开 `stream_options.include_usage=true`。
- **`budget_tokens` 不等于硬上限**：实际推理长度更受 `reasoning_effort` / 模型 / 通道影响。换思考模型时要一起重测 `max_tokens`、effort、超时和通道参数兼容性；目标通道至少真跑一次。
- **延迟测试必须用真实 PR 提示词**：大段重复假 diff 会严重低估思考量，不能拿来定 timeout。
- **成功判定看 `finish_reason` + 完整结构**：HTTP 200、有内容、甚至有 `## 结论` 都不够；`finish_reason=length` 必须回退/失败，日志带 usage 才能区分截断、限流和上游故障。
- **审查被截断不能静默发布**：Collect 阶段检查必备小节；不完整时告警并保留原始响应，不能拿半份审查去过 gate。
- **`run:` 块别用会破坏缩进抽取的顶格 heredoc 正文**：reusable workflow 的本地自检通常按 YAML 缩进截块，顶格 heredoc 会把抽取脚本截断；优先用 jq/独立脚本表达流式归约。
- **`workflow_dispatch` 不能直接复用 `pull_request.*` 上下文**：手动触发时 PR 对象为空，会 checkout 默认分支。没有完整的 `pr_number/base/head` 输入链路就不要开放 dispatch。
- **`needs.X.outputs.Y` 的 Y 必须和 job `outputs:` 完全一致**：拼错不会报错，只会让条件恒 false，表现成“打了标签但 job 全 skipped”。
- **gate 只拦明确失败**：不要用 `result != 'success'`，因为未运行 job 是 `skipped`；通常只对 `failure` 做阻塞。没有 diff 时应产出 `status=skipped`，不是 failed。
- **路径过滤必须覆盖强耦合测试自身**：改 `.github/scripts/**` 或模块 review prompt 时也要触发 review self-test；否则最需要保护的治理规则可以被静默改坏。
- **输出格式契约放中心实现**：调用方 prompt 只保留领域检查和模块专属阻塞口径。中心通用 P0/P1 与模块专属口径要明确“取并集、从严者胜”，否则精简 prompt 时会把该拦的规则一起删掉。
- `workflow_call` 的 number input 不要承诺“留空=关闭”；用 0 等显式哨兵值。
