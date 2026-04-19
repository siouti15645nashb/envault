"""Export audit log to various formats."""
import json
import csv
import io
from pathlib import Path
from typing import List, Dict

from envault.audit import get_log

SUPPORTED_FORMATS = ["json", "csv", "text"]


class AuditExportError(Exception):
    pass


def _format_json(entries: List[Dict]) -> str:
    return json.dumps(entries, indent=2)


def _format_csv(entries: List[Dict]) -> str:
    if not entries:
        return ""
    out = io.StringIO()
    fields = ["timestamp", "action", "key", "details"]
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for entry in entries:
        writer.writerow({f: entry.get(f, "") for f in fields})
    return out.getvalue()


def _format_text(entries: List[Dict]) -> str:
    lines = []
    for e in entries:
        ts = e.get("timestamp", "")
        action = e.get("action", "")
        key = e.get("key", "")
        details = e.get("details", "")
        line = f"[{ts}] {action}"
        if key:
            line += f" | key={key}"
        if details:
            line += f" | {details}"
        lines.append(line)
    return "\n".join(lines)


def export_audit_log(vault_dir: str, fmt: str = "json") -> str:
    if fmt not in SUPPORTED_FORMATS:
        raise AuditExportError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
    entries = get_log(vault_dir)
    if fmt == "json":
        return _format_json(entries)
    elif fmt == "csv":
        return _format_csv(entries)
    else:
        return _format_text(entries)


def export_audit_log_to_file(vault_dir: str, output_path: str, fmt: str = "json") -> int:
    content = export_audit_log(vault_dir, fmt)
    Path(output_path).write_text(content, encoding="utf-8")
    entries = get_log(vault_dir)
    return len(entries)
