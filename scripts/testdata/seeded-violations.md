# Seeded violation fixture — every residue class the boundary gate claims to catch

This file is test data with SCHEMATIC placeholders only — no live private
slug, path, or artifact reference appears here. It must trip every class;
the gate skips `testdata/` on real scans and reads this file only under
`--self-test`. Members marked (widened) would have been MISSED by the
pre-repair regexes, so the self-test proves the widening, not just the
original enumeration.

1. Private link (widened: non-enumerated slug): see
   github.com/instagrim-dev/private-example-repo for the implementation,
   also referenced as instagrim-dev/another-private-example.
2. Workspace path: the plan lives at /Users/exampleuser/dev/gh/example/docs/.
   (widened) uppercase+digit username: /Users/ExampleUser2/dev/notes.md;
   (widened) Linux home: /home/builder/x/config.yaml;
   (widened) tilde-relative: see ~/dev/example/scratch.md.
3. Internal review id: per docs/reviews/2026-01-01-example.md.
   (widened) non-enumerated docs tree: docs/brainstorms/2026-01-01-example-walk.md.
4. Internal shorthand (widened: letters outside the old alphabet): this
   satisfies XZ9 and F5 as reviewed; (widened) two-letter code OS1;
   (widened) MU-token MU-XX-101; (widened) backticked form `Q7`.
5. Correctness claim: this work is GVC-verified and therefore proven correct.
6. Pre-publication marker (widened: class did not exist pre-repair): this
   repository stays private until the publication boundary gate is green.
