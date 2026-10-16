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
    "Desc": ["Sunny", "Cloudy", "Overcast", "Rainy", "Storms"],
    "PType": ["None", "Rain", "Snow", "Sleet", "Hail"],
    # I dont want to bother being fancy. brute force.
    "WDir": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW",
            "SW", "WSW", "W", "WNW", "NW", "NNW"]
}
CONDITION_TYPES = ["Desc","Humid", "PChance", 
        "PType", "Temp","UV", "WDir", "WSpeed"]

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
    message = data.decode("ascii")
    # TODO: depending on implementation, may have to try-catch errors
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

    params = {key:val for key, val in response.items() if key != "Message Type"}
    data = messages.format_message(response["Message Type"], None,params)

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
    # Note: considering a lot of these are "message specific", I think
    # it may make sense to leave those for within the messages. Also
    # was a little silly to define the order we did for them. -Jordan

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
    # I think we forgot a TimeZone field in the spec
    response = {"Message Type": "Status Response","CurTime": None, "LocalDate": None,
        "TimeZone": None,"AdminActive": admin_active, "Uptime": None}
    
    now = dt.now().astimezone()

    response["CurTime"] = now.strftime("%H:%M")
    response["LocalDate"] = now.strftime("%Y-%m-%d")
    response["TimeZone"] = now.tzname()
    response["Uptime"] = (now-start_time).total_seconds()

    return response

def get_locations(limit: int = -1) -> dict:
    """Provide the location dictionary.
    Convert it into a string matching format specification.
    """
    if limit == -1:
        limit = len(locations)
    # get items in location. make a list of them. truncate based on limit.
    # make a dict of that.
    return {"Message Type": "Locations Response",
        "LocationDictionary": dict(list(locations.items())[:limit])}

def get_forecasts(location_code: str, condition_names: list[str] | None = None, additional_days: int = 0) -> dict:
    """Provide the forecast for a specific location up to a # of days."""
    if location_code not in locations:
        return give_error("UNKNOWN LOCATION")
    if additional_days > 14 or additional_days < 0:
        return give_error("INVALID DAYS")

    result = {"Message Type": "Forecase Response",
              "Location": location[location_code]}
    loc_forecasts = forecasts[location_code]

    # additional_days+1 since default is to only give today
    for day_num in range(additional_days+1):
        day = (day.today() + timedelta(days=day_num)).isoformat()
        # for safety
        if day not in loc_forecasts:
            continue
        # gets all conditions
        conditions = loc_forecasts[day]
        # filters
        if condition_names is not None and len(condition_names) > 0:
            conditions = {
                name: cond
                for name, cond in conditions.items() if name in condition_names
            }
        
        result[day_num] = conditions
    
    return result

def grant_auth(password: str) -> dict:
    """Check if the password matches one of an authorized user,
    then generate & store a temporary authorization code.
    Provide that & the expiry time to the user.
    """
    clean_auth()
    if password not in accepted_passwords:
        # Realized none of our errors really make sense if someone
        # without auth tries to get it. Closest match.
        return give_error("NEED AUTH")
    # Always generates, in case someone wants to refresh their authcode
    # generate an authcode
    authcode = ''.join(random.choices(string.ascii_letters+string.digits, k=6))
    # generate an expiry time, 1 hr from now
    expireTime = dt.now()+tdelt(hours=1)

    authcodes[authcode] = expireTime

    return {"Message Type": "Auth Response",
        "Code": authcode, "ExpiryTime": int(expireTime.timestamp())}

def append_forecast(authcode: str, location_code: str, conditions: dict[str, float|int|str]) -> dict:
    """If user is authenticated, appends the day's conditions to the next open date
    for a location.
    """
    clean_auth()
    if location_code not in locations:
        return give_error("UNKNOWN LOCATION")
    if not set(CONDITION_TYPES).issubset(conditions):
        return give_error("MISSING PARAMETER")
    if authcode not in authcodes:
        return give_error("NEED AUTH")
    if len(conditions) < len(CONDITION_TYPES):
        return give_error("MISSING PARAMETER")
    for cond in conditions:
        if cond not in CONDITION_TYPES:
            return give_error("INVALID FIELD")
    
    # find next unset day
    loc_forecasts = forecasts[location_code]
    next_day = date.today()
    while next_day.isoformat() in loc_forecasts:
        next_day += timedelta(days=1)

    # adds forecase
    location_forecasts[next_day.isoformat()] = conditions.copy()

    return {"Message Type": "Append Forecast Data Response", 
            "Location": locations[location_code], "Date": next_day.isoformat(),
            "Conditions": conditions}

