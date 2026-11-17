---
name: replay-pi-session-request
description: "【能力/按需】当 PI 会话反复出现上游 400、context、quota 或结构错误，需要把真实 session JSONL 重建成 API 请求并通过前缀/消息二分定位触发变量时使用；普通代码调试不适用。"
---

# 重放 PI 会话请求

把 PI session JSONL 重建成 OpenAI-compatible `messages`，用来区分「内容问题、上下文长度、tool_call 结构、模型路由、provider 抖动」。先复现，再缩小变量，不靠猜。

## 安全边界

- **默认只重建，不发送。** 只有显式加 `--send` 才调用 provider。
- session 里可能含用户内容、图片和工具输出。只发回**原本已经接收过该会话的 provider**；换 `--base-url` 到其他接收方前必须先得到用户明确同意。
- API key 从正式 `ai-vault` 读取；不打印 key，不把 key 放进 curl 命令参数。
- 请求 body 使用权限为 0600 的临时文件，发送结束后自动删除。需要人工检查 body 时显式用 `--dump-body <path>`。

## 最小流程

1. 找到失败 session：

```bash
grep -rl '<错误关键字>' ~/.pi/agent/sessions
```

2. 先重建到首个失败请求对应行，不发送：

```bash
PI_SESSION_JSONL=<session.jsonl> \
python3 agent-skills/skills/能力层/replay-pi-session-request/scripts/replay_session.py \
  --to <行号>
```

3. 确认消息数/字符数合理后，再显式发送：

```bash
PI_SESSION_JSONL=<session.jsonl> \
python3 agent-skills/skills/能力层/replay-pi-session-request/scripts/replay_session.py \
  --to <行号> --send
```

4. 做单变量缩小：
   - `--pick 12,13,20`：只保留指定 JSONL 行；
   - `--drop 25`：去掉某行；
   - `--replace '旧=新'`：替换字符串；
   - `--append-toolcall 'echo hi'`：追加一个最小合成 tool_call；
   - `--no-system`：排除 system；
   - `--thinking`：保留 assistant thinking 为 `reasoning_content`；
   - `--model <id>`：同一 provider 内做模型路由对照。

5. 至少重复 3 次再下结论。概率性 400/限流不能用一次成功或失败证明。

## 判断原则

- session JSONL 是 PI **收到/记录的内容**，不一定等于 provider 实际收到的原始 HTTP body；重放结果是高价值近似证据，不要写成抓包事实。
- 切前缀时保持 `tool_call` / `tool_result` 配对，否则会制造新的结构错误。
- 测“长度”时优先用短合成内容替换真实长内容，把长度与语义拆开。
- 跨模型正常、单模型稳定失败，更像模型路由/兼容问题；同 body 同 provider 概率性失败，更像上游抖动或隐式限制。

## 验收

结论至少包含：

- 可重复的触发变量；
- 最小复现命令；
- 原始错误与重放错误是否一致；
- HTTP code / trace_id（若上游返回）；
- 对照组结果与重复次数。
