# Choosing a protocol

Every group picks a protocol to design and build. **At least two groups build each one** — you and your partner group work from the same protocol, write your specs independently, merge them, and then find out in Phase 4 whether your two implementations can actually talk.

Pick from the list below, or propose your own — see the rule at the bottom.

For all protocols you can assume:

- **UDP only**, and you may **assume no loss and no reordering** — every datagram arrives exactly once, in order.
- **Console applications.** No GUI, no web frontend required or expected.
- **No real external data.** Everything can be synthetic or hard-coded. A weather server inventing its forecasts is completely fine — the point is the protocol, not the data.

---

## Protocol complexity
The list of options below describe the high level functionality of a distributed application; your job will be to determine the specifics. Your design must meet a sufficient level of complexity:

- **At least four distinct message types**, doing meaningfully different jobs. `GET` and `SET` would be two but an error reply is not a third.
- **At least one interaction that spans multiple messages**, where what one side sends depends on what it received earlier.
- **At least two things that can go wrong at the application level** — not network failures, which you're assuming away, but things like a request for something that doesn't exist, a request that arrives at the wrong moment, or a value that's too large to send.

The entries below all meet this bar *if you build the harder version*. The "What makes it hard" column gives some ideas about the more advanced features you should consider to ensure your protocol is sufficiently complex. Aim for a protocol with complexity in both the messages it sends and the state it must maintain.

---

## The list

| Protocol | What it does | What makes it hard |
|:--|:--|:--|
| **File sharing** | Clients move files to and from the server, and find out what it has | A file larger than one datagram (~65 KB) has to be split up. You have to invent ordering, completion, and a way for the receiver to know it got everything. Also consider: overwriting, listing, and what a partial transfer leaves behind. |
| **Chat / messaging** | Clients post messages in rooms, others read them | How are clients addressed and messages delivered? Is history maintained?  |
| **Email-style server** | Users leave messages for each other and collect the ones addressed to them | How to handle addressing, mailboxes, and message retention? What happens to mail for a user who doesn't exist? |
| **Music service** | Clients control playback of a playlist the server keeps (send lyrics as the "audio") | How to handle timing of playback? How to support multiple clients? |
| **Key–value store** | Clients store and retrieve values the server holds on their behalf | Consider more complex features like with expiry, conditional writes ("only if unchanged"), listing what's there, and limits on how big a key or value may be. |
| **Name resolver** | Maps names to things, from a table you invent | One query type is trivial. Consider several kinds of record, answers with more than one result, names that resolve to other names, etc. |
| **Weather service** | Returns fabricated conditions for a named place | A single forecast for a single place is too simple. Consider extensions like multi-day forecasts, ranges of time, units the client asks for, etc. |
| **Dialogue server** | Runs a scripted back-and-forth with the client — knock-knock jokes, a choose-your-own-adventure, a text adventure | The exchange happens in a fixed order, so both sides must agree on whose turn it is and what a valid reply looks like at each step. What happens when the client says something unexpected mid-dialogue, or wanders off and comes back? |
| **Turn-based game** | Two clients play through a server — hangman, connect four, battleship | Pairing two players up, deciding whose turn it is, rejecting a move made out of turn, and agreeing on what "the game is over" means. Pick a game with real state; something decided in one move each is too small |
| **Peer-to-peer chat** | Nodes talk directly, with no central server — each is both client and server | Discovery: how does a node find the others? How ot handle clients changing over time? |

---

## Proposing your own

You may design something not on this list, on one condition:

> **At least one other group must commit to building the same protocol.**

Without a partner group there is nobody to interoperate with, and Phases 2 and 4 simply cannot happen. So find a group that wants to build it with you, then bring the proposal to your instructor together for approval before Phase 1 begins.

Keep it in the spirit of the list above: something that clears the complexity bar, that two groups can specify in about five pages and implement in a couple of weeks, as a console application over UDP.

