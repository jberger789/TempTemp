# Protocol Specification — v2 (merged with partner group)

**Protocol name: Weather Service Protocol** 

**Our group: Joshua Berger, Jordan Stier**

**Partner group: Ethan Richardson, Anieesh Saravanan, Raina Jacob**

**Date: 09/30/2026**
---

## Changes from v1
| What we disagreed on | Our v1 said | Their v1 said | What v2 says | Why |
|:--|:--|:--|:--|:--|
|Connection|Required connection|Required connection|Connectionless for typical messages, connectionless but stateful for privileged messages|Messages are independent enough that it would be needlessly heavy to hold a connection, and state is only necessary for a privileged request.|
|Message format|Technical, packet based|Relatively standard plaintext `GET` messages|Plaintext `GET` messages|Likely easier to implement in a high-level language like python|
|Filter by conditions|Filtered by conditions|Not filtered by conditions|Filtered by conditions|Allows more choice for users; all conditions now must be available|
|Forecast timezone|Local to server|Local to server|Provide timezone in server status |Allows client to adjust for timezones in such edge cases|
|Separators|Length separates, client needs to parse|Delimiter|Delimiters|Easier for client to parse|
|Errors| Specific messages+Non-Error Response Returned |All or nothing|Specific messages, all or nothing|Connectionless, knowing which prior request caused an error is trivial (always the previous)|
|Possible locations|Allows for unlimited # of cities|Limited premade list of cities (dictionary-2 letter codes)|Initial longer list (3 letter codes) with ability to add more locations|Regex search is complex and takes a lot of space, a smaller dictionary allows for quick lookups|
|Status field returned|Status field returned|Status field not returned|Status field not returned|In a connectionless format, the proper responses are only sent on success anyways, making this redundant|
|Code field|Somewhat similar to TransactionID|No code field|A password to allow clients to add additional locations/updates to the conditions lists. User sends password, gets back generated code that it can use to modify|Adds additional state and support for “intermediate” weather users|
|Days in forecast |Default to week or specified number of days|Yesterday, Today, Week|Default of today, include a number to ask for that number of days starting from today up to 2 weeks|More flexibility than presets|
|Weather condition return|Specified by day|Specified by week|Conditions returned on a day by day basis with header info per day|Datagram is large enough to accommodate for headers per day|



## Still unresolved after class
We left open which locations to use in the database accessed, which may make the implementations have slightly different scopes of applicability, but the core feature set will be the same, and this would be unlikely to negatively affect end-users as clients can always request a dictionary of codes and their corresponding locations.

We also decided to allow for client freedom in features, as the protocol primarily specifies server responses to client requests, and not how the client should utilize said responses. For example, a client geared towards non-American users could parse responses and automatically convert units from US customary to metric, or on launch could silently request server status without notifying the end user to retrieve the server’s timezone, and adjust responses when relevant.

Defining passwords for privileged users–what they can contain, whether or not it's permanent, if passwords are unique to each privileged user–went unspecified because we ran out of time. This may cause problems with compatibility and interoperability during Phase 4.

We did not specify the order in which location results would be sorted.

## 1. Purpose and scope
Weather Service Protocol (WSP) makes available a method for a client to request weather information from a server for forecasts as far as two weeks from the present for a supported location code. A client may request server info to calculate time zone adjustments, or input their password to receive clearance to edit and append the server’s weather and location data.

## 2. Communication pattern
Interactions are initiated by the client. The client makes requests of the server using the message format defined in the next section, and receives plaintext messages in response with the desired data. 
Interactions are connectionless, with a single request returning a single reply and little else. Interactions that require authoritative privileges remember state while remaining connectionless, by taking a predefined password from the client and returning a temporary code to be utilized with `edit` or `append` requests. This allows for heightened security compared to a fully connectionless and stateless system.
The server cannot send the client anything without the client first requesting something, but in the case of an error, the server will not send the client what was expected, and sends an error message instead.

## 3. Message format
The messages should follow the high level format of 
	`Message Type|Authorization Code|Parameters`
Where:
 Message Type is the type of message, as specified in section 4 (ex “Status Request”, “Forecast Request”, “Auth Response”, etc.) [required]
Authorization Code the code provided in Auth Response and needed for the Edit Data Requests [Optional, may be left blank]
Parameters are the fields specific to the message type [Optional,may be left blank] 