def edit_forecast(authcode: str, location_code: str, forec_date: str,
                        conditions: dict[str, float|int|str]) -> dict:
    """Updates the forecast on a given date with those conditions."""
    clean_auth() # to ensure authcode is fine
    if location_code not in locations:
        return give_error("UNKNOWN LOCATION")
    if not set(CONDITION_TYPES).issubset(conditions):
        return give_error("MISSING PARAMETER")
    if authcode not in authcodes:
        return give_error("NEED AUTH")
    for cond in conditions:
        if cond not in CONDITION_TYPES:
            return give_error("INVALID FIELD")
    try:
        parsed_date = dt.strptime(forec_date, "%Y-%m-%d")
    except ValueError:
        return give_error("INVALID FIELD")
    if parsed_date.strftime("%Y-%m-%d") != forec_date:
        return give_error("INVALID FIELD")
    if forec_date not in forecasts[location_code]:
        return give_error("INVALID FIELD")

    current = forecasts[location_code][forec_date]
    old_conds = {
        name: old[name] for name in conditions
    }
    
    current.update(conditions)

    return {"Message Type": "Edit Forecast Data Response",
            "Location": locations[location_code],
            "Old": old_conds, "New": conditions.copy()}

def add_location(authcode: str, loc_code: str, location: str) -> dict:
    """Updates the locations dict with a new location."""
    clean_auth() # to ensure authcode is fine
    if authcode not in authcodes:
        return give_error("NEED AUTH")
    if loc_code in locations:
        return give_error("PREEXISTING LOCATION")
    locations[loc_code] = location
    forecasts[loc_code] = {}
    return {"Message Type": "Append Location Data Response"}

def give_error(error_code: str) -> dict:
    """Given an error code, passes back an error response with the
    appropriate message.
    """
    if error_code in ERROR_DICT:
        return {"Message Type": "Error Message",
            "ErrorCode": error_code, "Message": ERROR_DICT[error_code]}
    else:
        return {"Message Type": "Error Message",
            "ErrorCode": "MISC ERROR", "Message": ERROR_DICT["MISC ERROR"]}

def clean_auth():
    """Helper Function. Removes expired authcodes."""
    now = dt.now()
    delete_keys = []
    for code, expiry in authcodes.items():
        if now >= expiry:
            delete_keys.append(code)

    for code in delete_keys:
        del authcodes[code]

def generate_day() -> dict:
    """Generates random weather information for a single day. Not fancy.
    Will have weird days like 'Sunny, PChance 95%, Hail, Wind 40 MPH'.
    """
    wdict = {"Desc": None,"Humid": None, "PChance": None, 
        "PType": None, "Temp": None,"UV": None, "WDir": None,
        "WSpeed": None}
    wdict["Desc"] = random.choice(CONDITIONS["Desc"])
    wdict["Humid"] = round(random.uniform(0, 100), 2)
    wdict["PChance"] = round(random.uniform(0, 100), 2)
    wdict["PType"] = random.choice(CONDITIONS["PType"])
    # gets a random temp & clamps b/w -10 and 105 F.
    wdict["Temp"] = round(max(-10, min(105 ,random.normalvariate(65, 15))), 1)
    wdict["UV"] = round(random.uniform(1,11), 1)
    wdict["WDir"] = random.choice(CONDITIONS["WDir"])
    wdict["WSpeed"] = random.uniform(0, 50)
    
    return wdict

def generate_forecast(days = 15):
    forecast = {}
    for i in range(days):
        day = date.today() + timedelta(days=i)
        forecast[day.isoformat()]=generate_day()
    return forecast

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
