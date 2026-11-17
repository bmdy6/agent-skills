#!/usr/bin/env python3
"""Rebuild a PI session request and optionally replay it to an OpenAI-compatible endpoint."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from typing import Any

DEFAULT_MODEL = "deepseek/deepseek-v4.1-flash"
DEFAULT_BASE_URL = "https://api.commandcode.ai/provider/v1/chat/completions"
DEFAULT_KEY_NAME = "COMMANDCODE_GO_API_KEY"


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", default=os.environ.get("PI_SESSION_JSONL", ""), help="PI session JSONL；默认读 PI_SESSION_JSONL")
    ap.add_argument("--from", dest="from_line", type=int, default=1, help="起始 JSONL 行（1-based）")
    ap.add_argument("--to", dest="to_line", type=int, default=None, help="结束 JSONL 行（inclusive）")
    ap.add_argument("--model", default=os.environ.get("PI_MODEL", DEFAULT_MODEL))
    ap.add_argument("--base-url", default=os.environ.get("PI_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--key-name", default=os.environ.get("PI_KEY_NAME", DEFAULT_KEY_NAME), help="ai-vault 中的 key 名")
    ap.add_argument("--timeout", type=int, default=600, help="curl 总超时秒数")
    ap.add_argument("--no-system", action="store_true")
    ap.add_argument("--thinking", action="store_true", help="把 thinking 映射为 reasoning_content")
    ap.add_argument("--pick", help="只保留指定 JSONL 行，例如 12,13,20")
    ap.add_argument("--drop", type=int, action="append", default=[], help="排除 JSONL 行；可重复")
    ap.add_argument("--replace", action="append", default=[], metavar="OLD=NEW", help="序列化后替换字符串；可重复")
    ap.add_argument("--append-toolcall", metavar="COMMAND", help="追加最小 bash tool_call + tool_result")
    ap.add_argument("--dump-body", type=Path, help="显式把重建 body 写到指定路径（可能含敏感内容）")
    ap.add_argument("--send", action="store_true", help="真正发送；默认仅重建并输出统计")
    return ap


def text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        str(block.get("text", ""))
        for block in content
        if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
    )


def selected_lines(args: argparse.Namespace, total: int) -> list[int]:
    if args.pick:
        lines = [int(part.strip()) for part in args.pick.split(",") if part.strip()]
    else:
        hi = args.to_line or total
        lines = list(range(args.from_line, hi + 1))
    dropped = set(args.drop)
    lines = [n for n in lines if n not in dropped]
    bad = [n for n in lines if n < 1 or n > total]
    if bad:
        raise ValueError(f"JSONL 行号越界：{bad[:5]}（总行数 {total}）")
    return lines


def rebuild_messages(rows: list[dict[str, Any]], lines: list[int], *, include_system: bool, include_thinking: bool) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for n in lines:
        row = rows[n - 1]
        if row.get("type") != "message" or not isinstance(row.get("message"), dict):
            continue
        msg = row["message"]
        if msg.get("stopReason") == "error":
            continue
        role = msg.get("role")
        content = msg.get("content")

        if role == "system":
            if include_system:
                messages.append({"role": "system", "content": text_of(content)})
            continue

        if role == "user":
            if isinstance(content, str):
                messages.append({"role": "user", "content": content})
                continue
            parts: list[dict[str, Any]] = []
            for block in content or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and block.get("text"):
                    parts.append({"type": "text", "text": block["text"]})
                elif block.get("type") == "image" and block.get("data") and block.get("mimeType"):
                    parts.append({"type": "image_url", "image_url": {"url": f"data:{block['mimeType']};base64,{block['data']}"}})
            if parts:
                messages.append({"role": "user", "content": parts})
            continue

        if role == "assistant":
            out: dict[str, Any] = {"role": "assistant", "content": text_of(content)}
            blocks = content if isinstance(content, list) else []
            if include_thinking:
                thinking = "\n".join(
                    str(block.get("thinking", ""))
                    for block in blocks
                    if isinstance(block, dict) and block.get("type") == "thinking" and block.get("thinking")
                )
                if thinking:
                    out["reasoning_content"] = thinking
            calls = [block for block in blocks if isinstance(block, dict) and block.get("type") == "toolCall"]
            if calls:
                out["tool_calls"] = [
                    {
                        "id": call["id"],
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": json.dumps(call.get("arguments", {}), ensure_ascii=False),
                        },
                    }
                    for call in calls
                ]
            if out["content"] or calls:
                messages.append(out)
            continue

        if role == "toolResult":
            blocks = content if isinstance(content, list) else []
            body = content if isinstance(content, str) else text_of(blocks)
            messages.append({"role": "tool", "content": body or "(no tool output)", "tool_call_id": msg.get("toolCallId")})
            for block in blocks:
                if isinstance(block, dict) and block.get("type") == "image" and block.get("data") and block.get("mimeType"):
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Attached image(s) from tool result:"},
                            {"type": "image_url", "image_url": {"url": f"data:{block['mimeType']};base64,{block['data']}"}},
                        ],
                    })
    return messages


def append_synthetic_toolcall(messages: list[dict[str, Any]], command: str) -> None:
    tool_id = "call_00_replay_synthetic"
    messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": [{
            "id": tool_id,
            "type": "function",
            "function": {"name": "bash", "arguments": json.dumps({"command": command}, ensure_ascii=False)},
        }],
    })
    messages.append({"role": "tool", "content": "ok", "tool_call_id": tool_id})


def apply_replacements(raw: str, replacements: list[str]) -> str:
    for expr in replacements:
        if "=" not in expr:
            raise ValueError(f"--replace 必须是 OLD=NEW：{expr!r}")
        old, new = expr.split("=", 1)
        hits = raw.count(old)
        raw = raw.replace(old, new)
        print(f"[replay] replace {old!r} -> {new!r}: {hits} hit(s)")
    return raw


def vault_script() -> Path:
    # .../能力层/replay-pi-session-request/scripts/replay_session.py -> .../能力层/ai-vault/scripts/vault.py
    return Path(__file__).resolve().parents[2] / "ai-vault" / "scripts" / "vault.py"


def read_key(key_name: str) -> str:
    script = vault_script()
    cp = subprocess.run([sys.executable, str(script), "get", key_name], capture_output=True, text=True, check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise RuntimeError(cp.stderr.strip() or f"ai-vault 无法读取 key：{key_name}")
    return cp.stdout.strip()


def send_request(raw: str, *, base_url: str, key_name: str, timeout: int) -> tuple[str, str]:
    key = read_key(key_name)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", prefix="pi-replay-", delete=False) as fp:
            fp.write(raw)
            tmp_path = Path(fp.name)
        os.chmod(tmp_path, 0o600)
        # Header 从 stdin 读取，避免把 key 放进可被 ps 看到的 argv。
        headers = f"Authorization: Bearer {key}\nContent-Type: application/json\n"
        cp = subprocess.run(
            ["curl", "-sS", "-m", str(timeout), "-w", "\n%{http_code}", base_url,
             "-H", "@-", "--data-binary", f"@{tmp_path}"],
            input=headers, capture_output=True, text=True, check=False,
        )
        if cp.returncode != 0:
            raise RuntimeError(cp.stderr.strip() or f"curl exit {cp.returncode}")
        payload, _, code = cp.stdout.rpartition("\n")
        return code, payload
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not args.session:
        raise SystemExit("缺少 session：传 --session <jsonl> 或设置 PI_SESSION_JSONL")
    session_path = Path(args.session).expanduser()
    if not session_path.is_file():
        raise SystemExit(f"session 不存在：{session_path}")

    rows = [json.loads(line) for line in session_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    lines = selected_lines(args, len(rows))
    messages = rebuild_messages(rows, lines, include_system=not args.no_system, include_thinking=args.thinking)
    if args.append_toolcall is not None:
        append_synthetic_toolcall(messages, args.append_toolcall)

    body = {"model": args.model, "max_tokens": 16, "messages": messages}
    raw = apply_replacements(json.dumps(body, ensure_ascii=False), args.replace)
    first = min(lines) if lines else None
    last = max(lines) if lines else None
    print(f"[replay] lines={first}-{last} messages={len(messages)} chars={len(raw)} (~{len(raw) // 3} tok) model={args.model}")

    if args.dump_body:
        target = args.dump_body.expanduser()
        target.write_text(raw, encoding="utf-8")
        os.chmod(target, 0o600)
        print(f"[replay] body written: {target} (0600)")

    if not args.send:
        print("[replay] dry by default; add --send to call the provider")
        return 0

    code, payload = send_request(raw, base_url=args.base_url, key_name=args.key_name, timeout=args.timeout)
    print(f"[replay] HTTP {code}: {payload[:400]}")
    return 0 if code.startswith("2") else 1


if __name__ == "__main__":
    raise SystemExit(main())