These should be encoded as a string, with the different fields separated by `|` (i.e. the pipe character).  Every message should contain two pipes, even if only the Message Type field is set.

The Parameters field is the most important field, and should be formatted as a semi-colon (`;`) separated list, with each list element following the format, each separated by underscores (`_`).
	VariableName_VariableType_VariableValue
The variable name should match the specification in section 4
The variable type should be either a single letter: `I` for integers, `F` for floats, `S` for string, `D` for dates (formatted YYYY-MM-DD), `T` for times (formatted HH:MM) or two letters for lists and maps (i.e. dictionaries): ex LS for a list of strings, MI for a map/dictionary of ints, etc. For lists and dictionaries, the Variable Value in that case should be enclosed in parentheses, with list items separated by double commas (`,,`) and dictionary items as a list of tuples (with the key->value items arrow (`->`) separated).  For lists of sets of values of varying types, they should instead be treated as separate variables but formatted with names in the format Outer/Inner (for example, for a set of conditions for multiple days, the names should look like `0/Temp`, `0/Humid`, 1/Temp, etc. or when updating data as `Old/Temp`, `Old/Desc`, `New/Temp`, etc.).
The variable value should be interpretable as the specified value (i.e. something specified as an int should have a value that can be cast as an integer)

Notes:
- Leading and Trailing whitespaces are ignored
- Reserved characters
`|`,`;`,`_` are reserved in all cases and may not be used for values or names
`/` is reserved in Variable Names, but can be used in Variable Values
`,,` and `->` are only reserved in Variable Values of lists and maps, and may be used in other values or in Variable Names

###Examples:


`Locations Request||Limit_I_3`
`Locations Response||LocationDictionary_MS_(BOS->Boston,,NYC->New York City,,ATL->Atlanta)`


`Forecast Request||Location_S_BOS;ConditionNames_LS_(Temp,,Desc,,PChance);AdditionalDays_I_1`
`Forecast Response||Location_S_BOS;0/Temp_F_52.4;0/Desc_S_Rainy;0/PChance_I_55;1/Temp_F_60.1;1/Desc_S_Sunny;1/PChance_I_10`


`Auth Request||Password_S_WrongPassword`
`Error Message||ErrorCode_S_MISC ERROR;Message_S_Incorrect Password`

`Auth Request||Password_S_password123`
`Auth Response||Code_S_1CX92FA;ExpiryTime_I_1790812947`

`Edit Forecast Data Request|1CX92FA|Location_S_BOS;Date_D_2026-10-01;Temp_F_60.1;Desc_S_Sunny;PChance_I_10`
`Edit Forecast Data Response||Location_S_BOS;Old/Temp_F_52.4;Old/Desc_S_Rainy;Old/PChance_I_55;New/Temp_F_60.1;New/Desc_S_Sunny;New/PChance_I_10`

`Append Location Data Request||LocationCode_S_NAR;LocationName_S_Narnia`
`Error Message||ErrorCode_S_NEED AUTH;Message_S_Insufficient authorization provided to take the requested action`


###Condition Definitions:

Desc - One word description of conditions (e.g. Sunny, Cloudy, Rainy, etc.)
Humid - Humidity (0-100%, float)
PChance - Precipitation Chance (0-100%, float)
PType - Precipitation Type (Rain, Snow, Sleet, N/A, etc.)
Temp - Temperature (Fahrenheit, float)
UV - UV Index (1 - 11+)
WDir - Wind Direction (one of the standard 16-point compass directions)
WSpeed - Wind Speed (in mph)

