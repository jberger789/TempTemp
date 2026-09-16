#!/usr/bin/env python3
"""
UDP echo server — a starting point for Project 1.

This is NOT your protocol. It is the smallest thing that receives a datagram and
replies, so you have something that runs on day one. Replace handle() with your
own message parsing and response logic.

    python3 src/server.py --port 9000
"""

import argparse
import socket


def handle(data: bytes, addr: tuple[str, int]) -> bytes:
    """Handle one datagram and return the bytes to send back.

    Right now this echoes. Your protocol goes here: parse `data` according to
    your spec, work out which message type it is, and build a reply.

    For this project you may assume the network is reliable -- every datagram arrives
    exactly once, in order -- so you do not need duplicate detection or retransmission.
    What your spec does still have to answer:
      - what happens when `data` is malformed, empty, or a type you don't recognise
      - whether you reply with an error or stay silent, and what an error looks like
      - `addr` is the only thing identifying the client, and it is spoofable
    """
    print(f"  <- {len(data)} bytes from {addr[0]}:{addr[1]}: {data!r}", flush=True)
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description="Project 1 UDP server")
    ap.add_argument("--host", default="0.0.0.0", help="address to bind (default: all)")
    ap.add_argument("--port", type=int, default=9000, help="port to bind (default: 9000)")
    args = ap.parse_args()

    # SOCK_DGRAM is UDP. There is no listen() and no accept() — no connections exist.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    print(f"listening on {args.host}:{args.port} (ctrl-c to stop)", flush=True)

    try:
        while True:
            # 65535 is the largest a UDP datagram can be (about 65 KB of payload).
            # A message bigger than that cannot be sent at all, so if your protocol
            # can produce one, your spec has to say what the sender does instead.
            data, addr = sock.recvfrom(65535)
            reply = handle(data, addr)
            if reply is not None:
                sock.sendto(reply, addr)
                print(f"  -> {len(reply)} bytes to {addr[0]}:{addr[1]}", flush=True)
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
