# Phase 4 Reflection

**Group members:**
**Partner group:**
**Protocol:**
**Date:**

> Written after the in-class interoperability session.
>
> This is a **reflection, not a lab report**. We are not looking for a polished writeup or a description of what the protocol does — we already have your spec. We want to know what actually happened when your code met theirs, and what you now think differently about.
>
> Concrete beats general throughout. "We hadn't specified a timeout, so their client waited forever against our server" is worth more than a paragraph about the importance of clear specifications. Two to three pages.

---

## 1. What happened

> Walk through the four combinations. Which worked immediately, which failed, which sort of worked in a way you didn't notice at first?

| Client | Server | Result |
|:--|:--|:--|
| ours | ours | |
| ours | theirs | |
| theirs | ours | |
| theirs | theirs | |

## 2. The first thing that broke

> In detail. What was the symptom? What did you see in Wireshark? How long did it take to work out, and what was the actual cause?
>
> A screenshot or a pasted packet summary is welcome.

## 3. Assumptions you didn't know you were making

> Something your code relied on that your spec never said. Every group has at least one — finding it is the entire point of the exercise.
>
> Where in the spec *should* it have been written down? Why do you think you didn't notice it was missing?

## 4. Where the two implementations diverged

> Beyond outright bugs: places where both groups read the same sentence and built different things. Was the spec genuinely ambiguous, or did one side simply misread it?

## 5. What you'd change about the spec

> Not the code — the specification. If you handed v3 to a third group who had never spoken to either of you, what would you have to add or rewrite?

## 6. What this changed about how you think about protocols

> You've read about HTTP, DNS, and SMTP being defined in RFCs. Having now written a spec and watched someone else implement it, does that process look different than it did in Week 2? Anything in the textbook protocols that suddenly makes more sense?
