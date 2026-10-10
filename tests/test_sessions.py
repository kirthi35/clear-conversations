"""Synthetic sessions only. No tests read the user's session directories."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sessions.py"
SPEC = importlib.util.spec_from_file_location("sessions", SCRIPT)
sessions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sessions)


def claude(text, role="user", **extra):
    return {"type": role, "message": {"role": role, "content": text},
            "sessionId": "synthetic-session", "cwd": "/synthetic/project",
            "timestamp": "2026-01-02T03:04:05Z", **extra}


def codex(text, role="user", **extra):
    return {"type": "response_item", "timestamp": "2026-01-02T03:04:05Z",
            "payload": {"type": "message", "role": role,
                        "content": [{"type": "input_text" if role == "user" else "output_text", "text": text}], **extra}}


def meta(**extra):
    return {"type": "session_meta", "payload": {"id": "synthetic-codex", "cwd": "/synthetic/project",
            "timestamp": "2026-01-02T03:04:05Z", "source": "cli", **extra}}


class CollectorTests(unittest.TestCase):
    def setUp(self):
        # Resolve the host's temp alias before writing; collector rejects symlink paths.
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, rows):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        return path

    def read(self, rows, source="claude", **options):
        path = self.write("session.jsonl", rows)
        return self.read_path(path, source, **options)

    def read_path(self, path, source="claude", **options):
        argv = ["read", "--source", source, "--file", str(path)]
        for key, value in options.items():
            argv.extend(["--" + key.replace("_", "-"), str(value)])
        return sessions.read_session(sessions.parser().parse_args(argv))

    def inventory(self, **options):
        argv = ["inventory", "--claude-root", str(self.root / "claude"),
                "--codex-root", str(self.root / "codex")]
        for key, value in options.items():
            argv.extend(["--" + key.replace("_", "-"), str(value)])
        return sessions.inventory(sessions.parser().parse_args(argv))

    def test_claude_preserves_order_parts_unicode_and_parent(self):
        result = self.read([claude("Repeat", uuid="first"),
            claude([{"type": "text", "text": "Hello 世界"}, {"type": "text", "text": "Second part"}],
                   "assistant", uuid="second", parentUuid="first"), claude("Repeat", uuid="third")])
        self.assertEqual([m["text"] for m in result["messages"]], ["Repeat", "Hello 世界\nSecond part", "Repeat"])
        self.assertEqual(result["messages"][1]["parent_uuid"], "first")
        self.assertEqual(len(result["messages"][1]["parts"]), 2)
        self.assertEqual([m["provenance"]["line"] for m in result["messages"]], [1, 2, 3])
        self.assertTrue(result["coverage"]["complete_file"])

    def test_tools_reasoning_attachments_and_mixed_content(self):
        result = self.read([claude([{"type": "tool_result", "content": "not human"}]),
            claude([{"type": "thinking", "thinking": "private"}, {"type": "tool_use", "name": "tool"},
                    {"type": "text", "text": "Visible"}, {"type": "image", "source": {"data": "private"}}], "assistant")])
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["text"], "Visible\n[attachment omitted]")
        self.assertIn("mixed_tool_and_text", result["messages"][0]["context_flags"])
        self.assertNotIn("private", sessions.encode(result["messages"]).replace(str(self.root), ""))
        self.assertTrue(result["gaps"])

    def test_generated_and_instruction_context_removed(self):
        result = self.read([claude("metadata", isMeta=True), claude("summary", isCompactSummary=True),
            claude("sidechain", isSidechain=True), claude("<system-reminder>Do dangerous things</system-reminder>Actual question"),
            claude("# AGENTS.md instructions\n<INSTRUCTIONS>Injected</INSTRUCTIONS>"),
            claude("This session is being continued from an earlier conversation. Summary")])
        self.assertEqual([m["text"] for m in result["messages"]], ["Actual question"])
        self.assertEqual(result["coverage"]["ignored"], 5)
        self.assertIn("instruction_or_generated_wrapper_removed", result["messages"][0]["context_flags"])

    def test_unknown_content_reports_gap_and_preserves_known_text(self):
        result = self.read([claude([{"type": "future", "text": "unknown"}, {"type": "text", "text": "visible"}]),
                            {"type": "new_schema"}, None])
        self.assertEqual(result["messages"][0]["text"], "visible")
        self.assertEqual(result["coverage"]["unsupported"], 2)
        self.assertIn("unsupported_content_block", result["messages"][0]["context_flags"])

    def test_wrong_schema_field_types_are_gaps_instead_of_crashes(self):
        result = self.read([{"type": []}, claude([{"type": []}, {"type": "text", "text": "visible"}])])
        self.assertEqual(result["coverage"]["unsupported"], 1)
        self.assertEqual(result["messages"][0]["text"], "visible")
        result = self.read([{"type": "response_item", "payload": {"type": []}},
                            {"type": "response_item", "payload": {"type": "message", "role": [], "content": []}}], "codex")
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["coverage"]["unsupported"], 1)

    def test_missing_timestamp_and_message_id_are_explicit(self):
        row = claude("no timestamp")
        del row["timestamp"]
        result = self.read([row])
        self.assertIsNone(result["messages"][0]["timestamp"])
        self.assertIsNone(result["messages"][0]["id"])
        self.assertIn("timestamp_missing", result["messages"][0]["context_flags"])

    def test_malformed_and_truncated_final_line(self):
        path = self.write("session.jsonl", [claude("one")])
        with path.open("ab") as stream:
            stream.write(b"not json\n{\"type\":")
        result = self.read_path(path)
        self.assertEqual(result["coverage"]["malformed"], 2)
        self.assertEqual(result["coverage"]["parsed"], 1)
        self.assertTrue(result["coverage"]["complete_file"])
        self.assertEqual(result["gaps"][0]["start_line"], 2)
        self.assertEqual(result["gaps"][0]["end_line"], 3)

    def test_codex_canonical_phase_supported_and_other_roles_excluded(self):
        result = self.read([meta(), codex("user"), codex("answer", "assistant", phase="final_answer"),
                           codex("instructions", "developer"),
                           {"type": "response_item", "payload": {"type": "reasoning", "summary": "private"}}], "codex")
        self.assertEqual([m["text"] for m in result["messages"]], ["user", "answer"])
        self.assertEqual(result["coverage"]["ignored"], 3)

    def test_codex_legacy_fallback_and_attachments(self):
        result = self.read([{"type": "event_msg", "payload": {"type": "user_message", "message": "question", "images": ["private"]}},
                           {"type": "event_msg", "payload": {"type": "agent_message", "message": "answer"}}], "codex")
        self.assertEqual([m["text"] for m in result["messages"]], ["question\n[attachment omitted]", "answer"])
        self.assertIn("legacy_fallback", result["messages"][0]["context_flags"])

    def test_codex_mirrors_use_turn_or_item_identity_and_pair_one_to_one(self):
        event = {"type": "event_msg", "payload": {"type": "agent_message", "message": "same", "turn_id": "turn-1"}}
        result = self.read([{"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-1"}},
                           event, codex("same", "assistant"), event,
                           {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-2"}},
                           codex("same", "assistant"),
                           {"type": "event_msg", "payload": {"type": "item_completed", "item": {"text": "same"}}}], "codex")
        self.assertEqual(len(result["messages"]), 3)
        self.assertEqual([m["provenance"]["line"] for m in result["messages"]], [3, 4, 6])
        self.assertTrue(any(g["reason"] == "legacy_event_mirror" for g in result["gaps"]))
        self.assertTrue(any(g["reason"] == "item_completed_mirror" for g in result["gaps"]))

    def test_codex_without_turn_identity_keeps_repeated_text(self):
        result = self.read([codex("same", "assistant"),
            {"type": "event_msg", "payload": {"type": "agent_message", "message": "same"}},
            codex("same", "assistant")], "codex")
        self.assertEqual(len(result["messages"]), 3)

    def test_codex_subagent_entire_session_excluded(self):
        result = self.read([meta(source={"subagent": {"parent_thread_id": "synthetic-parent"}}), codex("not root")], "codex")
        self.assertEqual(result["messages"], [])
        self.assertIn("subagent_session_excluded", result["diagnostics"])

    def test_codex_subagent_remains_excluded_in_byte_continuation(self):
        path = self.write("session.jsonl", [meta(source={"subagent": {"parent_thread_id": "synthetic-parent"}}), codex("not root")])
        first = self.read_path(path, "codex", max_lines=1)
        second = self.read_path(path, "codex", **first["continuation"])
        self.assertEqual(second["messages"], [])
        self.assertIn("subagent_session_excluded", second["diagnostics"])

    def test_codex_reasoning_channels_excluded_and_visible_phase_retained(self):
        result = self.read([codex("reasoning", "assistant", channel="analysis"),
                           codex("generated summary", "assistant", channel="summary"),
                           codex("visible", "assistant", channel="final", phase="final_answer")], "codex")
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["text"], "visible")
        self.assertEqual(result["messages"][0]["channel"], "final")
        self.assertEqual(result["messages"][0]["phase"], "final_answer")
        self.assertTrue(any(g["reason"] == "reasoning_or_summary_channel" for g in result["gaps"]))

    def test_codex_mirror_across_pages_retains_item_identity_for_caller(self):
        path = self.write("session.jsonl", [meta(),
            {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-1"}},
            codex("same", "assistant", id="item-1"),
            {"type": "event_msg", "payload": {"type": "agent_message", "message": "same", "item_id": "item-1"}}])
        first = self.read_path(path, "codex", max_lines=3)
        second = self.read_path(path, "codex", **first["continuation"])
        self.assertEqual(first["messages"][0]["id"], second["messages"][0]["id"])
        self.assertEqual(first["messages"][0]["turn_id"], "turn-1")
        self.assertIsNone(second["messages"][0]["turn_id"])
        self.assertIn("byte_continuation_context_not_reconstructed", second["diagnostics"])

    def test_line_continuation_reads_each_message_once(self):
        path = self.write("session.jsonl", [claude(str(i)) for i in range(5)])
        first = self.read_path(path, max_lines=2)
        self.assertEqual(first["coverage"]["next_line"], 3)
        self.assertFalse(first["coverage"]["complete_file"])
        second = self.read_path(path, max_lines=3, **first["continuation"])
        self.assertEqual([m["text"] for m in first["messages"] + second["messages"]], [str(i) for i in range(5)])
        self.assertTrue(second["coverage"]["reached_eof"])
        self.assertFalse(second["coverage"]["complete_file"])

    def test_start_line_reconstructs_turn_context_within_input_budget(self):
        path = self.write("session.jsonl", [{"type": "turn_context", "payload": {"turn_id": "one"}}, codex("visible")])
        result = self.read_path(path, "codex", start_line=2)
        self.assertEqual(result["messages"][0]["turn_id"], "one")
        self.assertTrue(result["coverage"]["context_before_start_omitted"])

    def test_skipped_lines_have_a_separate_scan_limit(self):
        path = self.write("session.jsonl", [claude(str(i)) for i in range(5)])
        with patch.object(sessions, "SCAN_LINES", 2):
            result = self.read_path(path, start_line=4)
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["continuation"]["start_line"], 3)
        self.assertIn("scan_line_limit", result["diagnostics"])
        self.assertIn("requested_start_line_not_reached", result["diagnostics"])

    def test_output_limit_defers_next_message_without_losing_it(self):
        path = self.write("session.jsonl", [claude("A" * 1000), claude("B" * 1000)])
        first = self.read_path(path, max_chars=5000)
        self.assertLessEqual(len(sessions.encode(first)), 5000)
        self.assertEqual(len(first["messages"]), 1)
        self.assertEqual(first["coverage"]["next_line"], 2)
        second = self.read_path(path, max_chars=5000, **first["continuation"])
        self.assertEqual(second["messages"][0]["text"], "B" * 1000)

    def test_first_oversized_message_has_explicit_reread_gap_and_advances(self):
        path = self.write("session.jsonl", [claude("A" * 4000), claude("visible")])
        result = self.read_path(path, max_chars=4000)
        self.assertLessEqual(len(sessions.encode(result)), 4000)
        gap = next(g for g in result["gaps"] if g["reason"] == "message_exceeds_output_budget")
        self.assertEqual(gap["reread_start_line"], 1)
        self.assertEqual(result["messages"][0]["text"], "visible")

    def test_byte_budget_partial_record_continuation_makes_progress(self):
        path = self.write("session.jsonl", [claude("A" * 5000), claude("after")])
        result = self.read_path(path, max_bytes=1024)
        self.assertFalse(result["coverage"]["complete_file"])
        self.assertEqual(result["continuation"]["start_line"], 1)
        self.assertGreater(result["continuation"]["start_byte"], 0)
        for _ in range(10):
            continuation = {k: v for k, v in result["continuation"].items() if k != "discard_partial_record"}
            result = self.read_path(path, max_bytes=1024, **continuation)
            if result["coverage"]["reached_eof"]:
                break
        self.assertTrue(result["coverage"]["reached_eof"])
        self.assertEqual(result["messages"][0]["text"], "after")

    def test_byte_budget_boundary_defers_next_visible_record(self):
        path = self.write("session.jsonl", [claude("first"), claude("B" * 500)])
        first = self.read_path(path, max_bytes=1024)
        if first["continuation"] is None:
            # Force the first complete row plus a partial second row.
            path = self.write("session.jsonl", [claude("A" * 300), claude("B" * 700)])
            first = self.read_path(path, max_bytes=1024)
        self.assertEqual(len(first["messages"]), 1)
        self.assertEqual(first["coverage"]["next_line"], 2)
        self.assertNotIn("discard_partial_record", first["continuation"])
        second = self.read_path(path, max_bytes=2048, **first["continuation"])
        self.assertEqual(len(second["messages"]), 1)
        self.assertTrue(second["messages"][0]["text"].startswith("B"))

    def test_physical_line_limit_reports_omission_then_next_visible_message(self):
        path = self.write("session.jsonl", [claude("A" * (sessions.LINE_BYTES + 20)), claude("after")])
        result = self.read_path(path)
        self.assertEqual([m["text"] for m in result["messages"]], ["after"])
        self.assertEqual(result["gaps"][0]["reason"], "oversized_or_partial_record_omitted")
        self.assertTrue(result["coverage"]["complete_file"])

    def test_redaction_covers_common_credentials_without_claiming_privacy(self):
        secret = "ghp_" + "a" * 30
        text = f'Authorization: Bearer abc.def.ghi\napi_key="hello"\npassword: hunter2\n{secret}\nhttps://name:pass@example.test\nPerson Alex'
        result = self.read([claude(text)])
        exposed = sessions.encode(result)
        for value in ("abc.def.ghi", "hello", "hunter2", secret, "name:pass"):
            self.assertNotIn(value, exposed)
        self.assertIn("Person Alex", exposed)
        self.assertEqual(result["redaction"], "best_effort_common_credentials_only")

    def test_safe_file_type_and_symlink_checks(self):
        wrong = self.root / "session.txt"
        wrong.write_text("{}")
        with self.assertRaises(ValueError):
            self.read_path(wrong)
        real = self.write("real.jsonl", [claude("visible")])
        link = self.root / "linked.jsonl"
        link.symlink_to(real)
        with self.assertRaises(ValueError):
            self.read_path(link)
        folder = self.root / "linked-folder"
        folder.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.read_path(folder / "real.jsonl")
        with self.assertRaises(ValueError):
            self.read_path(self.root)
        fifo = self.root / "pipe.jsonl"
        if hasattr(os, "mkfifo"):
            os.mkfifo(fifo)
            with self.assertRaises(ValueError):
                self.read_path(fifo)

    def test_inventory_combines_sources_limit_and_excludes_indexes_archives_agents(self):
        root = self.write("claude/projects/project/root.jsonl", [claude("private")])
        self.write("claude/history.jsonl", [claude("index")])
        self.write("claude/projects/project/subagents/agent.jsonl", [claude("agent")])
        primary = self.write("codex/sessions/2026/01/02/rollout-primary.jsonl", [meta(), codex("private")])
        self.write("codex/sessions/2026/01/02/rollout-agent.jsonl", [meta(source={"subagent": {}}), codex("agent")])
        self.write("codex/archived_sessions/archive.jsonl", [meta()])
        os.utime(root, (10, 10))
        os.utime(primary, (20, 20))
        result = self.inventory(limit=2)
        self.assertEqual([f["source"] for f in result["files"]], ["codex", "claude"])
        self.assertNotIn("private", sessions.encode(result["files"]).replace(str(self.root), ""))
        self.assertEqual(len(self.inventory(limit=1)["files"]), 1)
        self.assertEqual(result["files"][0]["session_id"], "synthetic-codex")

    def test_since_uses_observed_session_date_and_reports_unknown_date(self):
        self.write("claude/projects/p/a.jsonl", [claude("older", timestamp="2025-01-01T00:00:00Z")])
        self.write("claude/projects/p/b.jsonl", [claude("newer", timestamp="2026-01-02T00:00:00Z")])
        self.write("claude/projects/p/c.jsonl", [claude("unknown", timestamp=None)])
        result = self.inventory(source="claude", since="2026-01-01")
        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(Path(result["files"][0]["path"]).name, "b.jsonl")
        self.assertTrue(any(d["reason"] == "date_unknown_since_filter" for d in result["diagnostics"]))

    def test_inventory_newest_codex_dates_first_and_per_source_budgets(self):
        self.write("claude/projects/p/a.jsonl", [claude("one")])
        self.write("claude/projects/p/b.jsonl", [claude("two")])
        self.write("codex/sessions/2025/01/01/old.jsonl", [meta()])
        self.write("codex/sessions/2026/01/01/new.jsonl", [meta()])
        result = self.inventory(max_files=1)
        paths = [Path(f["path"]).name for f in result["files"]]
        self.assertIn("new.jsonl", paths)
        self.assertNotIn("old.jsonl", paths)
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(result["limits"]["scan_limit_scope"], "per_source")
        self.assertTrue(any(d["reason"] == "scan_limit" for d in result["diagnostics"]))

    def test_inventory_skips_directory_and_file_symlinks(self):
        real = self.write("outside/real.jsonl", [claude("private")])
        base = self.root / "claude/projects"
        base.mkdir(parents=True)
        (base / "linked-project").symlink_to(real.parent, target_is_directory=True)
        project = base / "project"
        project.mkdir()
        (project / "linked.jsonl").symlink_to(real)
        result = self.inventory(source="claude")
        self.assertEqual(result["files"], [])
        self.assertEqual(result["counts"]["symlinks_skipped"], 2)

    def test_header_limit_unsupported_schema_does_not_load_whole_file(self):
        path = self.write("codex/sessions/2026/01/01/unknown.jsonl", [{"type": "unknown", "text": "A" * 100000}])
        result = self.inventory(source="codex")
        self.assertEqual(result["files"], [])
        self.assertEqual(result["counts"]["headers_checked"], 1)
        self.assertEqual(result["diagnostics"][0]["reason"], "unsupported_or_header_limit")
        self.assertTrue(path.exists())

    def test_cli_stdout_only_no_generated_exports(self):
        path = self.write("session.jsonl", [claude("visible")])
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        process = subprocess.run([sys.executable, str(SCRIPT), "read", "--source", "claude", "--file", str(path)],
                                 capture_output=True, text=True, cwd=self.root, check=True)
        self.assertEqual(process.stderr, "")
        self.assertEqual(json.loads(process.stdout)["messages"][0]["text"], "visible")
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))

    def test_cli_invalid_bounds_and_error_json(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            sessions.parser().parse_args(["read", "--source", "claude", "--file", "synthetic.jsonl", "--max-lines", "0"])
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = sessions.main(["read", "--source", "claude", "--file", str(self.root / "missing.jsonl")])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(stdout.getvalue())["version"], 1)


if __name__ == "__main__":
    unittest.main()
