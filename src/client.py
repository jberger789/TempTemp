#!/usr/bin/env python3
"""
UDP echo client — a starting point for Project 1.

Reads a line, sends it, prints the reply. Replace send_request() with your own
protocol's messages.

    python3 src/client.py --host 127.0.0.1 --port 9000
"""

import argparse
import socket

import messages # custom file for shared functionality

# For this project you may assume the network is reliable: every datagram arrives,
# exactly once, in order. So you do NOT need retransmission, acknowledgements or
# sequence numbers -- that is Project 2's subject.
#
# A timeout is still worth having, because plenty can go wrong that isn't packet loss:
# the server isn't running, the address or port is wrong, or the server has a bug and
# never replies. Without one, recv() blocks forever and the program just hangs.
TIMEOUT_SECONDS = 2.0


def send_request(sock: socket.socket, server: tuple[str, int], line: str) -> None:
    """Send one message and print the reply.

    Your protocol goes here: build the request bytes per your spec, send them,
    then parse the response.
    """
    # Jordan: I don't know if we really need to do anything client side to build.

    sock.sendto(line.encode(), server)

    try:
        data, _ = sock.recvfrom(65535)
    except socket.timeout:
        # Assuming no loss, silence means the server isn't reachable or didn't answer:
        # not running, wrong host/port, blocked by a firewall, or a bug on its side.
        # Your spec should say what the client tells the user when this happens.
        print(f"  (no reply within {TIMEOUT_SECONDS}s)")
        #TODO:
        return

    #TODO: should parse out and make the response easily readable.
    # What that means will depend on the message type received.
    print(f"  <- {data.decode(errors='replace')}")

def main() -> None:
    ap = argparse.ArgumentParser(description="Project 1 UDP client")
    ap.add_argument("--host", default="127.0.0.1", help="server address")
    ap.add_argument("--port", type=int, default=9000, help="server port")
    args = ap.parse_args()

    server = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SECONDS)

    print(f"talking to {args.host}:{args.port} — type a message, ctrl-d to quit")
    try:
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            if line:
                send_request(sock, server, line)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("\nbye")


if __name__ == "__main__":
    main()