## 4. Message types
| Type | Direction | Purpose | Fields |
|:--|:--|:--|:--|
|Status Request|client → server|Request server status||
|Status Response|server → client|Provide server status, including current time and local date, if an administrator is active, and uptime|CurTime, LocalDate, AdminActive (True/False), Uptime (in seconds)|
|||||
|Locations Request|client → server|Request a dictionary of all available locations, up to a limit|Limit (Default -1, show all)|
|Locations Response|server → client|Provide a dictionary of available locations, up to the specified limit|LocationDictionary{}|
|Forecast Request|client → server|Request a location’s forecast over a specified number of days, defaulting to only today, up to today + two weeks in the future|Location, ConditionNames[] (Defaults to all if left blank), AdditionalDays(Default 0, Max 14)|
|Forecast Response|server → client|Provide a location’s forecast| Location, Day#/[Desc, PChance, PType, Temp, etc]|
|||||
|Auth Request|client → server|Provide authorization to gain the ability to upload and edit data|Password|
|Auth Response|server → client|Authenticate the client and, if successful, pass a temporary codeword and its expiration time to them for use when editing and uploading|Code, ExpiryTime|
|||||
|Append Forecast Data Request|client → server|Append a location’s conditions for the next unset day|Location, Desc, PChance, PType, Temp, etc|
|Append Forecast Data Response|server → client|Confirm if successful appendation and display the results|Location, Date, Desc, PChance, PType, Temp, etc|
|Edit Forecast Data Request|client → server|Edit a location’s conditions for a specific date in series|Location, Date, PChance, PType, Temp, etc|
|Edit Forecast Data Response|server → client|Confirm successful edit and display changes|Location, Old/[Desc, PChance, PType, Temp, etc], New/[Desc, PChance, PType, Temp, etc]|
|Append Location Data Request|client → server|Append a location to the location dictionary|LocationCode, LocationName|
|Append Location Data Response|server → client|Reception confirms successful appendation||
|||||
|Error Message|server → client|Provide a specific status code and error message if a previous request failed|ErrorCode, Message|

## 5. Error handling
An error is sent by the server if it cannot fulfill a certain request. For example, a request that contains an invalid message format, incorrect number of fields, an unsupported location, etc., will return an error. WSP also uses an all-or-nothing approach for receiving requests. If any part of the client’s message is invalid or results in an error, the server does not process any part of the request. The server will return an error response, and the client must try again by sending a new, valid request.


Error responses have the following format:

    `Error Message||ErrorCode_S_Error Code; Message_S_Error Detailed Description`

The error codes defined by WSP are shown below:

| Error Code           | Description                                                                                 |
| ---------------------| ------------------------------------------------------------------------------------------- |
| `MISSING PARAMETER`   | The request does not contain a required parameter.                              |
| `UNKNOWN LOCATION`   | The requested location code is not that of a supported location.                          |
|`PREEXISTING LOCATION`| The location to be added has the same code as another location. |
|   `INVALID DAYS`     | The requested number of forecast days is greater than 14.                                    |
| `INVALID UNIT`       | The UNIT value is not `F` or `C`.                                                           |                                       |
| `UNKNOWN MESSAGE`    | The message type is not supported by WSP.                                                   |
| `INVALID FORMAT`     | The message does not follow WSP format.                                                     |
| `INVALID FIELD`      | A field contains an unsupported/invalid value.                                              |                                                  |
| `NEED AUTH`          | Insufficient authorization provided for the attempted action.                                             |
|`MISC ERROR`| An error that does not fall in the above categories|


For example, if a client sends:

    Forecast Request||Location_S_XYZ

The server responds with:

    Error Message||ErrorCode_S_UNKNOWN LOCATION;Message_S_The requested location code is not that of a supported location.
    
If a message contains multiple errors, they are checked in the following order to prevent variance across multiple implementations:
1. `UNKNOWN LOCATION`
2. `INVALID FORMAT`
3. `UNKNOWN MESSAGE`
4. `MISSING PARAMETER`
5. `PREEXISTING LOCATION`
6. `NEED AUTH`
7. `INVALID UNIT`
8. `INVALID DAYS`
9. `INVALID FIELD`
10. `MISC ERROR`


## 6. Edge cases and failure modes

### Non-ASCII Text:
The protocol only supports ASCII characters defined in the message format. A message with non-ASCII characters will be rejected by the server as an invalid format.

### Invalid Number of Days:
If a client requests a forecast for more than 15 days (today and following two weeks), the server returns an `INVALID DAYS` error. If no number of days is specified, the server defaults to today.

### Date and Time
The server assumes the local date and timezone when providing weather forecast data. The server also provides its timezone information upon a Status Request so the client can account for the server's local time when interpreting the response.

### Message Received on Different Day
If a message is sent by a client on one day but received by the server on the following day, the server uses the date on which it receives the message, according to the server's local timezone. The server always specifies which days the weather data being sent corresponds to prevent confusion.

