# Protocol Specification — v1

**Protocol name:**
**Group members:**
**Date:**

> **Phase 1.** Write this *before* talking to your partner group. Aim for something a competent programmer could implement without asking you a single question — that is the bar a real specification has to clear.
>
> Roughly 5 pages depending on your protocol complexity. Delete these quoted instruction blocks as you go.
>
> Throughout, we care as much about **why** as **what**. A spec that says "messages end with a newline" is OK, but one that says "messages end with a newline, because our payloads are human-readable text and we wanted the protocol debuggable with `nc`" is a more useful design document, especially when you need to justify your design to your partner team.

---

## 1. Purpose and scope

> What does this protocol let a client do? Two or three sentences. What is explicitly *out* of scope?

## 2. Communication pattern

> Who speaks first? Is every request answered? Can the server send anything unprompted? Is there a session or connection concept, or is each message independent?
>
> Remember you are on **UDP**: there is no connection unless you invent one.

## 3. Message types

> Every message your protocol defines. A table works well.

| Type | Direction | Purpose | Fields |
|:--|:--|:--|:--|
| | client → server | | |
| | server → client | | |

## 4. Message format

> The precise bytes on the wire. Text or binary? Field order, sizes, encoding, delimiters. How does a receiver know where a message ends?
>
> Include labelled examples of your message formats.

## 5. Error handling

> What can go wrong, and what happens then? Malformed messages, unknown message types, unsupported versions, requests for things that don't exist.
>
> Does the server reply with an error, or stay silent? If it stays silent, how does the client tell "rejected" from "still thinking"?

## 6. Edge cases and failure modes

> **Assume the network is reliable** — every datagram arrives exactly once, in order. You do not need to handle loss, reordering or duplication.
>
> The edge cases that remain are the ones your *protocol* creates, and they're where interoperability is usually won or lost. For example:
>
> - A message is **malformed** — wrong shape, missing a field, unparseable. What does the receiver do? Reply with an error, or ignore it?
> - A message has an **unknown type**. What if the other side implemented something you didn't?
> - A request refers to **something that doesn't exist** — a key that was never set, a file that isn't there. Is that an error, or an empty result?
> - A field is **empty**, or much longer than expected. Is `SET key <nothing>` legal?
> - A message is **larger than one datagram** (about 65 KB). Can that happen in your protocol? What should the sender do if it would?
> - The **server isn't running**, or the client has the wrong address. How long does the client wait before giving up, and what does the user see?
> - **Two clients** talk to the server at once. Does the server keep any per-client state, and what happens if it does?

## 7. Design decisions

> The three or four choices you argued about most. For each: what you picked, what you rejected, and why. Where do you think another team might reasonably choose differently?
>
> Be honest here — this section is worth more than a longer message-format table, and Phase 4 will tell you how good your predictions were.
