# How Project 1 is graded

100 points total.

| Component | Weight | Submitted as |
|:--|--:|:--|
| Specification v1 | **25%** | tag `spec-v1/N` → `spec/spec-v1.md` |
| Specification v2 | **15%** | tag `spec-v2/N` → `spec/spec-v2.md` |
| Implementation | **20%** | tag `implementation/N` → `src/` |
| Reflection | **30%** | tag `reflection/N` → `reflection.md` |
| Project management | **10%** | see details down below |

Notice that **the reflection is worth more than the code**, and the two specs together are worth twice the implementation. This is deliberate: a single working client and server is the most straightforward part of this project. What we're actually assessing is whether you can specify a protocol precisely, notice where you were imprecise, and say something honest about why.

---

## Specification v1 — 25%

Written by your team alone, before you meet your partner group.

- **Completeness.** All six sections addressed: purpose, communication pattern, message format, message types, error handling, edge cases.
- **Precision.** Could a competent programmer implement this without asking you a single question?
- **Design decisions.** Your spec should justify its choices as part of the design.
- **Edge cases.** You may assume the network is reliable — no loss, no reordering, no duplicates — but there are other application-level errors which can occur. Your spec should explain how to handle these.

## Specification v2 — 15%

Written in class with your partner group.

- **The disagreement table.** Where the two v1 specs differed, what v2 says, and why. This table is the single most informative thing you'll write in Phase 2 — treat it as the main deliverable, not a preamble.
- **Cooperative resolution.** Ambiguities or inconsistencies should be settled by combining your best ideas, not just accepting one spec in full over the other.
- **Honesty about what's unresolved.** If there are areas you think your spec may not be complete, write these out as a prediction of challenges you'll face in Phase 4.

## Implementation — 20%

- **Client and server both**, working against each other, following your v2 spec.
- **Runnable by your partner group** from `src/README.md` alone, without asking you for help.


## Reflection — 30%

Written after the Phase 4 interoperability session.

- **Concrete over general.** "We hadn't specified a timeout, so their client waited forever against our server" beats a paragraph on the importance of clear specifications.
- **Evidence.** What you saw in Wireshark, what the symptom was, how long it took to find.
- **The assumption you didn't know you were making.** Explain any assumptions or different interpretations in the spec that led to issues between you and your partner group.
- **What you'd change about the spec** — what would you revise for a v3 spec?
- **Honesty.**  Describing things that broke is a positive here, not an admission of failure. Our focus is on your learning experience not whether you had a perfect spec from the start.

## Project management — 10%

This grades evidence that all of you actually worked on the project and followed the instructions.

- **`TEAM.md` filled in**: every member's name and GitHub username, your protocol, your partner group.
- **All four milestone tags pushed**, by their deadlines. Each phase is tagged with an appropriate tag as detailed in the instructions.
- **Every member visible in the history.** We expect to see commits from all team members. It is great if you work closely together, but be sure each student has a chance to write specs and code that is committed from their accounts.
- **Files in the expected places**, so your work can be found and marked.
