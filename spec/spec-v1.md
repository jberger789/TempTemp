# Protocol Specification — v1

**Protocol name: Weather Servicing Protocol**
**Group members: Joshua Berger, Jordan Stier**
**Date: 9/23/2026**
---

## 1. Purpose and scope
Weather Servicing Protocol (WSP) allows the client to look up upcoming weather conditions for a named location. A client can discover locations available in the database and request a list of available conditions for a specific location. When seeking the weather data itself, a client may simply request the data for all conditions for a location for the next seven days, or specify a specific set of conditions and/or a specified span of days for which data should be returned. WSP does not allow clients to request weather conditions for a location not in the database, nor utilize non-name location information such as Latitude-Longitude coordinates.

## 2. Communication pattern
The client speaks first in each interaction. Assuming all requests are received, every message is responded to, either with a “confirmation of reception” meta-message, or with a message transmitting information requested by the client. Parties retain state on a given session, until close. The server retains the interaction’s state, so as to properly transmit specific condition data to the client after a location/duration is specified. The client retains state to remember past messages it sent in a series of iterative messages.

State Transition Diagram:

![The Server State Transition Diagram](/s1-server.jpg)

![The Client State Transition Diagram](/s1-client.jpg)

## 3. Message types
| Type | Direction | Purpose | Fields |
|:--|:--|:--|:--|
|ConnEsta (0)| client → server |Requests a connection with the server|AutoEnd (1b)|
|ConnConf (1)| server → client |Confirms the connection with the client|Confirmation Status (1b), AutoEnd (1b)|
|CitySearch (2)| client → server |Search for cities in the server’s database|Region (1B), ReturnLimit (1B), Regex (var)|
|SearchRslt (3)| server → client |Returns a list of cities matching a City|Status (1b), Cities[] (var)|
|WthrReq (4)|client → server|Requests all available weather data for a specific city over the next seven days|CityName (var)|
|WthrRep (5)|server → client|Returns all available weather data for a specific city over the next seven days|Status (1b), StartDate (var), WeatherFlags[] (var), WeatherData[Days[]] (var)|
|SuggReq (6)| client → server |Requests weather for a specified city over a specified number of days|NumDays (5b), CityName (var)|
|SuggRep (7)| server → client |Suggests available types of weather conditions, given the city and days|Status (1b), WeatherFlags[] (var)|
|FullReq (8)| client → server |Client response after server provides available conditions|WeatherFlags[] (var)|
|FullRep (9)| server → client |Server response with each day’s conditions for a city over the specified number of days|Status (1b), WeatherData[Days[]] (var)|
|EndReq (10)| client → server |Request to manually dissolve connection||
|EndRep (11)| server → client |Confirmation of connection dissolution|Status (1b)|
|ErrRep (12)|server → client|Error response when malformed request received by the server|ErrCode(8b), ErrDesc(var)|

Field Descriptions:

0: AutoEnd: Automatically end the connection after 1 request-response series (does not include connection establishment).

1: Confirmation Status: 0 if connection has been successfully established. 1 for any error that prevented connection establishment.

   AutoEnd: Confirmation if this connection will automatically end after 1 request-response series.

2: Region: Encodes what region to search in.

   ReturnLimit: Maximum number of results to return.

   Regex: A Regular Expression to search for.

3: Status: 0 if no issues, 1 if any issue was encountered.

   Cities[]: A list of cities matching the conditions asked for by (2).

4: CityName: A String of the name of a city.

5: Status: 0 if no issues, 1 if an issue was encountered (eg no such city exists).

   StartDate: A String of the date to begin the response at.

   WeatherFlags[]: A list of the conditions being shown.

   WeatherData[Days[]]: A 2-dimensional list. Each row is a specific condition, each column is a day, and each index is a specific condition on a specific day.

6: NumDays: The number of days to request weather for.

   CityName: A String of the name of a city.

7: Status: 0 if no issues, 1 if any issue was encountered.

   WeatherFlags[]: A list of available conditions.

8: WeatherFlags[]: A list of conditions the client requests to see.

9: Status: 0 if no issues, 1 if an issue was encountered.

   WeatherData[Days[]]: A 2-dimensional list. Each row is a specific condition, each column is a day, and each index is a specific condition on a specific day. There is no need for WeatherFlags in this reply since the client already knows which conditions are being sent over from (8).

10:

11: Status: 0 if no issues dissolving connection. 1 if any issues were encountered.

12: ErrCode: an 8 bit integer error code.

    ErrDesc: a String description of the error encountered.


## 4. Message format
	Message metadata is transmitted in binary. Message payloads are transmitted in text, though not necessarily designed to be fully human readable. Requests always follow the following format:

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |  VERSION              |    TYPE   |  LENGTH   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |            LENGTH                 |  TRANSID  |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |  TRANSID  |                                   |
    +--+--+--+--+                                   |
    |                    PAYLOAD                    |
    /                                               /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Where:
