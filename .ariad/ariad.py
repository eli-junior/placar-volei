"""Ariad sidecar orchestrator.

Install by extracting the sidecar zip at the project root, then run:
    python .ariad/ariad.py init [--dry-run]
    python .ariad/ariad.py setup
    python .ariad/ariad.py run [--story CODE] [--max N] [--dry-run]
    python .ariad/ariad.py status
    python .ariad/ariad.py agents
    python .ariad/ariad.py check [AGENT ...] [--timeout S]
    python .ariad/ariad.py export [--out FILE.zip]

Standard library only; Python 3.11+.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import unicodedata
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.2.0"
SCRIPT_DIR = Path(__file__).resolve().parent
OK, ERROR, STOPPED = 0, 1, 2

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


class Stop(Exception):
    """Ends the command with a pt-BR message and an exit code."""

    def __init__(self, message: str, code: int = ERROR):
        super().__init__(message)
        self.code = code


# ==== Paths and text ====

def project_root() -> Path:
    """The project root is the parent of `.ariad/`; commands that touch a project need it."""
    if SCRIPT_DIR.name != ".ariad":
        raise Stop("Rode a partir de .ariad/ dentro do projeto: gere o zip com `export` e extraia na raiz do projeto.")
    return SCRIPT_DIR.parent


def templates_dir() -> Path:
    for candidate in (SCRIPT_DIR / "templates", SCRIPT_DIR.parent / "templates",
                      SCRIPT_DIR.parent / "docs" / "project-templates"):
        if candidate.is_dir():
            return candidate
    raise Stop("Templates não encontrados (.ariad/templates ou templates).")


def template_files(src: Path) -> list[Path]:
    """Template files relative to `src`, without the site page `index.md` at its top level."""
    return sorted(p.relative_to(src) for p in src.rglob("*")
                  if p.is_file() and p.relative_to(src).as_posix() != "index.md"
                  and "__pycache__" not in p.parts)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def slug(text: str, limit: int = 48) -> str:
    base = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:limit].strip("-") or "item"


def to_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except ValueError:
        return default


def today() -> str:
    return dt.date.today().isoformat()


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%MZ")


def local_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


# ==== Terminal ====

def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        raise Stop("Entrada encerrada sem resposta. Rode de novo no terminal.", STOPPED)


def ask_text(label: str) -> str:
    """Reads lines until an empty line and returns them joined."""
    print(f"  {label} (linha vazia termina):")
    lines = []
    while line := ask("  › "):
        lines.append(line)
    return "\n".join(lines)


def menu(letters: str) -> str:
    while True:
        answer = ask("  > ").lower()[:1]
        if answer and answer in letters:
            return answer
        print(f"  Escolha uma opção: {', '.join(letters)}")


def banner(text: str) -> None:
    width = min(shutil.get_terminal_size((88, 24)).columns - 4, 100)
    color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    title = f"\033[1;36m{text}\033[0m" if color else text
    print(f"\n╭{'─' * max(20, width)}\n│ {title}\n╰{'─' * max(20, width)}")


def render_answer(step: str, label: str, answer: dict) -> None:
    """Render structured answers in Python; raw protocol output stays in the log."""
    import textwrap
    banner(f"{step} · {label}")
    labels = {"summary": "Resumo", "scope": "Escopo", "approach": "Plano", "risks": "Riscos",
              "changed_files": "Arquivos alterados", "tests": "Testes", "verdict": "Parecer",
              "findings": "Achados", "validation_route": "Como validar", "commit_message": "Commit"}
    width = max(30, min(100, shutil.get_terminal_size((88, 24)).columns - 6))
    for key, title in labels.items():
        value = answer.get(key)
        if not value:
            continue
        print(f"  {title}")
        values = value if isinstance(value, list) else [value]
        for item in values:
            content = (" · ".join(f"{k}: {v}" for k, v in item.items() if v not in (None, "", []))
                       if isinstance(item, dict) else str(item))
            print(textwrap.fill(content, width=width, initial_indent="    • ", subsequent_indent="      "))


# ==== State ====

def state_path(root: Path) -> Path:
    return root / ".ariad" / "state.json"


def load_state(root: Path) -> dict:
    path = state_path(root)
    if not path.is_file():
        return {}
    try:
        return json.loads(read(path))
    except ValueError:
        raise Stop(f"{path} corrompido; apague-o para recomeçar a história atual do zero.")


def save_state(root: Path, state: dict) -> None:
    write(state_path(root), json.dumps(state, ensure_ascii=False, indent=2))


class Lock:
    """Only one orchestrator per project."""

    def __init__(self, root: Path):
        self.path = root / ".ariad" / ".lock"

    def __enter__(self) -> "Lock":
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise Stop(f"Outro ariad parece ativo neste projeto ({self.path}). Se não houver, apague o arquivo.")
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return self

    def __exit__(self, *exc) -> None:
        self.path.unlink(missing_ok=True)


# ==== Frontmatter and sections ====

FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*)$")


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Returns (frontmatter lines, body); text without frontmatter gives ([], text)."""
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 3)
    if end == -1:
        return [], text
    return text[4:end].split("\n"), text[end + 5:]


def parse_frontmatter(text: str) -> dict[str, str]:
    lines, _ = split_frontmatter(text)
    return {m.group(1): m.group(2).strip() for m in map(FM_LINE.match, lines) if m}


def set_frontmatter(text: str, updates: dict) -> str:
    """Updates keys in place, appends missing keys, keeps every other line and the body."""
    lines, body = split_frontmatter(text)
    pending = {k: "" if v is None else str(v) for k, v in updates.items()}
    out = []
    for line in lines:
        m = FM_LINE.match(line)
        if m and m.group(1) in pending:
            out.append(f"{m.group(1)}: {pending.pop(m.group(1))}".rstrip())
        else:
            out.append(line)
    out += [f"{k}: {v}".rstrip() for k, v in pending.items()]
    return "---\n" + "\n".join(line for line in out if line.strip()) + "\n---\n" + body


def set_section(text: str, name: str, content: str) -> str:
    """Replaces the body of `## name` up to the next `## ` heading, or appends the section."""
    block = f"## {name}\n\n{content.strip()}\n"
    pattern = re.compile(rf"^## {re.escape(name)}[ \t]*\n.*?(?=^## |\Z)", re.M | re.S)
    if pattern.search(text):
        return pattern.sub(lambda _: block + "\n", text, count=1).rstrip("\n") + "\n"
    return text.rstrip("\n") + "\n\n" + block


def title_of(text: str) -> str:
    m = re.search(r"^# (.+)$", split_frontmatter(text)[1], re.M)
    return m.group(1).strip() if m else ""


# ==== Roadmap ====

ROADMAP = Path("docs/project/roadmap")
CODE_RE = re.compile(r"^CV\d+(\.DS\d+(\.(US|TS)\d+)?)?$")
LEVEL_BY_KIND = {"CV": "Value", "DS": "Delivery Story", "US": "User Story", "TS": "Technical Story"}
STORY_LEVELS = ("User Story", "Technical Story")
PARENT_STOPS = ("Blocked", "Deferred", "Dropped")


@dataclass
class Item:
    code: str
    level: str
    status: str
    title: str
    path: Path
    effort: int = 0
    effort_reason: str = ""
    order: int = 0
    writer: str = ""

    @property
    def is_story(self) -> bool:
        return self.level in STORY_LEVELS


def level_for(code: str) -> str:
    return LEVEL_BY_KIND[code.split(".")[-1][:2]]


def parent_code(code: str) -> str:
    return code.rsplit(".", 1)[0] if "." in code else ""


def code_key(code: str) -> tuple:
    return tuple((part[:2], to_int(part[2:])) for part in code.split("."))


def load_roadmap(root: Path) -> list[Item]:
    base = root / ROADMAP
    items = []
    for path in (sorted(base.rglob("index.md")) if base.is_dir() else []):
        if path.parent == base:
            continue
        text = read(path)
        fm = parse_frontmatter(text)
        code = fm.get("code", "")
        if not CODE_RE.match(code):
            continue
        items.append(Item(code=code, level=fm.get("level") or level_for(code),
                          status=fm.get("status") or "Planned", title=title_of(text) or code,
                          path=path.relative_to(root), effort=to_int(fm.get("effort", "")),
                          effort_reason=fm.get("effort_reason", ""), order=to_int(fm.get("order", "")),
                          writer=fm.get("writer", "")))
    return sorted(items, key=lambda i: code_key(i.code))


def children(items: list[Item], code: str) -> list[Item]:
    return [i for i in items if parent_code(i.code) == code]


def next_story(items: list[Item], only: str | None = None) -> Item | None:
    """Active before Planned, then `order`, then code; skips stories under a stopped parent."""
    by_code = {i.code: i for i in items}

    def open_parents(item: Item) -> bool:
        code = parent_code(item.code)
        while code:
            if code in by_code and by_code[code].status in PARENT_STOPS:
                return False
            code = parent_code(code)
        return True

    ready = [i for i in items if i.is_story and i.status in ("Active", "Planned") and open_parents(i)]
    if only:
        ready = [i for i in ready if i.code == only]
    ready.sort(key=lambda i: (i.status != "Active", i.order or 10 ** 6, code_key(i.code)))
    return ready[0] if ready else None


def cmd_status(args) -> int:
    root = project_root()
    items = load_roadmap(root)
    if not items:
        print("Roadmap vazio. Rode `python .ariad/ariad.py setup`.")
        return OK
    short = {"Value": "CV", "Delivery Story": "DS", "User Story": "US", "Technical Story": "TS"}
    rows = [("código", "nível", "status", "esforço", "escritor", "título")]
    rows += [(i.code, short.get(i.level, i.level), i.status, str(i.effort or ""), i.writer, i.title) for i in items]
    widths = [max(len(r[c]) for r in rows) for c in range(5)]
    for r in rows:
        print("  " + "  ".join(v.ljust(w) for v, w in zip(r, widths)) + "  " + r[5])
    state = load_state(root)
    if state.get("story"):
        print(f"\n  Ativa: {state['story']} · fase {state['phase']} · escritor {state.get('writer', '?')}"
              f" · rodada {state.get('round', 0)}")
    return OK


# ==== Config ====

DEFAULTS = {
    "project": {"language": "en", "verify": [], "plan_checkpoint_from": 4, "max_fix_rounds": 2,
                "timeout_minutes": 45, "diff_limit_kb": 60, "min_available": 10},
    "roles": {"brain": "claude", "brain_effort": 8, "writer": "claude", "reviewers": [],
              "reviewers_by_effort": {"1": 1}},
}


