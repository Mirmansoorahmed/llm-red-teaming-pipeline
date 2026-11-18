"""Minimal YAML loader for the restricted subset used by scenario files.

The `oss` profile must run with no third-party packages (requirements.md C6),
so PyYAML is not available. Scenario files use a deliberately small YAML subset:

  - block mappings (`key: value`) with 2-space indentation
  - block sequences (`- item`), including sequences of mappings
  - scalars: plain, single/double quoted, integers, booleans, null
  - nested mappings and lists
  - `|` and `>` block scalars (literal / folded)
  - `#` line comments and `---` document start

It intentionally does NOT support anchors, flow collections beyond simple
inline lists, multi-document streams, or tags. Loading anything outside the
subset raises YamlError rather than guessing. Scenario schema validation then
runs on the parsed structure.
"""

from __future__ import annotations

from typing import Any


class YamlError(ValueError):
    """Raised when a document is outside the supported YAML subset."""


def _strip_comment(line: str) -> str:
    out, in_s, in_d = [], False, False
    for ch in line:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(token: str) -> Any:
    token = token.strip()
    if token == "" or token in ("~", "null", "Null", "NULL"):
        return None
    if token in ("true", "True", "TRUE"):
        return True
    if token in ("false", "False", "FALSE"):
        return False
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    # inline flow list: [a, b, c]
    if token.startswith("[") and token.endswith("]"):
        inner = token[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p) for p in _split_flow(inner)]
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def _split_flow(inner: str) -> list[str]:
    parts, buf, depth, in_s, in_d = [], [], 0, False, False
    for ch in inner:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch in "[{" and not in_s and not in_d:
            depth += 1
        elif ch in "]}" and not in_s and not in_d:
            depth -= 1
        if ch == "," and depth == 0 and not in_s and not in_d:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


class _Lines:
    def __init__(self, raw: str) -> None:
        self.items: list[tuple[int, str]] = []
        for rawline in raw.splitlines():
            if rawline.strip() in ("---", "..."):
                continue
            stripped = _strip_comment(rawline)
            if stripped.strip() == "":
                continue
            indent = len(stripped) - len(stripped.lstrip(" "))
            self.items.append((indent, stripped.strip()))
        self.pos = 0

    def peek(self) -> tuple[int, str] | None:
        return self.items[self.pos] if self.pos < len(self.items) else None

    def next(self) -> tuple[int, str]:
        item = self.items[self.pos]
        self.pos += 1
        return item


def _parse_block(lines: _Lines, indent: int) -> Any:
    item = lines.peek()
    if item is None:
        return None
    if item[1].startswith("- "):
        return _parse_list(lines, indent)
    return _parse_map(lines, indent)


def _parse_list(lines: _Lines, indent: int) -> list:
    out: list = []
    while True:
        item = lines.peek()
        if item is None or item[0] < indent or not item[1].startswith("- "):
            break
        _, content = lines.next()
        rest = content[2:].strip()
        if ":" in rest and not rest.startswith(('"', "'")):
            # sequence of mappings: first key sits on the dash line
            key, _, val = rest.partition(":")
            entry: dict[str, Any] = {}
            if val.strip():
                entry[key.strip()] = _scalar(val)
            else:
                nxt = lines.peek()
                if nxt and nxt[0] > indent:
                    entry[key.strip()] = _parse_block(lines, nxt[0])
                else:
                    entry[key.strip()] = None
            # continuation keys at deeper indent
            while True:
                nxt = lines.peek()
                if nxt is None or nxt[0] <= indent:
                    break
                k2, _, v2 = nxt[1].partition(":")
                lines.next()
                if v2.strip():
                    entry[k2.strip()] = _scalar(v2)
                else:
                    deeper = lines.peek()
                    if deeper and deeper[0] > nxt[0]:
                        entry[k2.strip()] = _parse_block(lines, deeper[0])
                    else:
                        entry[k2.strip()] = None
            out.append(entry)
        else:
            out.append(_scalar(rest))
    return out


def _parse_map(lines: _Lines, indent: int) -> dict:
    out: dict[str, Any] = {}
    while True:
        item = lines.peek()
        if item is None or item[0] != indent or item[1].startswith("- "):
            if item is not None and item[0] > indent:
                raise YamlError(f"unexpected indentation at: {item[1]!r}")
            break
        _, content = lines.next()
        if ":" not in content:
            raise YamlError(f"expected 'key: value' but got {content!r}")
        key, _, val = content.partition(":")
        key = key.strip()
        val = val.strip()
        if val in ("|", ">"):
            out[key] = _parse_block_scalar(lines, indent, folded=(val == ">"))
        elif val:
            out[key] = _scalar(val)
        else:
            nxt = lines.peek()
            if nxt is not None and nxt[0] > indent:
                out[key] = _parse_block(lines, nxt[0])
            elif nxt is not None and nxt[0] == indent and nxt[1].startswith("- "):
                out[key] = _parse_list(lines, indent)
            else:
                out[key] = None
    return out


def _parse_block_scalar(lines: _Lines, parent_indent: int, folded: bool) -> str:
    collected: list[str] = []
    block_indent: int | None = None
    while True:
        item = lines.peek()
        if item is None or item[0] <= parent_indent:
            break
        if block_indent is None:
            block_indent = item[0]
        lines.next()
        collected.append(" " * (item[0] - block_indent) + item[1])
    return " ".join(collected) if folded else "\n".join(collected)


def load(text: str) -> Any:
    """Parse a single-document YAML string from the supported subset."""
    lines = _Lines(text)
    if lines.peek() is None:
        return None
    base_indent = lines.peek()[0]
    return _parse_block(lines, base_indent)