* VERSION = An 8 bit integer code for the current version of WSP being used.
* TYPE = a 4 bit integer code for each message type specified in part 3.
* LENGTH = a 16 bit integer specifying the length of the entire packet (header + contents) in bytes, rounded up.
* TRANSID = an 8 bit integer specifying which transaction this is a part of, so that both sides of the transaction can handle multiple requests made from 1 client without confusion. For connection establishment, termination, and error handling, this field is always 0. In other transactions, it is a unique number for each series of requests/responses.
* PAYLOAD = A variable length payload, containing the fields listed in each request.

The Header Metadata is fixed to always be 36 bits. Within the payload, fields of variable length are always prefixed with a 2-byte length subfield (in # of bytes) to delineate them when the length could potentially be ambiguous. Fields of fixed length do not need this, as the message type informs what fixed length flags are present, and in what order.

For example, a connection confirmation message, automatically ending after 1 request-response series, without errors, will have the following format:

```
Version: 1 Type: 1 Length: 5 TransID: 0 Status: 0 AutoEnd: 1
```

A client request for a list of no more than 10 cities in region 1 (eg US Northeast) with containing the word “New”:

```
Version: 1 Type: 2 Length: 10 TransID: 1 Region: 1 ReturnLimit: 10 Regex:Length: 3 RegEx: “New”
```


## 5. Error handling
The connection has a very specific message flow, and while there are multiple possible requests after connection is established, it is possible for the client to send the wrong type of message at a specific time, such as by asking for something as a first question (such as FullReq) that requires prior state, or by sending an “opener request” (such as CitySearch) after a process that requires a series of requests has been initiated, but before it has concluded.
In these instances, the server responds with an error to convey “not enough information” or “out of turn request.”
The client can also send improper messages that aren’t current regardless of the sequence, such as malformed or nonsense expressions, or requesting information that is out-of-scope, such as requests for weather for cities not logged in the database, or for a number of days exceeding the maximum. In the former case, the server should respond with an error to convey it “cannot parse information,” and in the latter case it should provide an “out-of-scope” error.

## 6. Edge cases and failure modes
Malformed messages will always result in an error - this ensures that the client should always expect to receive a response to every sent message, eliminating any situations where the client is waiting indefinitely on a response that may not be coming (i.e. due to the server not running). This includes cases where the message is requesting data that does not exist (i.e. for cities not in the database, weather conditions that are not available, empty keys, etc.). The main reason for this is that there are message types available to the client via which they may request information on the cities and conditions available on the server, so there is no reason they should ever be sending requests for data regarding invalid cities or conditions.
WSP does not implement messages larger than one datagram, as weather data is easy to represent concisely, so the information transmitted via this protocol should never come close to exceeding this amount. Any such scenarios which might be imagined in which larger amounts of data might appear desirable (i.e. radar maps of weather data) are out of scope and should be handled by a different protocol.
WSP expects the server to handle per-client state, tracked on a per message basis via the TRANSID attribute, which prevents issues from arising when multiple clients attempt to contact the server simultaneously, or when one client sends multiple transactions to the server.
The final possible edge case is what happens when a message is sent by a client on one day but not received by the server until the following day. In this case, the day that a message is received by the server is used (according to the server’s local timezone), and the server always specifies which days the weather data being sent corresponds to prevent confusion.

## 7. Design decisions
The key choice on which the designers’ opinions differed was to design WSP as a connection-based or connectionless format. The latter allows for less overhead, but the former allows for greater flexibility in interactions. It was ultimately decided to structure WSP as a connection-based protocol to allow for lookups prior to a desired transaction due to the likely event that the client would not be aware of what cities are logged in the database, nor what condition types are available for each city in a given date range.
That likely event also forced the designers to consider implementation of a secondary lookup feature, and a way to fetch the set of conditions available. In WSP, these are implemented for convenience, but it is entirely plausible for another team to lack these features. In that case, requests could be made using a blind request, where it is unknown if a city exists in the database, and automatically passing all available weather data to the client. The designers of WSP considered the possibility of a large number of faulty requests due to uninformed users to be of more concern than the excess overhead transactions would have without these convenience features, due to the wait times and additional user-input required in the former case.
The WSP designers also decided to include a status field in all server messages, despite an additional error response, to allow for additional information. Depending on the specificity of error response codes, it can be difficult to understand what the exact issue is. Utilizing the transaction ID field would not necessarily be helpful due to the fact that a chain of requests and replies can be in the same transaction. A status indication on a specific type of reply, as well as a general error reply, can further narrow down what went wrong in the transaction, by highlighting which message was problematic. Another team might omit this field, but would have to be certain to include thorough error descriptions and statuses in their version of an ErrRep message. 