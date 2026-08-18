# Patent posture

## Non-assert covenant (OWFa 1.0)

The maintainers of this repository apply the **Open Web Foundation
Agreement 1.0** (OWFa 1.0) patent non-assert covenant to the Graded
Verdict Custody specification (`spec/graded-verdict-custody.md` together
with `registration/verdict-grade-registration.json` and
`conformance/fixtures/`, the "Specification").

Per OWFa 1.0 section 3 (Patent Non-Assert), the maintainers irrevocably
covenant not to assert any of their **Necessary Claims** — patent claims
that are necessarily infringed by implementing the required portions of
the Specification — against any party for making, using, selling, offering
for sale, importing, or distributing an implementation of the
Specification, subject to the defensive-termination conditions stated in
OWFa 1.0.

The full instrument text is published by the Open Web Foundation:
<https://www.openwebfoundation.org/legal/the-owf-1-0-agreements/owfa-1-0>.
This file adopts that instrument's covenant as written; it does not restate
or modify it. Where this summary and the instrument differ, the instrument
governs.

## Successors and assigns

The covenant binds the maintainers' successors-in-interest and assigns, per
OWFa 1.0 section 8 (Transition and Transfer). A transfer of the
Specification's stewardship — including the council formation path described
in `governance/GOVERNANCE.md` — carries the covenant with it; no change of
authority narrows the grant already made for published versions.

## Inbound contributions

Inbound contributor IPR is handled by the Developer Certificate of Origin
(see the `DCO` file): every contribution must carry a `Signed-off-by`
line certifying the contributor's right to submit it under this
repository's licenses (see `CONTRIBUTING.md`). Contributions accepted into
the Specification fall under the same non-assert covenant once published.

## Conformance claims and naming

Conformance claims are governed by the Specification's conformance section
(spec section 9): claims MUST be version-pinned (for example "conforms to
GVC 1.2", never a bare major) and accompanied by machine-readable output
from the conformance runner demonstrating the claim. A conformance claim
without a passing pinned runner artifact is a self-issued grade — the exact
shape the Specification's producer-mint prohibition forbids.
