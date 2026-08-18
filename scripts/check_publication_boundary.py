#!/usr/bin/env python3
"""Publication boundary gate.

Fails when any tracked byte of this repository carries private-provenance
residue or a correctness-semantics claim. Residue classes:

  private_link            links/slugs of private sibling repositories: any
                          instagrim-dev/<name> where <name> is not this
                          repository (class predicate, not a slug list)
  workspace_path          absolute or home-relative development paths (any
                          user-home segment under /Users or /home, and
                          tilde-relative paths)
  internal_review_id      internal planning/review artifact references
                          (docs/<any-tree>/20YY-)
  internal_shorthand      internal doctrine shorthand that only resolves
                          inside a private workspace: 1-2 uppercase letters +
                          1-3 digits (shown defused here as r9, f5, os1;
                          uppercase in the wild), MU-<ALPHA>-<N> tokens, in
                          bare or backticked form
  correctness_claim       phrasings that present a grade as a correctness
                          verdict (the spec's normative anti-claim)
  pre_publication_marker  pre-publication status phrasing (the
                          stays-private-until sentence) that must not
                          survive the flip

The gate scans itself; class descriptions above are deliberately written in
defused forms (lowercase shorthand, hyphenated marker phrase, no literal
path shapes) so documentation never carries live-form residue.

Modes:

  (default)    scan every git-tracked file in the worktree. A tracked file
               that cannot be scanned (undecodable/unreadable) is counted and
               FAILS the gate distinctly — "could not look" never reads clean.
  --self-test  scan the seeded violation fixture and fail unless every class
               is detected there (polarity: the gate must be able to go red).
  --file PATH  scan one arbitrary file and report hits (probe mode).
  --history    scan every blob of every commit reachable from every local ref
               (git rev-list --all). Slower; reports commit+path per hit.

THE VISIBILITY-FLIP PROCEDURE MUST RUN --history: a clean worktree does not
prove clean history, and the flip publishes every reachable commit.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEEDED = Path(__file__).resolve().parent / "testdata" / "seeded-violations.md"

RESIDUE_CLASSES = {
    "private_link": re.compile(
        r"instagrim-dev/(?!graded-verdict-custody(?![\w-]))[\w.-]+"
    ),
    # Spelled with defusing character classes ([U], [h], [/]) so the
    # pattern source cannot match itself when the gate scans this file.
    "workspace_path": re.compile(r"/[U]sers/[^/\s]+/|/[h]ome/[^/\s]+/|(?<!\w)~[/]"),
    "internal_review_id": re.compile(r"docs/[a-z-]+/20\d{2}-"),
    "internal_shorthand": re.compile(
        r"(?<![\w/-])(?:MU-[A-Z]+-\d+|[A-Z]{1,2}\d{1,3})(?![\w./-])"
    ),
    "correctness_claim": re.compile(
        r"(?i)\b(?:verified|proven|graded|guaranteed)\s+correct\b|\bGVC-verified\b|\bguarantees?\s+correctness\b"
    ),
    "pre_publication_marker": re.compile(
        r"(?i)stays\s+private\s+until|\bprivate\s+until\s+the\b[^\n]{0,80}\bgate"
    ),
}

# Narrow carve: public SPDX license identifiers that collide with the
# internal_shorthand shape and appear in verbatim upstream license text
# (LICENSE-CC-BY-4.0 names CC0). Public-vocabulary tokens, not residue.
ALLOWED_SHORTHAND = {"CC0"}

SKIP_PARTS = {".git", "testdata"}


def scan_text(text: str) -> dict:
    hits = {}
    for name, pattern in RESIDUE_CLASSES.items():
        count = 0
        for match in pattern.finditer(text):
            if name == "internal_shorthand" and match.group(0) in ALLOWED_SHORTHAND:
                continue
            count += 1
        if count:
            hits[name] = count
    return hits


def scan_file(path: Path):
    """Return {class: count} for a decodable file, or None when the file
    could not be read/decoded (the caller must surface that, never drop it)."""
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        return None
    return scan_text(text)


def tracked_files() -> list:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [ROOT / rel for rel in out.split("\0") if rel]


def gate() -> int:
    failures = 0
    scanned = 0
    skipped = []
    for path in sorted(tracked_files()):
        if any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        hits = scan_file(path)
        if hits is None:
            skipped.append(path.relative_to(ROOT))
            continue
        scanned += 1
        for name, count in hits.items():
            failures += 1
            print(f"  FAIL {path.relative_to(ROOT)}: {name} x{count}")
    if scanned == 0:
        print("FAIL: gate scanned zero files — vacuous run")
        return 2
    if skipped:
        for rel in skipped:
            print(f"  SKIPPED-UNSCANNED {rel}")
        print(
            f"FAIL: {len(skipped)} tracked file(s) skipped-unscanned "
            "(undecodable/unreadable) — an unscanned tracked byte cannot be "
            "certified clean"
        )
        return 2
    if failures:
        print(f"publication boundary: {failures} residue finding(s)")
        return 1
    print(f"publication boundary: clean ({scanned} files scanned, 0 skipped)")
    return 0


def self_test() -> int:
    if not SEEDED.exists():
        print(f"FAIL: seeded violation fixture missing at {SEEDED}")
        return 2
    hits = scan_file(SEEDED)
    if hits is None:
        print("FAIL: seeded violation fixture is unreadable")
        return 2
    missing = [name for name in RESIDUE_CLASSES if name not in hits]
    if missing:
        print(f"FAIL: gate did not detect seeded class(es): {missing}")
        return 1
    print(f"self-test: all {len(RESIDUE_CLASSES)} residue classes detected in the seeded fixture")
    return 0


def probe_file(arg: str) -> int:
    hits = scan_file(Path(arg))
    if hits is None:
        print(f"FAIL: could not read/decode {arg}")
        return 2
    for name, count in sorted(hits.items()):
        print(f"  HIT {arg}: {name} x{count}")
    print(f"{arg}: {'clean' if not hits else str(sum(hits.values())) + ' hit(s)'}")
    return 1 if hits else 0


def history() -> int:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True, text=True, check=True,
        ).stdout

    failures = 0
    skipped = 0
    commits = git("rev-list", "--all").split()
    for commit in commits:
        for line in git("ls-tree", "-r", "--name-only", commit).splitlines():
            if any(part in SKIP_PARTS for part in Path(line).parts):
                continue
            try:
                blob = git("show", f"{commit}:{line}")
            except (subprocess.CalledProcessError, UnicodeDecodeError):
                skipped += 1
                print(f"  SKIPPED-UNSCANNED {commit[:12]}:{line}")
                continue
            for name, count in scan_text(blob).items():
                failures += 1
                print(f"  FAIL {commit[:12]}:{line}: {name} x{count}")
    print(f"history: {len(commits)} commit(s) scanned")
    if skipped:
        print(f"FAIL: {skipped} historical blob(s) skipped-unscanned")
        return 2
    if failures:
        print(f"publication boundary (history): {failures} residue finding(s)")
        return 1
    print("publication boundary (history): clean")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--history" in sys.argv:
        sys.exit(history())
    if "--file" in sys.argv:
        sys.exit(probe_file(sys.argv[sys.argv.index("--file") + 1]))
    sys.exit(gate())