def load_config(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            cfg = tomllib.load(fh)
    except FileNotFoundError:
        raise Stop(f"Config não encontrada: {path}")
    except tomllib.TOMLDecodeError as e:
        raise Stop(f"{path.name} inválido: {e}")
    for section, values in DEFAULTS.items():
        cfg.setdefault(section, {})
        for key, value in values.items():
            cfg[section].setdefault(key, value)
    agents = cfg.get("agents") or {}
    if not agents:
        raise Stop(f"{path.name} sem [agents].")
    for name, agent in agents.items():
        for key in ("exe", "write", "read", "bands"):
            if key not in agent:
                raise Stop(f"Agente '{name}' sem '{key}' em {path.name}.")
        for band in agent["bands"]:
            if not {"from", "to", "args"} <= band.keys():
                raise Stop(f"Agente '{name}': cada faixa precisa de from, to e args.")
    for role in ("brain", "writer"):
        if cfg["roles"][role] not in agents:
            raise Stop(f"[roles].{role} aponta para agente inexistente: {cfg['roles'][role]}")
    return cfg


def band_for(agent: dict, effort: int) -> dict:
    effort = max(1, min(10, effort))
    for band in agent["bands"]:
        if band["from"] <= effort <= band["to"]:
            return band
    return min(agent["bands"], key=lambda b: min(abs(b["from"] - effort), abs(b["to"] - effort)))


def band_label(band: dict) -> str:
    return band.get("model") or " ".join(band["args"]) or "padrão"


def agent_label(cfg: dict, name: str, effort: int) -> str:
    return f"{name}({band_label(band_for(cfg['agents'][name], effort))})"


def reviewer_count(cfg: dict, effort: int) -> int:
    table = {int(k): int(v) for k, v in cfg["roles"]["reviewers_by_effort"].items()}
    keys = [k for k in table if k <= effort]
    return table[max(keys)] if keys else 0


def pick_reviewers(candidates: list[str], writer: str, count: int) -> list[str]:
    return [name for name in candidates if name != writer][:count]


def needs_plan_stop(cfg: dict, effort: int, suggested: int = 0) -> bool:
    return max(effort, suggested) >= cfg["project"]["plan_checkpoint_from"]


def toml_with(text: str, section: str, key: str, value: object) -> str:
    """Sets `key = value` inside [section]; value is a string, an int, or a list of strings."""
    lines = text.split("\n")
    literal = json.dumps(value, ensure_ascii=False)
    current, section_end = None, None
    for n, line in enumerate(lines):
        header = re.match(r"^\s*\[\[?\s*([^\[\]]+?)\s*\]\]?\s*(#.*)?$", line)
        if header:
            if current == section and section_end is None:
                section_end = n
            current = header.group(1)
            continue
        if current == section and re.match(rf"^\s*{re.escape(key)}\s*=", line):
            comment = re.search(r"\s+#[^\"\]]*$", line)
            lines[n] = f"{key} = {literal}" + (comment.group(0) if comment else "")
            return "\n".join(lines)
    if current == section and section_end is None:
        section_end = len(lines)
    if section_end is None:
        return text.rstrip("\n") + f"\n\n[{section}]\n{key} = {literal}\n"
    lines.insert(section_end, f"{key} = {literal}")
    return "\n".join(lines)


def set_toml_value(path: Path, section: str, key: str, value: object) -> None:
    write(path, toml_with(read(path), section, key, value))


# ==== JSON answers ====

FENCE = re.compile(r"```(?:json)?[ \t]*\n(.*?)\n```", re.S)


def _loads(text: str):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def stream_answer(text: str) -> str | None:
    """Final answer text from JSON-lines output of Claude, agy, or Copilot; None when there is none."""
    answer = None
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        event = _loads(line)
        if not isinstance(event, dict):
            continue
        if event.get("type") == "result":
            if isinstance(event.get("structured_output"), dict):
                answer = json.dumps(event["structured_output"])
            elif isinstance(event.get("result"), str):
                answer = event["result"]
        elif event.get("event") == "result" and isinstance(event.get("result"), dict):
            answer = event["result"].get("response") or answer
        elif event.get("type") == "assistant.message":
            data = event.get("data") or {}
            if data.get("phase") == "final_answer" and isinstance(data.get("content"), str):
                answer = data["content"]
    return answer


def _unwrap(obj):
    if not isinstance(obj, dict):
        return None
    if isinstance(obj.get("structured_output"), dict):
        return obj["structured_output"]
    if obj.get("type") == "result" and isinstance(obj.get("result"), str):
        return extract_json(obj["result"])
    return obj


def extract_json(text: str) -> dict | None:
    """The agent's JSON answer: stream envelope, whole text, last fenced block, or last top-level object."""
    if not text or not text.strip():
        return None
    streamed = stream_answer(text)
    if streamed is not None and streamed.strip() != text.strip():
        found = extract_json(streamed)
        if found is not None:
            return found
    whole = _unwrap(_loads(text.strip()))
    if whole is not None:
        return whole
    for block in reversed(FENCE.findall(text)):
        found = _unwrap(_loads(block))
        if found is not None:
            return found
    decoder, last, pos = json.JSONDecoder(), None, 0
    while (start := text.find("{", pos)) != -1:
        try:
            obj, end = decoder.raw_decode(text, start)
        except ValueError:
            pos = start + 1
            continue
        if isinstance(obj, dict):
            last = obj
        pos = end
    return _unwrap(last)


def missing_keys(answer: dict | None, schema: dict) -> list[str]:
    required = schema.get("required", [])
    return list(required) if not isinstance(answer, dict) else [k for k in required if k not in answer]


# ==== Schemas (strict form: every property required, no extra properties) ====

def _obj(**props) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def _arr(items: dict) -> dict:
    return {"type": "array", "items": items}


STR, INT, BOOL = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}
ACCEPTANCE = _obj(given=STR, when=STR, then=STR, **{"and": STR})
ROUTE = _obj(**{"steps": _arr(STR), "expected": STR, "pass": STR, "fail": STR})
PLAN_SCHEMA = _obj(summary=STR, scope=_arr(STR), out_of_scope=_arr(STR), acceptance=ACCEPTANCE,
                   approach=_arr(STR), files=_arr(STR), validation_route=ROUTE, risks=_arr(STR),
                   effort=INT, effort_reason=STR)
IMPLEMENT_SCHEMA = _obj(changed_files=_arr(STR), tests=_arr(_obj(command=STR, passed=BOOL, summary=STR)),
                        validation_route=ROUTE, docs_updated=_arr(STR),
                        debt=_obj(paid=_arr(STR), introduced=_arr(STR), carried=_arr(_obj(item=STR, revisit=STR))),
                        follow_ups=_arr(STR), commit_message=STR)
REVIEW_SCHEMA = _obj(verdict={"type": "string", "enum": ["approve", "changes"]},
                     findings=_arr(_obj(severity={"type": "string", "enum": ["blocking", "minor"]},
                                        file=STR, line=INT, issue=STR, fix=STR)))
INTERVIEW_SCHEMA = _obj(context_summary=STR,
                        questions=_arr(_obj(id=STR, text=STR, options=_arr(STR), recommended=STR, why=STR)))
PROPOSE_SCHEMA = _obj(
    language=STR,
    briefing=_obj(purpose=STR, current_state=STR, architecture=_arr(STR), product=_arr(STR),
                  constraints=_arr(STR), glossary=_arr(_obj(term=STR, meaning=STR))),
    principles=_arr(_obj(name=STR, text=STR)),
    dev=_obj(commands=_obj(install=STR, test=STR, lint=STR, run=STR), verify=_arr(STR), notes=_arr(STR)),
    roadmap=_arr(_obj(code=STR, level=STR, title=STR, intent=STR, done_condition=STR, acceptance=ACCEPTANCE,
                      effort=INT, effort_reason=STR, order=INT, writer=STR)),
    open_questions=_arr(_obj(title=STR, question=STR)))
CHECK_SCHEMA = _obj(ok=BOOL)


def skeleton(schema: dict):
    """A compact example value for a schema, embedded in prompts."""
    if schema.get("type") == "object":
        return {k: skeleton(v) for k, v in schema["properties"].items()}
    if schema.get("type") == "array":
        return [skeleton(schema["items"])]
    if "enum" in schema:
        return "|".join(schema["enum"])
    return {"string": "", "integer": 0, "boolean": False}[schema["type"]]


# ==== Agent calls ====

PROMPT_ARG_LIMIT = 8000
QUOTA_DEFAULT = ["usage limit", "rate.?limit", "\\b429\\b", "quota"]
DENIED = re.compile(r"auto-denied|permission.{0,40}denied|denied.{0,40}permission", re.I)


@dataclass
class Call:
    cmd: list[str]
    stdin: str | None
    out_file: Path | None
    label: str


@dataclass
class Result:
    code: int
    output: str
    timed_out: bool = False


class QuotaHit(Exception):
    def __init__(self, agent: str, reset: str = ""):
        super().__init__(agent)
        self.agent, self.reset = agent, reset


def resolve_exe(agent: dict) -> str | None:
    names = agent["exe"] if isinstance(agent["exe"], list) else [agent["exe"]]
    return next((found for found in map(shutil.which, names) if found), None)


def build_call(name: str, agent: dict, role_args: str, band: dict, prompt: str, *, project: Path,
               schema: dict | None, files: Path) -> Call:
    """Command for one agent step. `files` is the path stem for the schema, out, and prompt files."""
    exe = resolve_exe(agent)
    if not exe:
        raise Stop(f"CLI de '{name}' não encontrada no PATH: {agent['exe']}")
    if agent.get("extra_prompt"):
        prompt = prompt.rstrip() + "\n" + agent["extra_prompt"].strip()
    args = [*agent[role_args], *band["args"]]
    if name == "copilot":
        # Migrate old configs: Auto cannot accept an explicit reasoning effort.
        model = args[args.index("--model") + 1] if "--model" in args else "auto"
        if model == "auto":
            band = {**band, "model": "auto"}
            while "--reasoning-effort" in args:
                at = args.index("--reasoning-effort")
                del args[at:at + 2]
            if "--model" not in args:
                args += ["--model", "auto"]
    schema_file = out_file = None
    if schema is not None and agent.get("schema"):
        schema_file = files.with_name(files.name + ".schema.json")
        write(schema_file, json.dumps(schema))
        args += agent["schema"]
    if agent.get("out"):
        out_file = files.with_name(files.name + ".out.txt")
        args += agent["out"]
    args += agent.get("tail", [])
    uses_arg = any("{prompt}" in a for a in args)
    one_line = " ".join(line.strip() for line in prompt.splitlines() if line.strip())
    if uses_arg and len(one_line) > PROMPT_ARG_LIMIT:
        prompt_file = files.with_name(files.name + ".prompt.md")
        write(prompt_file, prompt)
        rel = Path(os.path.relpath(prompt_file, project)).as_posix()
        one_line = (f"ARIAD ORCHESTRATED. Your full instructions are in {rel}. "
                    "Read that file first and follow it exactly.")
    values = {"{project}": str(project), "{schema}": json.dumps(schema) if schema else "",
              "{schema_file}": str(schema_file or ""), "{out}": str(out_file or ""), "{prompt}": one_line}

    def fill(arg: str) -> str:
        for key, value in values.items():
            arg = arg.replace(key, value)
        return arg

    return Call([exe, *map(fill, args)], None if uses_arg else prompt, out_file, f"{name}({band_label(band)})")


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.kill()
    proc.wait()


class Printer:
    """Writes agent text to the terminal with a `  │ ` prefix at each line start."""

    def __init__(self, enabled: bool):
        self.enabled, self.fresh = enabled, True

    def write(self, text: str | None) -> None:
        if not self.enabled or not text:
            return
        for piece in text.splitlines(keepends=True):
            sys.stdout.write(("  │ " if self.fresh else "") + piece)
            self.fresh = piece.endswith("\n")
        sys.stdout.flush()

    def end(self) -> None:
        if self.enabled and not self.fresh:
            sys.stdout.write("\n")
            self.fresh = True


def display_text(line: str) -> str | None:
    """Terminal text for one output line: agent text from JSON events; other events are hidden."""
    stripped = line.strip()
    event = _loads(stripped) if stripped.startswith("{") else None
    if not isinstance(event, dict):
        return line
    if event.get("type") == "assistant":
        parts = []
        for block in (event.get("message") or {}).get("content") or []:
            if block.get("type") == "text" and block.get("text", "").strip():
                parts.append(block["text"].rstrip() + "\n")
            elif block.get("type") == "tool_use":
                parts.append(f"→ {block.get('name', 'tool')}\n")
        return "".join(parts) or None
    if event.get("event") == "step_update":
        return (event.get("step_update") or {}).get("text_delta") or None
    if event.get("type") == "assistant.message_delta":
        return (event.get("data") or {}).get("deltaContent") or None
    return None


