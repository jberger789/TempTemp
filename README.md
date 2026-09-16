# Project 1 — Application Layer Protocol

**CSCI 4431 / 6431 — Computer Networks, Fall 2026**

You and your partner will design an application-layer protocol, write a specification for it, implement it, and then try to make your implementation talk to **another group's completely independent implementation of the same protocol**.

This project is less focused on the code you will write, and more on discovering — live, in class — that two teams reading the same specification may end up building two incompatible things. That experience is what this project is about.

---

## Where everything goes

```
spec/spec-v1.md     Phase 1 — your team's specification, written in isolation
spec/spec-v2.md     Phase 2 — the merged spec, after meeting your partner group
src/                Phase 3 — your client and server
reflection.md       Phase 4 — what you learned when the two implementations met
TEAM.md            Who you are, your protocol, your partner group

PROTOCOLS.md       The protocols you can choose from
RUBRIC.md          How the 100 points are split
```

Two of those are for reading, not editing: **[PROTOCOLS.md](PROTOCOLS.md)** lists what you can build, and **[RUBRIC.md](RUBRIC.md)** shows how the 100 points are split. Read both before you start.

Please keep these paths exactly as they are. We grade 25+ repositories; if your spec is somewhere unexpected, it may not get found.

---

## Setting up your repository

You work in **groups of 2 or 3, sharing one repository**. Only one of you creates it by accepting .

**1. One of you accepts the assignment.** Whoever goes first becomes the *founder* — the repository is named after them and they're the only one who can add the others. Decide between you who does this; it doesn't matter which of you it is.

```sh
gh student accept gw-computer-networks-f26 csci4431 project1-app-protocol
```

**2. The founder adds each teammate** — run this once per person:

```sh
gh student invite gw-computer-networks-f26/csci4431-project1-app-protocol-<founder> <teammate>
```

Replace `<founder>` with the founder's GitHub username (it's in the repository name the previous step printed) and `<teammate>` with a groupmate's. In a group of three, run it twice.

**3. Each teammate accepts the GitHub invitation** — it arrives by email and also appears at <https://github.com/notifications>. Until they accept, they can't push.

**4. You all clone the same repository** and work in it normally. Any of you can push, and any of you can push the submission tags.

> **"Teammate" and "partner group" are different things.** Your **teammates** are the other one or two people in your group. You share a repository, you share a grade, you write one spec together. Your **partner group** is a different group building the same protocol independently. You never share code or a repository with them — you meet them in class in Phase 2, and test against them in Phase 4.

**5. Choose your protocol.** Read **[PROTOCOLS.md](PROTOCOLS.md)** and discuss what kind of protocol you are interested in. You will officially pick your protocol in class during Week 4. We will need **two groups to build each protocol**, so you'll need to match up with another group.

You may propose a protocol that isn't on the list, but only with our approval and if another group commits to building it too — [PROTOCOLS.md](PROTOCOLS.md) explains why.

Fill in the rest of `TEAM.md` once you're set up and have determined your protocol.

---

## Phases and deadlines

| Phase | What | Where | Tag to push | When | Weight |
|:--|:--|:--|:--|:--|--:|
| 1 | Specification, written by your team alone | `spec/spec-v1.md` | `spec-v1/N` | Written out of class. Due Week 5 · 09-23 | 25% |
| 2 | Merged spec, with partner group | `spec/spec-v2.md` | `spec-v2/N` | Written in class, Week 5 | 15% |
| 3 | Client + server implementation | `src/` | `implementation/N` | Written out of class. Due Week 8 · 10-14 | 20% |
| 4 | Interoperability and Reflection | `reflection.md` | `reflection/N` | Evaluated and written in class, Week 8 | 30% |
| — | Project management | whole repo | — | — | 10% |

**The reflection is worth more than the code**, and the two specs together are worth twice the implementation. That's deliberate — see [RUBRIC.md](RUBRIC.md) for what each component is graded on.

### How to submit a phase

Committing and pushing is **not** submitting. To submit, push a tag:

```sh
git commit -am "Phase 1: initial specification"
git push

git tag spec-v1/1
git push origin spec-v1/1      # <- this is the submission
```

Use the exact tag names in the table, with a number on the end. Two habits carried over from the warm-up assignment:

- **`git commit -am` is your default.** It commits your edits and nothing else. Use `git add <file>` when you have made a *new* file that needs to be handed in.
- **A new number each time.** Tag names can only be used once, so a second attempt at Phase 1 is `spec-v1/2`, a third is `spec-v1/3`. We grade the highest-numbered tag you pushed before the deadline.

---

## Working with your partner group

You'll be paired with another group building the **same** protocol. Two rules, and they matter more than they might seem:

1. **You may only discuss and create the spec-v2 during the Phase 2 class session.** No messaging or asking for clarifications afterwards. You will have to resolve ambiguities in the v2 spec by reading it, which is exactly the situation real protocol implementers are in.
2. **You may never look at their code**, and nothing changes hands — no source, no executables, no repositories. In Phase 4 each group runs its **own** programs on its **own** machines, and you connect across the network:

   - they run their server, you point *your* client at it
   - you run your server, they point *their* client at it

That covers all four client/server combinations without anyone compiling anyone else's code. All you need from them is an address and a port.

Things might not work right away, so you'll need to debug, using tools like Wireshark and your brain... Good luck! (see phase 4 details in reflection.md).

---

## Technical requirements

- **UDP only.** Use datagram sockets.
- **Assume the network is reliable.** For this project, take it as given that every datagram arrives, exactly once, in the order it was sent. You do **not** need to design retransmission, acknowledgements, sequence numbers or duplicate detection — building reliability on top of UDP is what Project 2 is about. Here the interesting problem is the *protocol*: what the messages are, what they mean, and what happens when one side gets something it didn't expect.
- **Console applications.** No GUI, no web frontend.
- **Client and server both.** Your client must talk to your server before Phase 4.
- Any language is fine, the default is python for our class.

---

## Getting started

```sh
git clone <your repo url>
cd <your repo>

python3 src/server.py            # terminal 1
python3 src/client.py            # terminal 2
```

The stubs in `src/` are a working UDP echo client and server. They are a starting point, not a design — replace the message handling with your own protocol.

---

## Asking for help

Post in `#project-1` on Discord. Questions about *your own* design, sockets, or tooling are always fair game. Don't post your spec or your code publicly — your partner group is reading that channel too.