### Multiple Clients:
More than one client may communicate with the server at the same time. Each request is handled independently so that clients do not interfere with each other.

### Single-Datagram Messages:
WSP does not implement messages larger than one datagram, as weather data is easy to represent concisely, so the information transmitted via this protocol should fit within the UDP size limit. Any such scenarios which might be imagined in which larger amounts of data might appear desirable (i.e. radar maps of weather data) are out of scope and should be handled by a different protocol.

## 7. Design decisions
### Connectionless operations for ordinary requests

The original designs both had some concept of persistent state through interactions. One specification involved storing client locations, forecast durations, and temperature units throughout an active session. The other specification used a form of transaction state where a client could perform preliminary lookups followed by a series of associated requests.

For specification v2, we collectively decided that the WSP format should be connectionless instead. Requests for server information, locations, or weather data can be standalone and contain the information necessary for that specific operation. The server need not recall previous forecast requests from a specific client. This streamlines server operations by eliminating the need to create and close sessions just for weather information retrieval. Requests do not need to be influenced by earlier interactions.

The largest drawback of this decision is the client may need to repeat information like location or forecast duration between requests. However, these redundant fields are small, and maintaining a separate session for every client results in additional server state. It could theoretically cause disparities between the client and server regarding the state of interactions. Discovery features from the state-based design are kept as independent requests.

### Authorization based on minimal state

Specification v2 adds server state for clients who need authority to modify stored weather information. This is directed at clients such as weather stations, which may need to pull and push weather data to the server.

A client that desires modification privileges initially authenticates with the server and requests an authorization code. When the server generates a code, it stores the code so it can be validated in subsequent requests. The client can then include the code in an update request alongside location, condition, date, or other identifying data for new values to be stored. The server validates the code against its unexpired code storage before allowing modifications to take place. Code expiry prevents indefinite modification privileges and allows the server to dump unnecessary authorization states.

With this approach, the server only needs to store information to determine if a modification request is allowed. The code provides elevated permissions to clients across separate requests. A weather station may request a code and use that code repeatedly to deliver observations without having to keep a WSP connection open.

### Plaintext messages (non-binary header)

The original specifications had vastly different representations for messages. One format used human readable commands and fields, while the other used a binary header containing a version, message type, packet length, and transaction identifier followed by a payload of variable length. While the binary approach was extremely compact with data, it necessitated parsing on the bit level and length processing, which places unneeded burden on applications.

Specification v2 uses entirely plaintext messages. Weather requests and responses already contain relatively minimal control information, so we collectively decided that the space saved by a binary header was not justifiable for its added complexity. Plaintext messages are inherently easier to create and validate, especially in languages like Python.

Since standard requests do not involve a transaction across multiple messages, fields like the binary transaction identifier are less useful now. Requests can state operations and required values upfront. However, we still kept the idea that message boundaries must be explicit. Specification v2 clearly outlines delimiters and field structuring to make straightforward parsing possible.

### Limited discoverable locations

The original specifications had varying ideas for handling locations. One design supported an extended database of cities with search capabilities, while the other created a predefined dictionary of compact location codes. We collectively decided that the merged specification should support a limited location dictionary that clients are able to request from the server. This allows clients to discover supported locations without necessitating RegEx search or an unbounded location database, which could cause issues in data retrieval.

A client that is already aware of an acceptable location does not need to make any preliminary lookups. The location request mechanism is not required for a session, and is solely for search purposes. A limited location dictionary allows the server to validate locations through quick lookups and keeps requests and responses compact.

### Variable forecast duration without presets

One specification used limited forecast ranges like TODAY, WEEK, and YESTERDAY, while the other allowed requests to have varying forecast durations. We collectively decided on a numeric forecast duration beginning with the current day and limited to two weeks.

This provides clients with greater flexibility than presets, as it serves them exactly the number of days necessary. The maximum duration of two weeks places an upper bound on the amount of data able to be returned and ensures forecasts remain generally accurate.

### Response status information

One specification included status information in server responses, while the other was more dependent on error handling. We collectively decided to remove status fields from responses, relying solely on descriptive error messages, as in a connectionless setting it’s fairly trivial to deduce if an operation was successful. Descriptive error handling is especially important now that WSP facilitates both standard data requests and server data modification requests.