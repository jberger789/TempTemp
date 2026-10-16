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

import string
import random
from datetime import datetime as dt, timedelta as tdelt
# These 2 are for saving and loading locations
import json
import os
import messages # Custom file for shared functionality

ERROR_DICT = {
    "UNKNOWN LOCATION": "The requested location code is not that of a supported location.",
    "INVALID FORMAT": "The message does not follow WSP format.",
    "UNKNOWN MESSAGE": "The message type is not supported by WSP.",
    "MISSING PARAMETER": "The request does not contain a required parameter.",
    "PREEXISTING LOCATION": "The location to be added has the same code as another location.",
    "NEED AUTH": "Insufficient authorization provided for the attempted action.",
    "INVALID UNIT": "The UNIT value is not F or C.",
    "INVALID DAYS": "The requested number of forecast days is greater than 14.",
    "INVALID FIELD": "A field contains an unsupported/invalid value.",
    "MISC ERROR": "Unspecified/Unknown error."
}

FILE = "locations.json" #location file

CONDITIONS = {
    "Desc": ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Storms"],
    "PType": ["None", "Rain", "Snow", "Sleet", "Hail"],
    # I dont want to bother being fancy. brute force.
    "WDir": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW",
            "SW", "WSW", "W", "WNW", "NW", "NNW"]
}

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
    response = None
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
def error_check(message: str) -> Tuple[boolean, dict]:
    """Checks for general errors in a provided message.
    If there's an error with it, responds with that error.

    Returns a tuple. 
    Value 1 is a boolean - True if an error was found, False if not
    Value 2 is a dict with 1 kvp contained (error code and message)
    """
    # unknown location
    # invalid format
    # missing params
    # preexisting location
    # need auth
    # invalid unit
    # invalid days
    # invalid field
    # misc error

    return (False, None)

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
    if limit == -1:
        limit = len(locations)
    # get items in location. make a list of them. truncate based on limit.
    # make a dict of that.
    return {"LocationDictionary": dict(list(locations.items())[:limit])}

#TODO:
def get_forecasts(location: str, condition_names: list[str] | None = None, additional_days: int = 0) -> dict:
    """Provide the forecast
    """
    return

def grant_auth(password: str) -> dict:
    """Check if the password matches one of an authorized user,
    then generate & store a temporary authorization code.
    Provide that & the expiry time to the user.
    """
    if password not in accepted_passwords:
        return None
    # Always generates, in case someone wants to refresh their authcode
    # generate an authcode
    authcode = ''.join(random.choices(string.ascii_letters+string.digits, k=6))
    # generate an expiry time, 1 hr from now
    expireTime = dt.now()+tdelt(hours=1)

    authcodes[password] = (authcode, expireTime)

    return {"Code": authcodes[password][0], "ExpiryTime": authcodes[password][1]}

#TODO: also fill in remaining params
def append_forecast(authcode: str, location: str, conditions: dict[str, float|int|str]) -> dict:
    clean_auth() # to ensure authcode is fine
    return

#TODO: also fill in remaining params
def edit_forecast(authcode: str, location: str, date: str, ) -> dict:
    clean_auth() # to ensure authcode is fine
    return

#TODO:
def add_location(authcode: str, loc_code: str, location: str) -> dict:
    clean_auth() # to ensure authcode is fine
    if authcode in authcodes:
        
    return

def give_error(error_code: str) -> dict:
    """Given an error code, passes back an error response with the
    appropriate message.
    """
    if error_code in ERROR_DICT:
        return {error_code: ERROR_DICT[error_code]}
    else:
        return {"MISC ERROR": ERROR_DICT["MISC ERROR"]}

def validate_auth(authcode):
    """Helper Function. Validates if an authcode is good
    or not.
    """
    now = dt.now()
    for password, (code, expire) in authcodes.items():
        if code == authcode and now < expire:
            return True

    return False

def clean_auth():
    """Helper Function. Removes expired authcodes."""
    now = dt.now()
    for password, (code, expiry) in authcodes.items():
        if now >= expiry:
            del authcodes[password]

def generate_day() -> dict:
    """Generates random weather information for a single day. Not fancy.
    Will have weird days like 'Sunny, PChance 95%, Hail, Wind 40 MPH'.
    """
    wdict = {"Desc": None,"Humidity": None, "PChance": None, 
        "PType": None, "Temp": None,"UV": None, "WDir": None,
        "WSpeed": None}
    wdict["Desc"] = random.choice(CONDITIONS["Desc"])
    wdict["Humidity"] = round(random.uniform(0, 1), 2)
    wdict["PChance"] = round(random.uniform(0, 1), 2)
    wdict["PType"] = random.choice(CONDITIONS["PType"])
    # gets a random temp & clamps b/w -10 and 105 F.
    wdict["Temp"] = round(max(-10, min(105 ,random.normalvariate(65, 15))), 1)
    wdict["UV"] = round(random.uniform(0,11), 1)
    wdict["WDir"] = random.choice(CONDITIONS["WDir"])
    wdict["WSpeed"] = random.uniform(0, 50)
    
    return wdict

def generate_forecast(days = 15):
    forecast = {}
    for i in range(days):
        day = date.today() + timedelta(days=i)
        forecast[day.isoformat()]=generate_day()

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
    # load location dict or create if DNE
    if not os.path.exists(FILE):
        locations = {
            "BOS": "Boston",
            "NYC": "New York",
            "TKY": "Tokyo",
            "SGP": "Singapore",
            "LAX": "Los Angeles",
            "DET": "Detroit"
        }
        with open(FILE, "w") as file:
            json.dump(locations, file, indent=4)
    else:
        with open(FILE, "r") as file:
            locations = json.load(file)
    with open("locations.json", "r") as f:
        locations = json.load(f)
    
    # set default weather.
    forecasts = {
        code: generate_forecast() for code in locations
    }
    # set up codes
    accepted_passwords = ["Password123", "XKCD", "123!/x"]
    # dict. Key = password, value = tuple of Code & ExpiryTime
    authcodes = {}

    print(f"listening on {args.host}:{args.port} (ctrl-c to stop)", flush=True)

    try:
        while True:
            # Re
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
