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


from datetime import datetime as dt
import json
import messages # Custom file for shared functionality


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
    # Parse Message type
    message = data.decode("utf-8")
    mtype, acode, params = messages.unformat_message(message)
    # Match to an existing one or throw an error
    # Given a specific message type, go to a specific routine
    match mtype:
        case "Status Request":
            response = get_status()
        case "Locations Request":
            response = get_locations(params["Limit"])
        case "Forecast Request":
            response = get_forecasts(params["Location"], \
                params["ConditionNames"], params["AdditionalDays"])
        case "Auth Request":
            response = grant_auth(params["Password"])
        case "Append Forecast Data Request":
            response = append_forecast(acode, params["Location"], \
                params["Conditions"])
        case "Edit Forecast Data Request":
            response = edit_forecast(acode, params["Location"], params["Date"],\
                params["Conditions"])
        case "Append Location Data Request":
            response = add_location(acode, params["LocationCode"],\
                params["LocationName"])
        case _:
            response = give_error("UNKNOWN MESSAGE")

    print(f"  <- {len(data)} bytes from {addr[0]}:{addr[1]}: {data!r}", flush=True)
    return data

#TODO:
def error_check(message: str) -> dict:
    """Checks for any errors in a provided message.
    If there's an error with it, makes that error.
    """

    return

def get_status() -> dict:
    """Provide the server's status.
    Curren local date and time,
    If an Admin is active,
    & Uptime.
    """
    response = {"CurTime": None, "LocalDate": None,
        "AdminActive": admin_active, "Uptime": None}
    
    now = dt.now()
    response["CurTime"] = now.time()
    response["LocalDate"] = now.date()
    response["Uptime"] = (now-start_time).total_seconds()

    return response

#TODO:
def get_locations(limit: int = -1) -> dict:
    """Provide the location dictionary.
    Convert it into a string matching format specification.
    """
    
    return

#TODO:
def get_forecasts(location: str, condition_names: list[str] | None = None, additional_days: int = 0) -> dict:
    """Provide the forecast
    """
    return

#TODO:
def grant_auth(password: str) -> dict:
    """Check if the password matches one of an authorized user,
    then generate & store a temporary authorization code.
    Provide that & the expiry time to the user.
    """
    return

#TODO: also fill in remaining params
def append_forecast(authcode: str, location: str, conditions: dict[str, float|int|str]) -> dict:

    return

#TODO: also fill in remaining params
def edit_forecast(authcode: str, location: str, date: str, ) -> dict:

    return

#TODO:
def add_location(authcode: str, loc_code: str, location: str) -> dict:

    return

#TODO:
def give_error(error_code: str) -> dict:
    """Given an erorr code, passes back an error response with the
    appropriate message.
    """

def main() -> None:
    ap = argparse.ArgumentParser(description="Project 1 UDP server")
    ap.add_argument("--host", default="0.0.0.0", help="address to bind (default: all)")
    ap.add_argument("--port", type=int, default=9000, help="port to bind (default: 9000)")
    args = ap.parse_args()

    # SOCK_DGRAM is UDP. There is no listen() and no accept() — no connections exist.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    # default server vars
    # Server status vars
    start_time = dt.now()
    admin_active = False
    #TODO: load locations dictionary.
    #TODO: set default weather.
    #TODO: set up codes
    accepted_passwords = []
    authcodes = {}

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