def run_process(cmd: list[str] | str, stdin: str | None, cwd: Path, timeout_s: float, log: Path,
                stream: bool = False, on_line=None, progress: str = "") -> Result:
    """Runs a command and tees its output to `log`. A string command runs through the shell."""
    log.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "NO_COLOR": "1", "PYTHONIOENCODING": "utf-8"}
    printer, chunks = Printer(stream), []
    with log.open("w", encoding="utf-8") as fh:
        fh.write("$ " + (cmd if isinstance(cmd, str) else subprocess.list2cmdline(cmd)) + "\n")
        if stdin:
            fh.write("--- prompt ---\n" + stdin + "\n")
        fh.write("--- output ---\n")
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, shell=isinstance(cmd, str), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def pump() -> None:
            for raw in iter(proc.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace")
                chunks.append(line)
                fh.write(line)
                fh.flush()
                if on_line:
                    on_line(line)
                printer.write(display_text(line))

        reader = threading.Thread(target=pump, daemon=True)
        reader.start()
        try:
            if stdin:
                proc.stdin.write(stdin.encode("utf-8"))
            proc.stdin.close()
        except OSError:
            pass
        timed_out = False
        started = time.monotonic()
        try:
            if progress and sys.stdout.isatty():
                tick = 0
                while proc.poll() is None:
                    elapsed = time.monotonic() - started
                    remaining = timeout_s - elapsed
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(cmd, timeout_s)
                    sys.stdout.write(f"\r  {'◐◓◑◒'[tick % 4]} {progress} · {elapsed:.0f}s ")
                    sys.stdout.flush()
                    tick += 1
                    try:
                        proc.wait(timeout=min(0.5, remaining))
                    except subprocess.TimeoutExpired:
                        pass
            else:
                proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_tree(proc)
        except KeyboardInterrupt:
            kill_tree(proc)
            raise
        finally:
            if progress and sys.stdout.isatty():
                sys.stdout.write("\r" + " " * (len(progress) + 24) + "\r")
                sys.stdout.flush()
        reader.join(timeout=5)
        if not reader.is_alive():
            proc.stdout.close()
        printer.end()
    return Result(proc.returncode, "".join(chunks), timed_out)


def fmt_epoch(value) -> str:
    try:
        return dt.datetime.fromtimestamp(int(value)).strftime("%d/%m %H:%M")
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def claude_windows(event: dict) -> list[tuple[str, int]]:
    windows = (event.get("rate_limit_info") or {}).get("unifiedWindows") or {}
    out = []
    for key, label in (("five_hour", "5h"), ("seven_day", "semana")):
        w = windows.get(key)
        if isinstance(w, dict) and isinstance(w.get("utilization"), (int, float)):
            out.append((label, round(100 - 100 * w["utilization"])))
    return out


def claude_rejected(output: str) -> str | None:
    """Reset time (maybe empty) when a Claude rate_limit_event says rejected; None otherwise."""
    for line in output.splitlines():
        if '"rate_limit_event"' in line:
            info = (_loads(line.strip()) or {}).get("rate_limit_info") or {}
            if info.get("status") == "rejected":
                return fmt_epoch(info.get("resetsAt"))
    return None


def hit_quota(agent: dict, output: str) -> bool:
    return any(re.search(p, output, re.I) for p in agent.get("quota", QUOTA_DEFAULT))


@dataclass
class Ctx:
    root: Path
    cfg: dict
    usage: dict = field(default_factory=dict)       # agent -> Availability, updated live
    exhausted: dict = field(default_factory=dict)   # agent -> reset text
    automode: bool = False

    @property
    def logs(self) -> Path:
        return self.root / ".ariad" / "logs"

    def note_usage(self, name: str, line: str) -> None:
        if '"rate_limit_event"' in line and name in self.usage:
            windows = claude_windows(_loads(line.strip()) or {})
            if windows:
                self.usage[name].windows = windows


def call_agent(ctx: Ctx, name: str, role_args: str, effort: int, tag: str, step: str, prompt: str,
               schema: dict, stream: bool = False) -> dict:
    """Runs one agent step and returns its JSON answer. Raises QuotaHit on a usage limit, Stop on failure."""
    agent = ctx.cfg["agents"][name]
    band = band_for(agent, effort)
    timeout = float(ctx.cfg["project"]["timeout_minutes"]) * 60
    body = prompt.rstrip() + "\nFinal answer: only one JSON object shaped like " + json.dumps(skeleton(schema))
    missing: list[str] = []
    log = None
    for attempt in (1, 2):
        text = body if attempt == 1 else (
            body + f"\nYour previous attempt ended without a valid JSON answer (missing: {', '.join(missing)}). "
            "File changes you made are still in place; do not redo them. Reply with only the JSON object.")
        stem = ctx.logs / f"{local_stamp()}_{slug(tag, 24)}_{step}_{name}_{attempt}"
        call = build_call(name, agent, role_args, band, text, project=ctx.root, schema=schema, files=stem)
        log = stem.with_name(stem.name + ".log")
        print(f"  · {step} · {call.label}")
        result = run_process(call.cmd, call.stdin, ctx.root, timeout, log, stream=False,
                             on_line=lambda line: ctx.note_usage(name, line),
                             progress=f"{step} · {call.label}" if stream else "")
        if result.timed_out:
            raise Stop(f"{name} excedeu {timeout / 60:.0f} min. Log: {log}")
        output = result.output
        if call.out_file and call.out_file.is_file() and read(call.out_file).strip():
            output = read(call.out_file)
        answer = extract_json(output)
        missing = missing_keys(answer, schema)
        if not missing and result.code == 0:
            if stream:
                render_answer(step, call.label, answer)
            return answer
        reset = claude_rejected(result.output)
        if reset is not None or (result.code != 0 and hit_quota(agent, result.output)):
            raise QuotaHit(name, reset or "")
        if DENIED.search(result.output):
            raise Stop(f"{name} negou uma permissão e não respondeu. Ajuste os args em ariad.toml. Log: {log}")
        if result.code != 0:
            lines = [line.strip() for line in result.output.splitlines() if line.strip()]
            decisive = next((line for line in lines if re.search(r"error|failed|invalid", line, re.I)),
                            lines[-1] if lines else "sem detalhes")
            raise Stop(f"{name} falhou (código {result.code}): {decisive[:600]}. Log: {log}")
    raise Stop(f"{name} não devolveu JSON válido (faltando: {', '.join(missing)}). Log: {log}")


# ==== Agent availability ====

@dataclass
class Availability:
    name: str
    installed: bool = False
    logged: bool | None = None
    windows: list = field(default_factory=list)   # [(label, percent left)]
    reset: str = ""
    blocked: bool = False
    note: str = ""

    def state(self, min_available: int) -> str:
        if not self.installed:
            return "não instalado"
        if self.logged is False:
            return "não logado"
        if self.blocked or any(left <= 0 for _, left in self.windows):
            return "esgotado"
        if self.windows and min(left for _, left in self.windows) < min_available:
            return "baixo"
        return "ok"


CLAUDE_PROBE = ["-p", "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands", "--tools", "",
                "--system-prompt", "Reply with ok.", "--model", "haiku", "--output-format", "stream-json",
                "--verbose", "--no-session-persistence", "ok"]


def run_quiet(cmd: list[str], timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, stdin=subprocess.DEVNULL)


def probe_claude(exe: str, av: Availability, timeout: float) -> None:
    status = _loads(run_quiet([exe, "auth", "status"], timeout).stdout.strip()) or {}
    av.logged = bool(status.get("loggedIn"))
    if not av.logged:
        return
    for line in run_quiet([exe, *CLAUDE_PROBE], timeout).stdout.splitlines():
        if '"rate_limit_event"' in line:
            event = _loads(line.strip()) or {}
            info = event.get("rate_limit_info") or {}
            av.windows = claude_windows(event)
            av.blocked = info.get("status") == "rejected"
            resets = [w.get("resetsAt") for w in (info.get("unifiedWindows") or {}).values()
                      if isinstance(w, dict) and w.get("resetsAt")]
            av.reset = fmt_epoch(min(resets)) if resets else ""


def read_jsonrpc(stream, want_id: int, timeout: float) -> dict | None:
    box: list = []

    def pump() -> None:
        for line in stream:
            msg = _loads(line.strip())
            if isinstance(msg, dict) and msg.get("id") == want_id:
                box.append(msg)
                return

    reader = threading.Thread(target=pump, daemon=True)
    reader.start()
    reader.join(timeout)
    return box[0] if box else None


def window_label(minutes) -> str:
    return {300: "5h", 10080: "semana"}.get(minutes) or (f"{int(minutes) // 60}h" if minutes else "?")


def parse_codex_limits(result: dict, av: Availability) -> None:
    limits = result.get("rateLimits") or {}
    resets = []
    for key in ("primary", "secondary"):
        w = limits.get(key)
        if isinstance(w, dict) and isinstance(w.get("usedPercent"), (int, float)):
            av.windows.append((window_label(w.get("windowDurationMins")), round(100 - w["usedPercent"])))
            if w.get("resetsAt"):
                resets.append(w["resetsAt"])
    av.reset = fmt_epoch(min(resets)) if resets else ""
    av.blocked = result.get("ordinaryUsageAllowed") is False or bool(limits.get("rateLimitReachedType"))


def probe_codex(exe: str, av: Availability, timeout: float) -> None:
    proc = subprocess.Popen([exe, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    try:
        for msg in ({"method": "initialize", "id": 0,
                     "params": {"clientInfo": {"name": "ariad", "title": "Ariad", "version": VERSION}}},
                    {"method": "initialized"}, {"method": "account/rateLimits/read", "id": 1}):
            proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        answer = read_jsonrpc(proc.stdout, 1, timeout)
    finally:
        kill_tree(proc)
    if answer is None:
        return
    if "error" in answer:
        av.logged = False
        av.note = str((answer.get("error") or {}).get("message", ""))[:60]
        return
    av.logged = True
    parse_codex_limits(answer.get("result") or {}, av)


def parse_copilot_user(data: dict, av: Availability) -> None:
    av.logged = bool(data.get("cli_enabled", True))
    left = [s["percent_remaining"] for key, s in (data.get("quota_snapshots") or {}).items()
            if key != "completions" and isinstance(s, dict) and not s.get("unlimited")
            and (s.get("entitlement") or 0) > 0 and isinstance(s.get("percent_remaining"), (int, float))]
    if left:
        av.windows = [("mês", round(min(left)))]
    reset = str(data.get("quota_reset_date") or "")
    av.reset = f"{reset[8:10]}/{reset[5:7]}" if len(reset) >= 10 else ""


def probe_copilot(exe: str, av: Availability, timeout: float) -> None:
    gh = shutil.which("gh")
    if not gh:
        av.note = "sem gh: uso não informado"
        return
    run = run_quiet([gh, "api", "copilot_internal/user"], timeout)
    data = _loads(run.stdout)
    if run.returncode != 0 or not isinstance(data, dict):
        av.note = "gh sem acesso ao Copilot"
        return
    parse_copilot_user(data, av)


def probe_agy(exe: str, av: Availability, timeout: float) -> None:
    av.logged = run_quiet([exe, "models"], timeout).returncode == 0
    av.note = "uso não informado"


PROBES = {"claude": probe_claude, "codex": probe_codex, "copilot": probe_copilot, "agy": probe_agy}


def probe(name: str, agent: dict, timeout: float = 60) -> Availability:
    av = Availability(name)
    exe = resolve_exe(agent)
    av.installed = exe is not None
    kind = agent.get("usage", "none")
    if exe and kind in PROBES:
        try:
            PROBES[kind](exe, av, timeout)
        except (OSError, subprocess.SubprocessError, ValueError) as e:
            av.note = f"sonda falhou: {type(e).__name__}"
    return av


def check_agents(cfg: dict, names: list[str] | None = None) -> dict:
    names = list(names or cfg["agents"])
    with ThreadPoolExecutor(max_workers=max(1, len(names))) as pool:
        found = list(pool.map(lambda n: probe(n, cfg["agents"][n]), names))
    return {av.name: av for av in found}


def usage_text(av: Availability) -> str:
    return " · ".join(f"{label} {left}%" for label, left in av.windows) or "?"


VERSION_SOURCES = {
    "claude": "https://registry.npmjs.org/@anthropic-ai/claude-code/latest",
    "codex": "https://registry.npmjs.org/@openai/codex/latest",
    "copilot": "https://api.github.com/repos/github/copilot-cli/releases/latest",
    "agy": "https://api.github.com/repos/google-antigravity/antigravity-cli/releases/latest",
}


def cli_version(name: str, agent: dict) -> tuple[str, str, str]:
    exe = resolve_exe(agent)
    if not exe:
        return name, "—", "não instalado"
    local = "?"
    try:
        run = run_quiet([exe, "--version"], 15)
        match = re.search(r"\b\d+\.\d+\.\d+(?:-[\w.]+)?", run.stdout)
        if run.returncode or not match:
            return name, local, "versão local não identificada"
        local = match.group()
        if os.environ.get("ARIAD_OFFLINE") == "1":
            return name, local, "atualização não verificada (modo offline)"
        url = agent.get("version_url") or VERSION_SOURCES.get(agent.get("usage", name))
        if not url:
            return name, local, "atualização não verificada; configure version_url"
        request = urllib.request.Request(url, headers={"User-Agent": "ariad-sidecar"})
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
        latest = str(data.get("version") or data.get("tag_name") or "").removeprefix("v")
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[\w.]+)?", latest):
            return name, local, "fonte sem versão reconhecida"
        def numbers(v):
            return tuple(int(n) for n in v.split("-")[0].split("."))
        status = f"atualização disponível: {latest}" if numbers(local) < numbers(latest) else "atualizado"
        return name, local, status
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return name, local, f"atualização não verificada ({type(exc).__name__})"


def check_cli_versions(cfg: dict) -> None:
    banner("Inicialização · versões dos CLIs")
    with ThreadPoolExecutor(max_workers=max(1, len(cfg["agents"]))) as pool:
        rows = list(pool.map(lambda pair: cli_version(*pair), cfg["agents"].items()))
    for name, version, status in rows:
        print(f"  {name:<12} {version:<18} {status}")


def agents_table(avail: dict, min_available: int) -> str:
    yes_no = {True: "sim", False: "não", None: "?"}
    rows = [("agente", "instalado", "logado", "uso livre", "reset", "estado")]
    for av in avail.values():
        state = av.state(min_available)
        if state == "ok" and av.note:
            state = f"ok ({av.note})"
        rows.append((av.name, yes_no[av.installed], yes_no[av.logged] if av.installed else "-",
                     usage_text(av), av.reset or "?", state))
    widths = [max(len(r[c]) for r in rows) for c in range(5)]
    return "\n".join("  " + "  ".join(v.ljust(w) for v, w in zip(r, widths)) + "  " + r[5] for r in rows)


def usable(avail: dict, name: str, min_available: int) -> bool:
    return name in avail and avail[name].state(min_available) == "ok"


def default_roster(cfg: dict, avail: dict, previous: dict | None) -> dict:
    min_available = cfg["project"]["min_available"]
    ok = [n for n in cfg["agents"] if usable(avail, n, min_available)]
    prev = previous or {}

    def first(*candidates: str) -> str:
        return next((c for c in candidates if c in ok), ok[0] if ok else "")

    writer = first(prev.get("writer", ""), cfg["roles"]["writer"])
    brain = first(prev.get("brain", ""), cfg["roles"]["brain"])
    wanted = prev.get("reviewers") or cfg["roles"]["reviewers"]
    return {"writer": writer, "brain": brain, "reviewers": [r for r in wanted if r in ok and r != writer]}


def pick_agent(cfg: dict, avail: dict, label: str, default: str) -> str:
    min_available = cfg["project"]["min_available"]
    while True:
        answer = ask(f"  {label} [{default}]: ") or default
        if answer in cfg["agents"]:
            if not usable(avail, answer, min_available):
                state = avail[answer].state(min_available) if answer in avail else "?"
                print(f"  Aviso: {answer} está '{state}'.")
            return answer
        print(f"  Agente desconhecido: {answer or '(vazio)'}. Opções: {', '.join(cfg['agents'])}")


def choose_roster(cfg: dict, avail: dict, previous: dict | None, brain_only: bool = False) -> dict:
    """Shows availability and asks which agents take part in this execution."""
    print(agents_table(avail, cfg["project"]["min_available"]))
    roster = default_roster(cfg, avail, previous)
    if not (roster["brain"] if brain_only else roster["writer"]):
        resets = ", ".join(f"{a.name} {a.reset}" for a in avail.values() if a.reset)
        raise Stop("Nenhum agente disponível agora." + (f" Resets: {resets}." if resets else ""), STOPPED)
    if brain_only:
        roster["brain"] = pick_agent(cfg, avail, "Cérebro", roster["brain"])
        return roster
    roster["writer"] = pick_agent(cfg, avail, "Escritor", roster["writer"])
    while True:
        default = ",".join(r for r in roster["reviewers"] if r != roster["writer"]) or "-"
        answer = ask(f"  Revisores [{default}] (vírgulas; - para nenhum): ") or default
        names = [] if answer.strip() == "-" else [n.strip() for n in answer.split(",") if n.strip()]
        unknown = [n for n in names if n not in cfg["agents"]]
        if not unknown:
            roster["reviewers"] = [n for n in names if n != roster["writer"]]
            return roster
        print(f"  Agente desconhecido: {', '.join(unknown)}. Opções: {', '.join(cfg['agents'])}")


def replace_agent(ctx: Ctx, role: str, failed: str, reset: str, exclude=()) -> str | None:
    """After a usage limit: shows availability and asks for a substitute. None skips a reviewer."""
    ctx.exhausted[failed] = reset or "?"
    others = [n for n in ctx.cfg["agents"] if n not in ctx.exhausted and n not in exclude]
    avail = check_agents(ctx.cfg, others) if others else {}
    ctx.usage.update(avail)
    min_available = ctx.cfg["project"]["min_available"]
    if ctx.automode:
        candidates = [n for n in others if usable(avail, n, 0)]
        if not candidates:
            raise Stop("Cota disponível esgotada. Estado salvo para retomar.", STOPPED)
        return candidates[0]
    if avail:
        print(agents_table(avail, min_available))
    label = {"writer": "escritor", "brain": "cérebro"}.get(role, "revisor")
    until = f" (reseta {reset})" if reset else ""
    if not others:
        if role == "reviewer":
            print(f"  {failed} esgotado{until}; sem substituto, seguindo sem este revisor.")
            return None
        raise Stop(f"{failed} esgotado{until} e nenhum agente sobrou para {label}.", STOPPED)
    default = ([n for n in others if usable(avail, n, min_available)] or others)[0]
    skip = ", [p]ular este revisor" if role == "reviewer" else ""
    while True:
        answer = ask(f"  {failed} esgotado{until}. Novo {label} [{default}]{skip} ou [s]air: ") or default
        if answer == "s":
            raise Stop("Parado a pedido. Rode o mesmo comando para retomar.", STOPPED)
        if answer == "p" and role == "reviewer":
            return None
        if answer in others:
            return answer
        print(f"  Opções: {', '.join(others)}{skip} ou s.")


def cmd_agents(args) -> int:
    root = project_root()
    cfg = load_config(root / ".ariad" / "ariad.toml")
    check_cli_versions(cfg)
    print(agents_table(check_agents(cfg), cfg["project"]["min_available"]))
    return OK


# ==== Git ====

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def git(root: Path, *args: str, check: bool = True, input: str | None = None) -> str:
    run = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8",
                         errors="replace", input=input)
    if check and run.returncode != 0:
        raise Stop(f"git {' '.join(args[:2])} falhou: {(run.stderr or run.stdout).strip()[:300]}")
    return run.stdout.rstrip("\n")


def is_repo(root: Path) -> bool:
    """True only when `root` itself is the top of a Git work tree."""
    if not shutil.which("git"):
        return False
    top = git(root, "rev-parse", "--show-toplevel", check=False).strip()
    return bool(top) and Path(top).resolve() == root.resolve()


def head(root: Path) -> str:
    return git(root, "rev-parse", "--verify", "-q", "HEAD", check=False).strip() or EMPTY_TREE


def changed_paths(root: Path) -> list[str]:
    lines = git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    return [line[3:].strip().strip('"') for line in lines if line.strip()]


def staged_diff(root: Path, base: str, limit_kb: int) -> tuple[str, str]:
    """Stages everything; returns (diff against base, truncated to limit_kb, and its shortstat)."""
    git(root, "add", "-A")
    diff = git(root, "diff", "--cached", base)
    stat = git(root, "diff", "--cached", "--shortstat", base).strip()
    data = diff.encode("utf-8")
    if len(data) > limit_kb * 1024:
        diff = data[:limit_kb * 1024].decode("utf-8", errors="ignore") + (
            f"\n[diff truncated at {limit_kb} KB; read the files or run git diff {base[:10]} -- <file>]")
    return diff, stat


def commit(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-F", "-", input=message)


# ==== Export and init ====

SIDECAR_FILES = ("ariad.py", "ariad.toml", "README.md", ".gitignore")


def cmd_export(args) -> int:
    src = templates_dir()
    toml_path = SCRIPT_DIR / "ariad.toml"
    load_config(toml_path)
    if not (src / "AGENTS.md").is_file():
        raise Stop(f"AGENTS.md ausente em {src}.")
    missing = [n for n in SIDECAR_FILES if not (SCRIPT_DIR / n).is_file()]
    if missing:
        raise Stop("Sidecar incompleto, faltam: " + ", ".join(missing))
    out = Path(args.out).resolve() if args.out else Path.cwd() / f"ariad-sidecar-{VERSION}.zip"
    if out.suffix.lower() != ".zip":
        out = out.with_suffix(".zip")
    if out.exists():
        raise Stop(f"{out} já existe; escolha outro nome com --out.")
    clean_toml = toml_with(toml_with(read(toml_path), "project", "verify", []), "project", "language", "en")
    rels = template_files(src)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in SIDECAR_FILES:
            if name == "ariad.toml":
                z.writestr(".ariad/ariad.toml", clean_toml)
            else:
                z.write(SCRIPT_DIR / name, f".ariad/{name}")
        for rel in rels:
            z.write(src / rel, f".ariad/templates/{rel.as_posix()}")
    print(f"Exportado: {out} ({len(SIDECAR_FILES) + len(rels)} arquivos, "
          f"{out.stat().st_size // 1024} KB, Ariad {VERSION})")
    print(f'Instale na raiz do projeto: tar -xf "{out}" -C <projeto>')
    print("Depois: python .ariad/ariad.py init")
    return OK


def cmd_init(args) -> int:
    root = project_root()
    if not args.dry_run:
        check_cli_versions(load_config(root / ".ariad" / "ariad.toml"))
    src = templates_dir()
    created, kept = [], []
    for rel in template_files(src):
        target = root / rel
        if target.exists():
            kept.append(rel.as_posix())
            continue
        created.append(rel.as_posix())
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src / rel, target)
    prefix = "[dry-run] " if args.dry_run else ""
    for rel in created:
        print(f"  {prefix}+ {rel}")
    for rel in kept:
        print(f"  = {rel} (mantido)")
    agents_md = root / "AGENTS.md"
    if agents_md.is_file() and "Ariad" not in read(agents_md):
        print("  Aviso: AGENTS.md existente não menciona Ariad; mescle com .ariad/templates/AGENTS.md.")
    if not args.dry_run and not is_repo(root):
        if ask("  Inicializar git aqui? [s/N] ").lower().startswith("s"):
            git(root, "init", "-q")
            print("  ✔ git init")
        else:
            print("  Sem git: `run` exige um repositório próprio.")
    print(f"\n{prefix}{len(created)} criados, {len(kept)} mantidos. "
          "Próximo: faça commit e rode python .ariad/ariad.py setup")
    return OK


# ==== Story prompts and screens ====

EFFORT_SCALE = ("effort scale: 1-2 trivial (text or config, one file), 3-4 small (one component, few tests), "
                "5-6 moderate (several files, new tested behavior), 7-8 large (cross-module, new integration or "
                "contract, notable risk), 9-10 critical (architecture, security, data migration; prefer splitting)")


def header(role: str, step: str, state: dict | None, cfg: dict) -> str:
    story = f" | story={state['story']} effort={state['effort']}" if state else ""
    return f"ARIAD ORCHESTRATED | role={role} step={step}{story} | language={cfg['project']['language']}"


def prompt_plan(state: dict, cfg: dict) -> str:
    route = ("validation_route: internal evidence for this Technical Story (tests, diagnostics, commands)."
             if state["level"] == "Technical Story" else
             "validation_route: steps the Navigator can run, the expected observation, pass and fail conditions.")
    lines = [header("writer", "plan", state, cfg),
             f"You are the Ariad Driver for story {state['story']}. Read AGENTS.md, "
             f"docs/process/development-guide.md, and {state['path']}.",
             "Read only the code this story needs. Do not edit any file in this step.",
             "Plan this story only. Keep scope; list related work in out_of_scope.",
             "acceptance: observable Given/When/Then/And. " + route,
             f"effort: your estimate from 1 to 10; {EFFORT_SCALE}.",
             f"Write text values in {cfg['project']['language']}."]
    if state.get("feedback"):
        lines.append("Navigator feedback on the previous plan: " + state["feedback"])
    return "\n".join(lines)


def prompt_implement(state: dict, cfg: dict) -> str:
    lines = [header("writer", "implement", state, cfg),
             f"Implement the approved plan for story {state['story']} ({state['path']}): "
             + json.dumps(state.get("plan") or {}, ensure_ascii=False),
             "Stay inside its scope. Write tests for behavior changes when practical and run them.",
             "Update project docs this change makes untrue (see AGENTS.md). Record debt that must outlive this "
             "story in docs/project/debt/items/.",
             f"Never commit or push. Never edit {state['path']} or .ariad/; the orchestrator records history.",
             f"Write text values in {cfg['project']['language']}. commit_message: subject line, blank line, why."]
    if state.get("resume"):
        lines.append("A previous attempt may have left partial changes in the working tree; continue from them.")
    if state.get("feedback"):
        lines.append(state["feedback"])
    return "\n".join(lines)


def prompt_review(state: dict, cfg: dict, diff: str) -> str:
    return "\n".join([
        header("reviewer", "review", state, cfg),
        f"Review this change read-only. Story and approved plan: {state['path']}. "
        f"Diff against {state['base'][:10]} is below.",
        "Report only material problems: behavior against the acceptance, scope drift, missing or weak tests, "
        "security, data loss, docs made untrue. No style comments.",
        "severity=blocking only when the story must not be accepted as is. verdict=approve when nothing is blocking.",
        f"Write text values in {cfg['project']['language']}.",
        "--- diff ---", diff or "(empty diff)"])


def fmt_acceptance(a: dict) -> str:
    parts = [f"Dado {a.get('given', '')}", f"Quando {a.get('when', '')}", f"Então {a.get('then', '')}"]
    return " · ".join(parts + ([f"E {a['and']}"] if a.get("and") else []))


def fmt_route(route: dict) -> list[str]:
    lines = [f"  {n}. {step}" for n, step in enumerate(route.get("steps") or [], 1)]
    return lines + [f"  esperado: {route.get('expected', '')} · passa: {route.get('pass', '')} · "
                    f"falha: {route.get('fail', '')}"]


def plan_lines(plan: dict) -> list[str]:
    def joined(key: str) -> str:
        return "; ".join(plan.get(key) or []) or "-"

    return [f"resumo: {plan.get('summary', '')}", f"escopo: {joined('scope')}", f"fora: {joined('out_of_scope')}",
            f"aceite: {fmt_acceptance(plan.get('acceptance') or {})}",
            "abordagem: " + " ".join(f"{n}. {s}" for n, s in enumerate(plan.get("approach") or [], 1)),
            f"arquivos: {', '.join(plan.get('files') or []) or '-'}", f"riscos: {joined('risks')}"]


def acceptance_lines(state: dict, stat: str, show_plan: bool) -> list[str]:
    result, reviews = state.get("result") or {}, state.get("reviews") or {}
    lines = plan_lines(state.get("plan") or {}) if show_plan else []
    lines.append(f"mudou: {stat or 'sem diff'}")
    verify = state.get("verify")
    if verify:
        last = (verify.get("tail") or "").strip().splitlines()[-1:] or [""]
        lines.append("verify: ✔" if verify["ok"] else f"verify: ✘ {last[0][:120]}")
    lines.append("revisão: " + (" · ".join(f"{n} {r.get('verdict', '?')}" for n, r in reviews.items())
                                or "nenhum revisor"))
    for name, review in reviews.items():
        for f in (review.get("findings") or [])[:5]:
            lines.append(f"achado {name} [{f.get('severity')}] {f.get('file')}:{f.get('line')} {f.get('issue')}")
    debt = result.get("debt") or {}
    carried = "; ".join(f"{c.get('item')} (revisitar: {c.get('revisit')})" for c in debt.get("carried") or [])
    lines.append(f"débito: introduzido {'; '.join(debt.get('introduced') or []) or 'nenhum'}"
                 f" · carregado {carried or 'nenhum'}")
    if result.get("follow_ups"):
        lines.append("follow-ups: " + "; ".join(result["follow_ups"]))
    lines.append("rota de validação:")
    lines += fmt_route(result.get("validation_route") or (state.get("plan") or {}).get("validation_route") or {})
    subject = (result.get("commit_message") or "").strip().splitlines()[:1]
    lines.append("commit: " + (subject[0] if subject else "(sem mensagem)"))
    return lines


def render_plan(plan: dict) -> str:
    lines = [plan.get("summary", ""), ""]
    for label, key in (("Scope", "scope"), ("Out of scope", "out_of_scope"), ("Approach", "approach"),
                       ("Files", "files"), ("Risks", "risks")):
        if plan.get(key):
            lines += [f"**{label}:**"] + [f"- {v}" for v in plan[key]] + [""]
    a = plan.get("acceptance") or {}
    lines += ["**Acceptance:**", "", f"Given {a.get('given', '')}", f"When {a.get('when', '')}",
              f"Then {a.get('then', '')}"] + ([f"And {a['and']}"] if a.get("and") else []) + [""]
    lines.append(f"**Effort:** {plan.get('effort', '')} ({plan.get('effort_reason', '')})")
    return "\n".join(lines).strip()


def render_route(route: dict, verify: dict | None) -> str:
    lines = [f"{n}. {step}" for n, step in enumerate(route.get("steps") or [], 1)]
    lines += ["", f"- Expected: {route.get('expected', '')}", f"- Pass: {route.get('pass', '')}",
              f"- Fail: {route.get('fail', '')}"]
    if verify:
        lines.append(f"- Automated verify: {'passed' if verify['ok'] else 'failed'}")
    return "\n".join(lines).strip()


def render_review(state: dict) -> str:
    result, reviews = state.get("result") or {}, state.get("reviews") or {}
    lines = [f"- {name}: {r.get('verdict', 'unavailable')}" for name, r in reviews.items()] or ["- no reviewer"]
    for review in reviews.values():
        lines += [f"  - [{f.get('severity')}] {f.get('file')}:{f.get('line')} {f.get('issue')}"
                  for f in review.get("findings") or []]
    debt = result.get("debt") or {}
    carried = "; ".join(f"{c.get('item')} (revisit: {c.get('revisit')})" for c in debt.get("carried") or [])
    lines += ["", f"Debt paid: {'; '.join(debt.get('paid') or []) or 'none'}",
              f"Debt introduced: {'; '.join(debt.get('introduced') or []) or 'none'}",
              f"Debt carried: {carried or 'none'}"]
    if result.get("follow_ups"):
        lines += ["", "Follow-ups:"] + [f"- {x}" for x in result["follow_ups"]]
    return "\n".join(lines)


def run_verify(root: Path, commands: list[str], logs: Path, timeout_s: float) -> tuple[bool, str]:
    """Runs the project verify commands through the shell; returns (passed, last 60 output lines)."""
    output, ok = [], True
    for n, command in enumerate(commands, 1):
        print(f"  · verify: {command}")
        result = run_process(command, None, root, timeout_s, logs / f"{local_stamp()}_verify_{n}.log")
        output.append(f"$ {command}\n{result.output}")
        if result.timed_out or result.code != 0:
            ok = False
            break
    return ok, "\n".join("\n".join(output).splitlines()[-60:])


# ==== Story runner ====

class Runner:
    """One story at a time: plan, plan stop, implement, verify, review, acceptance, commit."""

    def __init__(self, ctx: Ctx, state: dict):
        self.ctx, self.state = ctx, state
        ctx.exhausted = state.setdefault("exhausted", {})

    @property
    def cfg(self) -> dict:
        return self.ctx.cfg

    @property
    def root(self) -> Path:
        return self.ctx.root

    def save(self, **changes) -> None:
        self.state.update(changes)
        save_state(self.root, self.state)

    def update_story(self, fm: dict | None = None, sections: dict | None = None) -> None:
        path = self.root / self.state["path"]
        text = read(path)
        if fm:
            text = set_frontmatter(text, {**fm, "updated": today()})
        for name, content in (sections or {}).items():
            text = set_section(text, name, content)
        write(path, text)

    def note_agent(self, role: str, name: str) -> None:
        label = f"{role}={agent_label(self.cfg, name, self.state['effort'])}"
        if label not in self.state["agents"]:
            self.state["agents"].append(label)

    def pull(self, item: Item) -> None:
        if changed_paths(self.root):
            raise Stop("Árvore suja: faça commit ou stash antes de iniciar uma história.", STOPPED)
        roster = self.state["roster"]
        writer = item.writer if item.writer in (roster["writer"], *roster["reviewers"]) else roster["writer"]
        if item.writer and writer != item.writer:
            print(f"  writer '{item.writer}' fora do roster desta execução; usando {writer}.")
        effort = item.effort or 5
        self.state.update(story=item.code, path=item.path.as_posix(), title=item.title, level=item.level,
                          phase="plan", base=head(self.root), effort=effort, original_effort=effort,
                          writer=writer, round=0, feedback="", resume=False, rerun=[], plan={}, result={},
                          verify=None, reviews={}, agents=[], human_pending=False)
        self.update_story(fm={"status": "Active", "status_reason": "pulled by ariad run"})
        self.save()
        banner(f"{item.code} {item.title} · esforço {effort} · escritor {writer}")

    def advance(self) -> None:
        steps = {"plan": self.do_plan, "plan_checkpoint": self.do_plan_checkpoint,
                 "implement": self.do_implement, "verify": self.do_verify, "review": self.do_review,
                 "acceptance": self.do_acceptance, "commit": self.do_commit}
        while self.state.get("story"):
            steps[self.state["phase"]]()

    def writer_call(self, step: str, role_args: str, build, schema: dict) -> dict:
        while True:
            try:
                answer = call_agent(self.ctx, self.state["writer"], role_args, self.state["effort"],
                                    self.state["story"], step, build(), schema, stream=True)
                self.note_agent("writer", self.state["writer"])
                return answer
            except QuotaHit as hit:
                new = replace_agent(self.ctx, "writer", hit.agent, hit.reset)
                self.state["roster"]["writer"] = new
                self.save(writer=new, resume=step == "implement")

    def do_plan(self) -> None:
        plan = self.writer_call("plan", "read", lambda: prompt_plan(self.state, self.cfg), PLAN_SCHEMA)
        original = self.state["original_effort"]
        suggested = to_int(plan.get("effort"))
        effort = suggested if 1 <= suggested <= 10 else original
        fm = {"effort": effort, "effort_reason": plan.get("effort_reason", "")} if effort != original else None
        self.update_story(fm=fm, sections={"Plan": render_plan(plan)})
        stop = needs_plan_stop(self.cfg, original, effort)
        self.save(plan=plan, effort=effort, feedback="", phase="plan_checkpoint" if stop else "implement")

    def do_plan_checkpoint(self) -> None:
        s = self.state
        if self.ctx.automode:
            self.update_story(fm={"execution_mode": "automode", "human_validation": "pending"})
            self.save(phase="implement", plan_authorization="automode; human review pending")
            return
        note = f" (escritor sugere {s['effort']}; era {s['original_effort']})" if s["effort"] != s["original_effort"] else ""
        banner(f"PLANO · {s['story']} {s['title']} · esforço {s['effort']}{note}")
        for line in plan_lines(s["plan"]):
            print("  " + line)
        if s["effort"] >= 9:
            print("  esforço ≥ 9: considere dividir (deferir e rodar setup)")
        print("  [a]provar  [r]edirecionar  [d]eferir  [s]air")
        choice = menu("ards")
        if choice == "a":
            self.save(phase="implement")
        elif choice == "r":
            feedback = ask_text("O que mudar no plano?")
            if feedback:
                self.save(phase="plan", feedback=feedback)
        elif choice == "d":
            reason = ask_text("Motivo do adiamento?")
            if reason:
                self.update_story(fm={"status": "Deferred", "status_reason": reason.replace("\n", " ")})
                commit(self.root, f"Defer {s['story']} {s['title']}\n\n{reason}\n\nAriad-Story: {s['story']}\n")
                print(f"  ✔ {s['story']} adiada.")
                self.finish()
        else:
            raise Stop("Parado a pedido. Rode `run` para retomar no plano.", STOPPED)

    def do_implement(self) -> None:
        result = self.writer_call("implement", "write", lambda: prompt_implement(self.state, self.cfg),
                                  IMPLEMENT_SCHEMA)
        if not [p for p in changed_paths(self.root) if p != self.state["path"]]:
            raise Stop(f"{self.state['writer']} terminou sem mudar arquivos. Veja o log; rode `run` para tentar de novo.")
        self.save(result=result, resume=False, feedback="", phase="verify")

    def do_verify(self) -> None:
        commands = self.cfg["project"]["verify"]
        if not commands:
            self.save(verify=None, phase="review")
            return
        timeout = float(self.cfg["project"]["timeout_minutes"]) * 60
        ok, tail = run_verify(self.root, commands, self.ctx.logs, timeout)
        if ok:
            self.save(verify={"ok": True, "tail": tail}, phase="review")
        elif self.state["round"] < self.cfg["project"]["max_fix_rounds"]:
            self.save(verify={"ok": False, "tail": tail}, round=self.state["round"] + 1,
                      feedback="Verification failed. Fix it first:\n" + tail, phase="implement")
        else:
            self.save(verify={"ok": False, "tail": tail}, phase="acceptance")

    def do_review(self) -> None:
        s = self.state
        selected = pick_reviewers(s["roster"]["reviewers"], s["writer"], reviewer_count(self.cfg, s["effort"]))
        pending = [n for n in selected if n in s["roster"]["reviewers"]]
        if not pending:
            self.save(rerun=[], phase="acceptance")
            return
        diff, _ = staged_diff(self.root, s["base"], self.cfg["project"]["diff_limit_kb"])
        results = self.run_reviewers(pending, prompt_review(s, self.cfg, diff))
        reviews = results
        blocking = [n for n, r in results.items()
                    if r.get("verdict") == "changes" or
                    any(f.get("severity") == "blocking" for f in r.get("findings") or [])]
        if blocking and s["round"] < self.cfg["project"]["max_fix_rounds"]:
            fixes = [f"- [{n}] {f.get('file')}:{f.get('line')} {f.get('issue')} -> {f.get('fix')}"
                     for n in blocking for f in results[n]["findings"] if f.get("severity") == "blocking"]
            print(f"  {', '.join(blocking)} pediu mudanças; corrigindo (rodada {s['round'] + 1} de "
                  f"{self.cfg['project']['max_fix_rounds']})")
            self.save(reviews=reviews, rerun=blocking, round=s["round"] + 1, phase="implement",
                      feedback="Fix these blocking review findings first:\n" + "\n".join(fixes))
        else:
            self.save(reviews=reviews, rerun=[], phase="acceptance")

    def run_reviewers(self, names: list[str], prompt: str) -> dict:
        results: dict = {}
        queue = list(names)
        while queue:
            with ThreadPoolExecutor(max_workers=len(queue)) as pool:
                futures = {n: pool.submit(call_agent, self.ctx, n, "read", self.state["effort"],
                                          self.state["story"], "review", prompt, REVIEW_SCHEMA) for n in queue}
            queue = []
            for name, future in futures.items():
                try:
                    results[name] = future.result()
                    self.note_agent("reviewer", name)
                except QuotaHit as hit:
                    new = replace_agent(self.ctx, "reviewer", hit.agent, hit.reset,
                                        exclude=(self.state["writer"], *names, *results.keys(), *queue))
                    reviewers = [r for r in self.state["roster"]["reviewers"] if r != hit.agent]
                    if new and new != self.state["writer"] and new not in reviewers:
                        reviewers.append(new)
                        queue.append(new)
                    self.state["roster"]["reviewers"] = reviewers
                except Stop as e:
                    print(f"  revisão indisponível ({name}): {e}")
                    results[name] = {"verdict": "indisponível", "findings": []}
            self.save()
        return results

    def do_acceptance(self) -> None:
        s = self.state
        if self.ctx.automode:
            wanted = reviewer_count(self.cfg, s["effort"])
            reviews = s.get("reviews") or {}
            failed = s.get("verify") and not s["verify"].get("ok")
            failed = failed or any(t.get("passed") is False for t in s.get("result", {}).get("tests", []))
            blocked = any(r.get("verdict") != "approve" or
                          any(f.get("severity") == "blocking" for f in r.get("findings") or [])
                          for r in reviews.values())
            if failed or blocked or len(reviews) < wanted:
                raise Stop("Automode pausado: verificação/revisão pendente ou impeditiva. Estado preservado.", STOPPED)
            self.save(phase="commit", human_pending=True)
            return
        stat = staged_diff(self.root, s["base"], 1)[1]
        banner(f"ACEITE · {s['story']} {s['title']} · esforço {s['effort']}")
        show_plan = not needs_plan_stop(self.cfg, s["original_effort"], s["effort"])
        for line in acceptance_lines(s, stat, show_plan):
            print("  " + line)
        wanted, ran = reviewer_count(self.cfg, s["effort"]), len(s.get("reviews") or {})
        if ran < wanted:
            print(f"  revisores: {ran} de {wanted} pedidos (roster desta execução)")
        print("  [a]ceitar+commit  [f]alhou (feedback)  [e]ditar mensagem  [s]air")
        choice = menu("afes")
        if choice == "a":
            self.save(phase="commit", human_pending=False)
        elif choice == "f":
            feedback = ask_text("O que falhou na validação?")
            if feedback:
                self.save(phase="implement", round=0, rerun=[], feedback="Navigator validation failed:\n" + feedback)
        elif choice == "e":
            message = ask_text("Nova mensagem de commit")
            if message:
                s["result"]["commit_message"] = message
                self.save()
        else:
            raise Stop("Parado a pedido. Rode `run` para retomar no aceite.", STOPPED)

    def do_commit(self) -> None:
        s = self.state
        result = s.get("result") or {}
        pending = self.ctx.automode or s.get("human_pending", False)
        route = result.get("validation_route") or s["plan"].get("validation_route") or {}
        self.update_story(fm={"status": "Validated" if pending else "Done",
                              "status_reason": "automode; awaiting human validation" if pending else "",
                              "execution_mode": "automode" if pending else "interactive",
                              "human_validation": "pending" if pending else "accepted"}, sections={
            "Validation Route": render_route(route, s.get("verify")),
            "Review": render_review(s),
            "History": (f"Implemented in automode on {today()}; NOT tested or accepted by the human. "
                        if pending else f"Accepted by the Navigator on {today()}. ")
                       + f"Agents: {', '.join(s['agents']) or 'none'}."})
        message = (result.get("commit_message") or f"Complete {s['story']} {s['title']}").strip()
        trailers = f"Ariad-Story: {s['story']}\nAriad-Agents: {' '.join(s['agents'])}"
        if pending:
            message = "[automode; human validation pending] " + message
            trailers += "\nAriad-Human-Validation: pending"
        try:
            commit(self.root, f"{message}\n\n{trailers}\n")
        except Stop as e:
            self.update_story(fm={"status": "Active", "status_reason": "commit failed"})
            self.save(phase="acceptance")
            raise Stop(f"Commit falhou: {e}. Ajuste e rode `run` de novo (volta ao aceite).", STOPPED)
        print(f"  ✔ commit: {message.splitlines()[0]}")
        code = s["story"]
        batch = s.setdefault("validation_batch", [])
        if not batch:
            s["batch_base"] = s["base"]
        batch.append({"code": code, "path": s["path"], "commit": head(self.root)})
        self.finish()
        self.strong_validation()
        if not pending:
            parent_cadence(self.root, code)

    def strong_validation(self) -> None:
        batch = self.state.get("validation_batch", [])
        if len(batch) < 5:
            return
        if changed_paths(self.root):
            raise Stop("Revisão acumulada exige árvore limpa; preserve suas alterações em commit antes de retomar.", STOPPED)
        role = self.cfg.get("strong_review", {})
        name = role.get("agent", "claude")
        if name not in self.cfg["agents"]:
            raise Stop(f"Revisão de 5 histórias exige o agente {name}; configure [strong_review].")
        agent = {**self.cfg["agents"][name], "bands": [{"from": 1, "to": 10,
                 "model": role.get("model", "opus"),
                 "args": role.get("args", ["--model", "opus", "--effort", "high"])}]}
        cfg = {**self.cfg, "agents": {**self.cfg["agents"], name: agent}}
        ctx = Ctx(self.root, cfg, automode=self.ctx.automode)
        banner(f"Validação acumulada · {len(batch)} histórias · {name} / {agent['bands'][0]['model']}")
        prompt = ("ARIAD ORCHESTRATED | role=reviewer step=strong-validation\n"
                  "Read the development guide and every story listed below. Inspect the FULL cumulative git diff "
                  "and relevant code between the base commit and HEAD. Review integration, regressions, architecture, "
                  "tests and Ariad coherence across all five stories. Do not edit, commit or push. "
                  "Human acceptance remains separate. Return blocking findings for any unresolved failure.\n"
                  f"Base commit: {self.state['batch_base']}\nStories: {json.dumps(batch)}")
        try:
            review = call_agent(ctx, name, "read", 10, "batch", "strong-review", prompt, REVIEW_SCHEMA, stream=True)
        except QuotaHit:
            raise Stop("Cota do modelo forte esgotada; revisão acumulada pendente. Retome com `run`.", STOPPED)
        stamp = dt.datetime.now(dt.timezone.utc)
        report = self.root / "docs/process/worklog/entries" / f"{stamp:%Y-%m-%dT%H%M%SZ}-ariad-strong-review.md"
        related = "\n".join(f"  - {b['code']}" for b in batch)
        findings = "\n".join(f"- [{f.get('severity')}] {f.get('file')}:{f.get('line')} "
                             f"{f.get('issue')} → {f.get('fix')}" for f in review.get("findings") or []) or "- None."
        write(report, f"---\ndate: {stamp:%Y-%m-%dT%H:%M:%SZ}\nauthor: ariad/{name}\nrelated:\n{related}\n"
              "verification:\n  - cumulative strong-model review\n---\n\n# Five-story validation\n\n"
              f"## What changed\n\nReviewed {len(batch)} stories with {agent['bands'][0]['model']}.\n\n"
              "## Why it matters\n\nChecks integration and Ariad coherence; human acceptance remains separate.\n\n"
              f"## Verification\n\nBase: `{self.state['batch_base']}`. Head: `{head(self.root)}`.\n"
              f"Verdict: {review.get('verdict')}.\n\n{findings}\n")
        commit(self.root, "Record strong validation of " + ", ".join(b["code"] for b in batch))
        if review.get("verdict") != "approve" or any(f.get("severity") == "blocking" for f in review.get("findings") or []):
            raise Stop(f"Revisão forte encontrou impedimentos. Corrija antes de continuar. Relatório: {report}", STOPPED)
        self.save(validation_batch=[], batch_base="")

    def finish(self) -> None:
        keep = {k: self.state[k] for k in ("roster", "exhausted", "validation_batch", "batch_base") if k in self.state}
        self.state.clear()
        self.state.update(keep)
        save_state(self.root, self.state)


def parent_cadence(root: Path, code: str) -> None:
    """Asks to close the Delivery Story, then the Value, once all their children are done or dropped."""
    items = load_roadmap(root)
    by_code = {i.code: i for i in items}
    closed = []
    parent = parent_code(code)
    while parent in by_code:
        item = by_code[parent]
        kids = children(items, parent)
        if item.status in ("Done", "Dropped") or not kids or any(k.status not in ("Done", "Dropped") for k in kids):
            break
        done = sum(k.status == "Done" for k in kids)
        if not ask(f'  Fechar {parent} "{item.title}" ({done}/{len(kids)} Done)? [s/n] ').lower().startswith("s"):
            break
        path = root / item.path
        write(path, set_frontmatter(read(path), {"status": "Done", "status_reason": "", "updated": today()}))
        item.status = "Done"
        closed.append(item)
        parent = parent_code(parent)
    if closed:
        commit(root, "Close " + ", ".join(f"{i.code} {i.title}" for i in closed)
               + f"\n\nAriad-Story: {closed[0].code}\n")
        kinds = {"Delivery Story": "DS: MINOR", "Value": "CV: MAJOR"}
        print("  Possível fronteira de release (" + ", ".join(kinds.get(i.level, i.level) for i in closed)
              + "). Registre no CHANGELOG quando decidir.")


def dry_run(ctx: Ctx, state: dict, only: str | None) -> int:
    roster = state.get("roster") or {"writer": ctx.cfg["roles"]["writer"], "reviewers": ctx.cfg["roles"]["reviewers"]}
    s = state if state.get("story") else None
    if s is None:
        item = next_story(load_roadmap(ctx.root), only)
        if item is None:
            print("Nenhuma história Planned/Active.")
            return OK
        s = {"story": item.code, "path": item.path.as_posix(), "title": item.title, "level": item.level,
             "effort": item.effort or 5, "phase": "plan", "writer": item.writer or roster["writer"],
             "plan": {}, "feedback": "", "resume": False, "base": head(ctx.root)}
    if s["phase"] in ("plan", "plan_checkpoint"):
        name, role_args, prompt, schema = s["writer"], "read", prompt_plan(s, ctx.cfg), PLAN_SCHEMA
    elif s["phase"] in ("implement", "verify"):
        name, role_args, prompt, schema = s["writer"], "write", prompt_implement(s, ctx.cfg), IMPLEMENT_SCHEMA
    else:
        name = (roster["reviewers"] or [s["writer"]])[0]
        role_args, prompt, schema = "read", prompt_review(s, ctx.cfg, "(diff)"), REVIEW_SCHEMA
    agent = ctx.cfg["agents"][name]
    call = build_call(name, agent, role_args, band_for(agent, s["effort"]), prompt, project=ctx.root,
                      schema=schema, files=ctx.logs / "dry-run")
    print(f"{s['story']} · fase {s['phase']} · {call.label}")
    print("$ " + subprocess.list2cmdline(call.cmd))
    print(call.stdin if call.stdin is not None else "(prompt no argumento)")
    return OK


def cmd_run(args) -> int:
    root = project_root()
    ctx = Ctx(root, load_config(root / ".ariad" / "ariad.toml"))
    ctx.automode = getattr(args, "automode", False)
    if ctx.automode:
        ctx.cfg["project"]["min_available"] = 0
    if not is_repo(root):
        raise Stop("Projeto sem git próprio. Rode `init` (oferece git init) e faça o commit inicial.")
    state = load_state(root)
    if args.dry_run:
        return dry_run(ctx, state, args.story)
    with Lock(root):
        check_cli_versions(ctx.cfg)
        ctx.usage = check_agents(ctx.cfg)
        roster = (default_roster(ctx.cfg, ctx.usage, state.get("roster")) if ctx.automode
                  else choose_roster(ctx.cfg, ctx.usage, state.get("roster")))
        if not roster["writer"]:
            raise Stop("Nenhum escritor disponível. Estado preservado.", STOPPED)
        state.update(roster=roster, exhausted={})
        if state.get("story") and state.get("writer") not in (roster["writer"], *roster["reviewers"]):
            state["writer"] = roster["writer"]
        if state.get("phase") == "implement":
            state["resume"] = True
        save_state(root, state)
        runner, done = Runner(ctx, state), 0
        runner.strong_validation()
        while True:
            if not state.get("story"):
                if (args.max and done >= args.max) or (args.story and done):
                    return OK
                item = next_story(load_roadmap(root), args.story)
                if item is None:
                    print("Nenhuma história Planned/Active" + (f" com código {args.story}." if args.story else "."))
                    return OK
                if done and not ctx.automode:
                    if not ask(f"  Quer iniciar outra história agora ({item.code})? [s/N] ").lower().startswith("s"):
                        return OK
                runner.pull(item)
            runner.advance()
            done += 1


# ==== Human validation ====

def cmd_validate(args) -> int:
    """Accept or return one automode story, without implying acceptance of the others."""
    root = project_root()
    with Lock(root):
        state = load_state(root)
        pending = [i for i in load_roadmap(root) if i.is_story and i.status == "Validated" and
                   parse_frontmatter(read(root / i.path)).get("human_validation") == "pending"]
        if args.story:
            pending = [i for i in pending if i.code == args.story]
        if not pending:
            print("Nenhuma história pendente de validação humana.")
            return OK
        for item in sorted(pending, key=lambda i: code_key(i.code)):
            path = root / item.path
            text = read(path)
            original = text
            if item.path.as_posix() in changed_paths(root):
                raise Stop(f"{item.code} tem alterações locais; preserve-as antes de validar esta história.", STOPPED)
            banner(f"Validação humana · {item.code} · {item.title}")
            print(text)
            print("  [a]ceitar  [f]alhou  [p]ular  [s]air")
            choice = menu("afps")
            if choice == "s":
                return OK
            if choice == "p":
                continue
            if choice == "f":
                feedback = ask_text("O que falhou?")
                if not feedback:
                    continue
                text = set_section(text, "Human Validation", f"Failed on {today()}:\n\n{feedback}")
                updates = {"status": "Planned", "human_validation": "failed", "status_reason": "human validation failed"}
            else:
                text = set_section(text, "Human Validation", f"Tested and accepted by the Navigator on {today()}.")
                updates = {"status": "Done", "human_validation": "accepted", "status_reason": ""}
            write(path, set_frontmatter(text, {**updates, "updated": today()}))
            try:
                git(root, "commit", "--only", "-q", "-F", "-", "--", item.path.as_posix(),
                    input=f"Human validation {updates['human_validation']}: {item.code}\n")
            except Stop:
                write(path, original)
                raise
            if choice == "a" and not state.get("story") and not changed_paths(root):
                parent_cadence(root, item.code)
            if args.story:
                return OK
            if not ask("  Quer validar outra história agora? [s/N] ").lower().startswith("s"):
                return OK
    return OK

# ==== Setup ====

SETUP_ROUNDS = 4
SETUP_DOCS = {"briefing": "docs/project/briefing.md", "principles": "docs/product/principles.md",
              "dev": "docs/process/development-guide.md"}


def doc_is_template(root: Path, rel: str, templates: Path) -> bool:
    path, template = root / rel, templates / rel
    return not path.is_file() or (template.is_file() and read(path) == read(template))


def existing_docs(root: Path, templates: Path) -> str:
    return "\n".join(f"--- {rel} (Navigator-owned; keep consistent) ---\n{read(root / rel)[:4000]}"
                     for rel in SETUP_DOCS.values() if not doc_is_template(root, rel, templates))


def qa_text(transcript: list) -> str:
    return "\n".join(f"Q: {q}\nA: {a}" for q, a in transcript)


def prompt_interview(round_no: int, summary: str, transcript: list, existing: str) -> str:
    lines = [f"ARIAD ORCHESTRATED | role=brain step=interview round={round_no}/{SETUP_ROUNDS}",
             "You configure Ariad for this repository: project briefing, product principles, development "
             "commands, and a delivery roadmap. Do not edit any file."]
    if round_no == 1:
        lines.append("Explore the repository read-only first: README, manifests, top-level layout, tests, docs/. "
                     "context_summary: at most 250 words about what you found.")
    else:
        lines += ["Context summary from round 1: " + summary, "Do not explore again; context_summary may be empty."]
    if transcript:
        lines.append("Answers so far:\n" + qa_text(transcript))
    if existing:
        lines.append("Existing project docs:\n" + existing)
    lines.append("Ask only what you cannot infer and what changes the roadmap, scope, or priorities: at most 5 "
                 "questions, each with 2-4 short options and the letter of your recommended option. Ask for the "
                 "project docs language when unknown. Return questions=[] when you know enough to propose. "
                 "Write the questions in Brazilian Portuguese.")
    return "\n".join(lines)


def prompt_propose(summary: str, transcript: list, existing: str, previous: dict | None = None,
                   feedback: str = "") -> str:
    lines = ["ARIAD ORCHESTRATED | role=brain step=propose",
             "Produce the Ariad setup proposal for this repository. Do not edit any file.",
             "Context summary: " + summary]
    if transcript:
        lines.append("Navigator answers:\n" + qa_text(transcript))
    if existing:
        lines.append("Existing project docs:\n" + existing)
    lines += [
        "Roadmap rules: codes CV<n>, CV<n>.DS<m>, CV<n>.DS<m>.US<k> or CV<n>.DS<m>.TS<k>; level is Value, "
        "Delivery Story, User Story, or Technical Story and matches the code; every parent exists.",
        "Each Delivery Story has a done_condition. Each User Story has observable acceptance "
        "(Given/When/Then/And). A Technical Story is internal capability that enables a User Story.",
        f"effort only for User and Technical Stories (0 for Values and Delivery Stories); {EFFORT_SCALE}.",
        "order: pull order across all stories starting at 1, enabling Technical Stories first. Split any story "
        "at effort 9 or 10. Keep the first Value small enough to deliver soon. writer: empty unless the "
        "Navigator asked for a specific agent.",
        "dev.verify: shell commands that prove the project still works (tests, build); empty when none exist.",
        "language: the docs language the Navigator chose (default en). Write every text value in that language."]
    if previous:
        lines.append("Previous proposal: " + json.dumps(previous, ensure_ascii=False))
    if feedback:
        lines.append("Navigator feedback on it: " + feedback)
    return "\n".join(lines)


def ask_question(q: dict) -> str:
    letters = "abcd"
    options = (q.get("options") or [])[:4]
    print(f"\n  {q.get('id', '')}. {q.get('text', '')}")
    for letter, option in zip(letters, options):
        print(f"    {letter}) {option}")
    rec = str(q.get("recommended", "")).strip()
    rec_text = next((o for letter, o in zip(letters, options) if rec.lower() in (letter, o.lower())), rec)
    if rec_text:
        print(f"    recomendado: {rec_text}" + (f" ({q['why']})" if q.get("why") else ""))
    while True:
        answer = ask("  › ")
        if not answer:
            if rec_text:
                return rec_text
            continue
        if len(answer) == 1 and answer.lower() in letters[:len(options)]:
            return options[letters.index(answer.lower())]
        return answer


def validate_proposal(proposal: dict, existing: set[str]) -> list[str]:
    errors, seen = [], set()
    items = proposal.get("roadmap") or []
    codes = {str(i.get("code", "")) for i in items} | existing
    for item in items:
        code = str(item.get("code", ""))
        if not CODE_RE.match(code):
            errors.append(f"código inválido: {code!r}")
            continue
        if code in seen:
            errors.append(f"código repetido: {code}")
        seen.add(code)
        if item.get("level") != level_for(code):
            errors.append(f"{code}: level deve ser {level_for(code)}")
        if parent_code(code) and parent_code(code) not in codes:
            errors.append(f"{code}: pai {parent_code(code)} não existe")
        effort = item.get("effort")
        if level_for(code) in STORY_LEVELS and (isinstance(effort, bool) or not isinstance(effort, int)
                                                or not 1 <= effort <= 10):
            errors.append(f"{code}: effort deve ser inteiro de 1 a 10")
    return errors


def show_proposal(proposal: dict, existing: set[str], errors: list[str]) -> None:
    banner("PROPOSTA DE SETUP")
    print(f"  idioma dos docs: {proposal.get('language', '')}")
    print(f"  verify: {', '.join((proposal.get('dev') or {}).get('verify') or []) or '-'}")
    valid = [i for i in proposal.get("roadmap") or [] if CODE_RE.match(str(i.get("code", "")))]
    for item in sorted(valid, key=lambda i: code_key(i["code"])):
        effort = f"  esforço {item['effort']}" if item.get("effort") else ""
        order = f"  #{item['order']}" if item.get("order") else ""
        kept = "  (mantido)" if item["code"] in existing else ""
        print(f"  {'  ' * item['code'].count('.')}{item['code']} {item.get('title', '')}{effort}{order}{kept}")
    for q in proposal.get("open_questions") or []:
        print(f"  pergunta aberta: {q.get('title', '')}")
    for error in errors:
        print(f"  ERRO: {error}")


def edit_proposal(root: Path, proposal: dict) -> dict:
    path = root / ".ariad" / "setup.json"
    write(path, json.dumps(proposal, ensure_ascii=False, indent=2))
    while True:
        ask(f"  Edite {path} e tecle Enter para recarregar: ")
        loaded = _loads(read(path))
        if isinstance(loaded, dict):
            return loaded
        print("  JSON inválido; corrija e tecle Enter.")


def bullets(values: list) -> str:
    return "\n".join(f"- {v}" for v in values if v)


def fill_doc(template_text: str, sections: dict) -> str:
    for name, content in sections.items():
        template_text = set_section(template_text, name, content or "(none yet)")
    return template_text


def setup_docs(proposal: dict) -> dict:
    """Section contents for each file in SETUP_DOCS."""
    b, d = proposal.get("briefing") or {}, proposal.get("dev") or {}
    commands = d.get("commands") or {}
    glossary = "\n".join(f"- **{g.get('term', '')}**: {g.get('meaning', '')}" for g in b.get("glossary") or [])
    command_block = "\n".join(f"# {label}\n{commands.get(key) or '(none)'}" for key, label in
                              (("install", "install"), ("test", "test"), ("lint", "lint or format"),
                               ("run", "run locally")))
    notes = bullets(d.get("notes") or [])
    return {
        "briefing": {"Purpose": b.get("purpose", ""), "Current State": b.get("current_state", ""),
                     "Architecture Premises": bullets(b.get("architecture") or []),
                     "Product Premises": bullets(b.get("product") or []),
                     "Constraints": bullets(b.get("constraints") or []), "Glossary": glossary},
        "principles": {"Principles": "\n\n".join(f"### {p.get('name', '')}\n\n{p.get('text', '')}"
                                                 for p in proposal.get("principles") or [])},
        "dev": {"Commands": f"```bash\n{command_block}\n```" + (f"\n\n{notes}" if notes else ""),
                "Verification": bullets([f"`{v}`" for v in d.get("verify") or []])},
    }


def render_item(item: dict) -> str:
    level = item["level"]
    fm = {"code": item["code"], "level": level, "status": "Planned", "status_reason": "", "updated": today()}
    if level in STORY_LEVELS:
        fm.update(effort=item.get("effort", ""), effort_reason=item.get("effort_reason", ""),
                  order=item.get("order", ""), writer=item.get("writer", ""))
    text = "---\n" + "\n".join(f"{k}: {v}".rstrip() for k, v in fm.items()) + "\n---\n\n"
    text += f"# {item.get('title') or item['code']}\n\n## Intent\n\n{item.get('intent', '')}\n"
    if level in STORY_LEVELS:
        a = item.get("acceptance") or {}
        text += (f"\n## Acceptance\n\nGiven {a.get('given', '')}\nWhen {a.get('when', '')}\n"
                 f"Then {a.get('then', '')}\n" + (f"And {a['and']}\n" if a.get("and") else ""))
    elif item.get("done_condition"):
        text += f"\n## Done Condition\n\n{item['done_condition']}\n"
    return text


def render_decision(q: dict) -> str:
    return (f"---\nstatus: Open\nraised: {today()}\ndecided:\ndeciders:\n  - Navigator\n---\n\n"
            f"# {q.get('title') or 'Open question'}\n\n## Question\n\n{q.get('question', '')}\n\n"
            "## Decision\n\nPending\n")


def write_setup(root: Path, cfg_path: Path, proposal: dict, existing: set[str], templates: Path) -> list[str]:
    written = []
    for key, sections in setup_docs(proposal).items():
        rel = SETUP_DOCS[key]
        if doc_is_template(root, rel, templates):
            write(root / rel, fill_doc(read(templates / rel), sections))
            written.append(rel)
    folders = {i.code: (root / i.path).parent for i in load_roadmap(root)}
    for item in sorted(proposal.get("roadmap") or [], key=lambda i: code_key(i["code"])):
        code = item["code"]
        if code in existing:
            continue
        parent = folders.get(parent_code(code), root / ROADMAP)
        folder = parent / f"{code.lower().replace('.', '-')}-{slug(item.get('title', ''))}"
        write(folder / "index.md", render_item(item))
        folders[code] = folder
        written.append((folder / "index.md").relative_to(root).as_posix())
    records = root / "docs/project/decisions/records"
    for q in proposal.get("open_questions") or []:
        base = f"{utc_stamp()}-{slug(q.get('title') or 'question')}"
        path, n = records / f"{base}.md", 2
        while path.exists():
            path, n = records / f"{base}-{n}.md", n + 1
        write(path, render_decision(q))
        written.append(path.relative_to(root).as_posix())
    set_toml_value(cfg_path, "project", "language", proposal.get("language") or "en")
    set_toml_value(cfg_path, "project", "verify", (proposal.get("dev") or {}).get("verify") or [])
    written.append(cfg_path.relative_to(root).as_posix())
    return written


def brain_call(ctx: Ctx, roster: dict, step: str, prompt: str, schema: dict) -> dict:
    while True:
        try:
            return call_agent(ctx, roster["brain"], "read", ctx.cfg["roles"]["brain_effort"], "setup", step,
                              prompt, schema, stream=True)
        except QuotaHit as hit:
            roster["brain"] = replace_agent(ctx, "brain", hit.agent, hit.reset)


def cmd_setup(args) -> int:
    root = project_root()
    cfg_path = root / ".ariad" / "ariad.toml"
    ctx = Ctx(root, load_config(cfg_path))
    templates = templates_dir()
    if not is_repo(root):
        raise Stop("Projeto sem git próprio. Rode `init` primeiro.")
    with Lock(root):
        state = load_state(root)
        if state.get("story"):
            raise Stop(f"História {state['story']} ativa; termine-a com `run` antes do setup.", STOPPED)
        check_cli_versions(ctx.cfg)
        ctx.usage = check_agents(ctx.cfg)
        roster = choose_roster(ctx.cfg, ctx.usage, state.get("roster"), brain_only=True)
        existing = existing_docs(root, templates)
        summary, transcript = "", []
        for round_no in range(1, SETUP_ROUNDS + 1):
            answer = brain_call(ctx, roster, "interview",
                                prompt_interview(round_no, summary, transcript, existing), INTERVIEW_SCHEMA)
            summary = summary or answer.get("context_summary", "")
            questions = (answer.get("questions") or [])[:5]
            if not questions:
                break
            transcript += [(q.get("text", ""), ask_question(q)) for q in questions]
        proposal = brain_call(ctx, roster, "propose", prompt_propose(summary, transcript, existing), PROPOSE_SCHEMA)
        codes = {i.code for i in load_roadmap(root)}
        while True:
            errors = validate_proposal(proposal, codes)
            show_proposal(proposal, codes, errors)
            print("  [a]provar  [e]ditar  [r]efazer  [s]air")
            choice = menu("aers")
            if choice == "a" and not errors:
                break
            if choice == "a":
                print("  Corrija os erros antes de aprovar: [e]ditar ou [r]efazer.")
            elif choice == "e":
                proposal = edit_proposal(root, proposal)
            elif choice == "r":
                feedback = ask_text("O que mudar na proposta?")
                if feedback:
                    proposal = brain_call(ctx, roster, "propose",
                                          prompt_propose(summary, transcript, existing, proposal, feedback),
                                          PROPOSE_SCHEMA)
            else:
                raise Stop("Setup interrompido; nada foi gravado.", STOPPED)
        for rel in write_setup(root, cfg_path, proposal, codes, templates):
            print(f"  + {rel}")
        state["roster"] = roster
        save_state(root, state)
        pending = len(changed_paths(root))
        if ask(f'  Commit "Set up Ariad docs and roadmap" ({pending} arquivos)? [s/n] ').lower().startswith("s"):
            label = agent_label(ctx.cfg, roster["brain"], ctx.cfg["roles"]["brain_effort"])
            commit(root, f"Set up Ariad docs and roadmap\n\nAriad-Agents: brain={label}\n")
            print("  ✔ commit feito")
    return OK


# ==== Check ====

def check_one(name: str, agent: dict, role_args: str, band: dict, timeout: float) -> tuple[str, str]:
    """Runs a tiny task with one agent and band in a temporary folder; returns (status, note)."""
    with tempfile.TemporaryDirectory(prefix=f"ariad-check-{name}-", ignore_cleanup_errors=True) as tmp:
        work = Path(tmp)
        writes = role_args == "write"
        prompt = ("ARIAD ORCHESTRATED | role=check step=check\n"
                  + ("Create the file check.txt in the current folder containing only OK." if writes
                     else "Do not edit any file.")
                  + "\nFinal answer: only one JSON object shaped like " + json.dumps(skeleton(CHECK_SCHEMA)))
        try:
            call = build_call(name, agent, role_args, band, prompt, project=work, schema=CHECK_SCHEMA,
                              files=work / "call")
        except Stop as e:
            return "FALHA", str(e)
        log = SCRIPT_DIR / "logs" / f"{local_stamp()}_check_{name}_{role_args}_{band['from']}-{band['to']}.log"
        start = time.monotonic()
        result = run_process(call.cmd, call.stdin, work, timeout, log)
        output = result.output
        if call.out_file and call.out_file.is_file() and read(call.out_file).strip():
            output = read(call.out_file)
        answered = not missing_keys(extract_json(output), CHECK_SCHEMA)
        wrote = (work / "check.txt").is_file()
        took = f"{time.monotonic() - start:.0f}s · log {log.name}"
    if result.timed_out:
        return "FALHA", f"tempo esgotado · {took}"
    if not answered and result.code != 0:
        return "FALHA", ("cota/limite" if hit_quota(agent, result.output) else f"código {result.code}") + f" · {took}"
    if not answered:
        return "ATENCAO", f"sem JSON na resposta · {took}"
    if writes and not wrote:
        return "ATENCAO", f"respondeu, mas não criou o arquivo · {took}"
    return "OK", took


def cmd_check(args) -> int:
    cfg = load_config(SCRIPT_DIR / "ariad.toml")
    check_cli_versions(cfg)
    names = args.agents or list(cfg["agents"])
    unknown = [n for n in names if n not in cfg["agents"]]
    if unknown:
        raise Stop(f"Agente(s) desconhecido(s): {', '.join(unknown)}. Configurados: {', '.join(cfg['agents'])}.")
    rows = []
    for name in names:
        agent = cfg["agents"][name]
        middle = agent["bands"][len(agent["bands"]) // 2]
        for role_args, band in [("write", b) for b in agent["bands"]] + [("read", middle)]:
            label = f"{role_args} {band['from']}-{band['to']}"
            print(f"  · check {name} {label} ({band_label(band)})")
            rows.append((name, label, *check_one(name, agent, role_args, band, args.timeout)))
    banner("Resultado do check")
    for name, label, status, note in rows:
        print(f"  {status:<8} {name:<8} {label:<10} {note}")
    print("\n  Cada linha gasta cota real do agente; rode só quando precisar.")
    return OK if all(row[2] == "OK" for row in rows) else ERROR


# ==== CLI ====

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ariad", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="instala os templates Ariad no projeto")
    p.add_argument("--dry-run", action="store_true")
    sub.add_parser("setup", help="entrevista, roadmap e esforço por história")
    p = sub.add_parser("run", help="executa histórias com escritor, revisores e checkpoints humanos")
    p.add_argument("--story", metavar="CODIGO")
    p.add_argument("--automode", action="store_true", help="continua com validação humana pendente")
    p.add_argument("--max", type=int, default=0, metavar="N")
    p.add_argument("--dry-run", action="store_true")
    sub.add_parser("status", help="roadmap e fase atual")
    p = sub.add_parser("validate", help="valida histórias feitas em automode, uma a uma")
    p.add_argument("--story", metavar="CODIGO")
    sub.add_parser("agents", help="disponibilidade dos agentes")
    p = sub.add_parser("check", help="testa as CLIs dos agentes em cada faixa de esforço")
    p.add_argument("agents", nargs="*")
    p.add_argument("--timeout", type=float, default=180)
    p = sub.add_parser("export", help="gera o zip do sidecar")
    p.add_argument("--out")
    args = parser.parse_args(argv)
    handler = globals().get(f"cmd_{args.command}")
    try:
        if handler is None:
            raise Stop(f"Comando '{args.command}' ainda não implementado.")
        return handler(args)
    except Stop as e:
        print(f"\n■ {e}")
        return e.code
    except KeyboardInterrupt:
        print("\n■ Interrompido. O estado foi preservado; rode o mesmo comando para retomar.")
        return STOPPED


if __name__ == "__main__":
    sys.exit(main())
