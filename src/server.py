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
from datetime import datetime as dt, timedelta as tdelt, date

from typing import Tuple, Any
from itertools import islice

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

CONDITIONS = {
    "Desc": ["Sunny", "Cloudy", "Overcast", "Rainy", "Storms"],
    "PType": ["None", "Rain", "Snow", "Sleet", "Hail"],
    # I dont want to bother being fancy. brute force.
    "WDir": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW",
            "SW", "WSW", "W", "WNW", "NW", "NNW"]
}
CONDITION_TYPES = ["Desc","Humid", "PChance", 
        "PType", "Temp","UV", "WDir", "WSpeed"]

class WEP_Server():

    def __init__(self):
        # default server vars
        # Server status vars
        self.start_time = dt.now()
        self.admin_active = "False"
        #location dict
        self.locations = {
            "BOS": "Boston",
            "NYC": "New York",
            "TKY": "Tokyo",
            "SGP": "Singapore",
            "LAX": "Los Angeles",
            "DET": "Detroit"
            }
        
        # set default weather.
        self.forecasts = {
            code: self.generate_forecast() for code in self.locations
        }
        # set up codes
        self.accepted_passwords = ["password123", "XKCD", "123!/x"]
        # dict. Key = password, value = tuple of Code & ExpiryTime
        self.authcodes = {}

    def handle(self, data: bytes, addr: tuple[str, int]) -> bytes:
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
        try:
            mtype, authcode, params = messages.unformat_message(message)
        except Exception:
            # Catch errors when trying to parse incoming messages
            data = self.give_error(error_code="INVALID FORMAT")
        else:
            # Match to an existing one or throw an error
            # Given a specific message type, go to a specific routine
            match mtype:
                case "Status Request":
                    response = self.get_status()
                case "Locations Request":
                    response = self.get_locations(params)
                case "Forecast Request":
                    response = self.get_forecasts(params)
                case "Auth Request":
                    response = self.grant_auth(params)
                case "Append Forecast Data Request":
                    response = self.append_forecast(authcode, params)
                case "Edit Forecast Data Request":
                    response = self.edit_forecast(authcode, params)
                case "Append Location Data Request":
                    response = self.add_location(authcode, params)
                case _:
                    response = self.give_error("UNKNOWN MESSAGE")

            data = response
        
        print(f"  <- {len(data)} bytes from {addr[0]}:{addr[1]}: {data!r}", flush=True)
        return data.encode()

    #TODO:
    def error_check(self, message: str) -> Tuple[bool, dict]:
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

    def get_status(self) -> str:
        """Provide the server's status.
        Curren local date and time,
        If an Admin is active,
        & Uptime.
        """

        return messages.format_message(
            message_type="Status Response",
            CurTime = dt.now().time(),
            LocalDate = date.today(),
            AdminActive = self.admin_active,
            Uptime = (dt.now() - self.start_time).total_seconds()
        )

    def get_locations(self, params: Any|None) -> str:
        """Provide the location dictionary.
        Convert it into a string matching format specification.
        """
        if params is not None and "Limit" in params and params["Limit"] != -1:
            limit = params["Limit"]
        else:
            # Otherwise use the default of all locations
            limit = len(self.locations)
        
        if limit < -1:
            return self.give_error(error_code="INVALID FIELD")
        
        # Truncate the returned dict based on limit
        rdict = dict(islice(self.locations.items(), limit)) 

        return messages.format_message(
            message_type="Locations Response",
            LocationDictionary=rdict
        )

    def locations_error_correction(self, loc: str) -> str:
        """Returns the appropriate location code for either a location code or location name, to ameliorate spec ambiguity"""
        
        if loc in self.locations.keys():
            return loc
        else:
            if loc in self.locations.values():
                # Set it to the location code that matches the received location
                for k,v in self.locations.items():
                    if v == loc:
                        return k 
            else:
                print("TESTESTEST")
                raise(ValueError(f"{loc} is not a valid location"))


    def get_forecasts(self, params) -> str:

        """Provide the forecast for a specific location up to a # of days."""

        # For maximum compatibility we allow some leeway for mixing up location names and location codes, as "Location" was not clearly defined in the spec
        if "Location" not in params and  "LocationCode" not in params and "LocationName" not in params:
            return self.give_error("MISSING PARAMETER")
        else:
            loc = params.get("Location", params.get("LocationCode", params.get("LocationName")))
            try:
                location_code = self.locations_error_correction(loc)
            except Exception as e:
                return self.give_error("UNKNOWN LOCATION")

        additional_days = params.get("AdditionalDays", 0)
        
        if additional_days > 14 or additional_days < 0:
            return self.give_error("INVALID DAYS")

        condition_names = params.get("ConditionNames", None)

        loc_forecasts = self.forecasts[location_code]

        response_fcs = {}

        # additional_days+1 since default is to only give today
        for day_num in range(additional_days+1):
            day = (date.today() + tdelt(days=day_num))
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
            
            response_fcs[str(day_num)] = conditions
        
        # return result
        return messages.format_message(
            message_type = "Locations Response",
            Location = location_code,
            NestedData = response_fcs
        )

    def grant_auth(self, params, duration: int = 60) -> str:
        """Check if the password matches one of an authorized user,
        then generate & store a temporary authorization code.
        Provide that & the expiry time to the user.
        """
        self.clean_auth()

        try: 
            password = params["Password"]
        except (TypeError,KeyError):
            return self.give_error("MISSING PARAMETER")
        
        if password not in self.accepted_passwords:
            # Realized none of our errors really make sense if someone
            # without auth tries to get it. Closest match.
            return self.give_error("NEED AUTH")
        # Always generates, in case someone wants to refresh their authcode
        # generate an authcode
        authcode = ''.join(random.choices(string.ascii_letters+string.digits, k=6))
        # generate an expiry time, 1 hr by default
        expireTime = dt.now()+tdelt(minutes=duration)

        self.authcodes[authcode] = expireTime

        return messages.format_message(
            message_type = "Auth Response",
            Code = authcode,
            ExpiryTime = int(expireTime.timestamp())
        )

    def append_forecast(self, authcode: str, params: dict) -> str:
        """If user is authenticated, appends the day's conditions to the next open date
        for a location.
        """
        self.clean_auth()

        # For maximum compatibility we allow some leeway for mixing up location names and location codes, as "Location" was not clearly defined in the spec
        if "Location" not in params and  "LocationCode" not in params and "LocationName" not in params:
            return self.give_error("MISSING PARAMETER")
        else:
            loc = params.get("Location", params.get("LocationCode", params.get("LocationName")))
            try:
                location_code = self.locations_error_correction(loc)
            except Exception as e:
                return self.give_error("UNKNOWN LOCATION")

        conditions = {}
        for c in CONDITION_TYPES:
            if c in params:
                conditions[c]=params[c]
        
        if not set(CONDITION_TYPES).issubset(conditions):
            return self.give_error("MISSING PARAMETER")
        if authcode not in self.authcodes:
            return self.give_error("NEED AUTH")
        if len(conditions) < len(CONDITION_TYPES):
            return self.give_error("MISSING PARAMETER")
        for cond in conditions:
            if cond not in CONDITION_TYPES:
                return self.give_error("INVALID FIELD")
        
        # find next unset day
        loc_forecasts = self.forecasts[location_code]
        next_day = date.today()
        while next_day in loc_forecasts:
            next_day += tdelt(days=1)

        # adds forecase
        self.location_forecasts[next_day] = conditions.copy()

        return messages.format_message(
            message_type = "Append Forecast Data Response",
            Location = self.locations[location_code],
            Date = next_day,
            **conditions
        )


    def edit_forecast(self, authcode: str, params) -> str:
        """Updates the forecast on a given date with those conditions."""
        self.clean_auth() # to ensure authcode is fine
        
        # For maximum compatibility we allow some leeway for mixing up location names and location codes, as "Location" was not clearly defined in the spec
        if "Location" not in params and  "LocationCode" not in params and "LocationName" not in params:
            return self.give_error("MISSING PARAMETER")
        else:
            loc = params.get("Location", params.get("LocationCode", params.get("LocationName")))
            try:
                location_code = self.locations_error_correction(loc)
            except Exception as e:
                return self.give_error("UNKNOWN LOCATION")

        conditions = {}
        for c in CONDITION_TYPES:
            if c in params:
                conditions[c]=params[c]
        forec_date = params["Date"]

        if authcode not in self.authcodes:
            return self.give_error("NEED AUTH")
        for cond in conditions:
            if cond not in CONDITION_TYPES:
                return self.give_error("INVALID FIELD")
        
        if forec_date not in self.forecasts[location_code]:
            return self.give_error("INVALID FIELD")

        current_forecast = self.forecasts[location_code][forec_date]

        old_conds = {}
        new_conds = {}
        for cond_name,cond_val in conditions.items():
            old_conds[cond_name] = current_forecast[cond_name]
            #In order to account for issues where server and client might disagree on whether something is a float or an int
            new_conds[cond_name] = type(current_forecast[cond_name])(cond_val)
        
        current_forecast.update(new_conds)
    
        return messages.format_message(
            message_type = "Edit Forecast Data Response",
            Location = self.locations[location_code],
            NestedData = {"Old": old_conds, "New": new_conds}
        )

    def add_location(self, authcode: str|None, params: dict[Any]) -> str:
        """Updates the locations dict with a new location."""
        self.clean_auth() # to ensure authcode is fine
        if authcode is None:
            return self.give_error("MISSING PARAMETER")
        elif authcode not in self.authcodes:
            return self.give_error("NEED AUTH")
        
        if "LocationCode" not in params:
            return self.give_error("MISSING PARAMETER")
        elif "LocationName" not in params:
            return self.give_error("MISSING PARAMETER")
        else: 
            loc_code = params["LocationCode"]
            loc_name = params["LocationName"]
        
        self.locations[loc_code] = loc_name
        self.forecasts[loc_code] = {}
    
        return messages.format_message(
            message_type = "Append Location Data Response"
        )

    def give_error(self, error_code: str) -> dict:
        """Given an error code, passes back an error response with the
        appropriate message.
        """
        
        if error_code not in ERROR_DICT:
            error_code = "MISC ERROR"

        return messages.format_message(
            message_type = "Error Message",
            ErrorCode = error_code,
            Message = ERROR_DICT[error_code]
        )
        

    def clean_auth(self):
        """Helper Function. Removes expired authcodes."""
        now = dt.now()
        delete_keys = []
        for code, expiry in self.authcodes.items():
            if now >= expiry:
                delete_keys.append(code)

        for code in delete_keys:
            del self.authcodes[code]

    def generate_day(self) -> dict:
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

    def generate_forecast(self,days = 15):
        forecast = {}
        for i in range(days):
            day = date.today() + tdelt(days=i)
            # forecast[day.isoformat()]=self.generate_day()
            forecast[day]=self.generate_day()
        return forecast

def main() -> None:
    ap = argparse.ArgumentParser(description="Project 1 UDP server")
    ap.add_argument("--host", default="0.0.0.0", help="address to bind (default: all)")
    ap.add_argument("--port", type=int, default=9000, help="port to bind (default: 9000)")
    args = ap.parse_args()

    # SOCK_DGRAM is UDP. There is no listen() and no accept() — no connections exist.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    server = WEP_Server()

    print(f"listening on {args.host}:{args.port} (ctrl-c to stop)", flush=True)

    try:
        while True:
            # Re
            # 65535 is the largest a UDP datagram can be (about 65 KB of payload).
            # A message bigger than that cannot be sent at all, so if your protocol
            # can produce one, your spec has to say what the sender does instead.
            data, addr = sock.recvfrom(65535)
            reply = server.handle(data, addr)
            if reply is not None:
                sock.sendto(reply, addr)
                print(f"  -> {len(reply)} bytes to {addr[0]}:{addr[1]}", flush=True)
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
