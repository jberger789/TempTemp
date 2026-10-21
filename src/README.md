# Implementation

> Replace this file with instructions for **your** implementation.
>
> Your partner group has to run this in Phase 4 without asking you anything and without reading your source. Write it for them. Remember that while the network protocol you are implementing should be the same, your application interfaces can be wildly different -- one team might expect commands to be entered as text in a terminal style client while another team might assume command line arguments are provided for each request. That is fine!

## Requirements

<!-- e.g. Python 3.10+, no third-party packages -->
Should probably work on Python 3.10+, tested on Python 3.14.8

## Running the server

```sh
python3 src/server.py --port 9000
```

## Running the client

```sh
python3 src/client.py --host <server ip> --port 9000
```

## Example session
<!-- Paste a short transcript: what you typed, what came back. -->
Type queries as they appear in spec v2 -  
`"Message Type" | "Auth Code" (optional) | "Parameter Name"_"Parameter type"_"Parameter value"`  
with a ";" between Parameters.

Responses will be printed as the raw response message, and a (slightly) more legibly
formatted response.  
You do **not** need to include all parameters when the spec provides a default value.
For example:

`Locations Request ||` (ask for all locations), is successfully responded with
```
Raw Response: Locations Response||LocationDictionary_MS_(BOS->Boston,,NYC->New York,,TKY->Tokyo,,SGP->Singapore,,LAX->Los Angeles,,DET->Detroit)
Message Type: Locations Response
Message Parameters: {'LocationDiction': {'BOS': 'Boston', 'NYC': 'New York', 'TKY': 'Tokyo', 'SGP': 'Singapore', 'LAX': 'Los Angeles', 'DET': 'Detroit'}}
```
And using a more formal `Locations Request || Limit_I_2` (ask for the first 2 locations)
is responded with
```
Raw Response: Locations Response||LocationDictionary_MS_(BOS->Boston,,NYC->New York)
Message Type: Locations Response
Message Parameters: {'LocationDiction': {'BOS': 'Boston', 'NYC': 'New York'}}
```
We can get the forecast data now that we have locations.
```
> Forecast Request || Location_S_BOS;ConditionNames_LS_(Temp,,Desc,,PChance); AdditionalDays_I_2
Raw Response: Locations Response||Location_S_BOS;0/Desc_S_Storms;0/PChance_I_41;0/Temp_F_60.3;1/Desc_S_Sunny;1/PChance_I_49;1/Temp_F_63.2;2/Desc_S_Cloudy;2/PChance_I_40;2/Temp_F_57.1
Message Type: Locations Response
Message Parameters: {'Location': 'BOS', 'NestedData': {'0': {'Desc': 'Storms', 'PChance': 41, 'Temp': 60.3}, '1': {'Desc': 'Sunny', 'PChance': 49, 'Temp': 63.2}, '2': {'Desc': 'Cloudy', 'PChance': 40, 'Temp': 57.1}}}
```
Telling us on day 0 (today) it'll be stormy, with a 41% rain chance and temperature of
60.3 degrees F.

We predefine 3 passwords to try: `password123`,`XKCD`, and `123!/x`.  
Using an incorrect password to try and get an auth code:  
```
> Auth Request||     Password_S_ABCD
Raw Response: Error Message||ErrorCode_S_NEED AUTH;Message_S_Insufficient authorization provided for the attempted action.
Message Type: Error Message
Message Parameters: {'ErrorCode': 'NEED AUTH', 'Message': 'Insufficient authorization provided for the attempted action.'}
```
Using a correct password:
```
> Auth Request||                          Password_S_XKCD
Raw Response: Auth Response||Code_S_89Np32;ExpiryTime_I_1792549718
Message Type: Auth Response
Message Parameters: {'Code': '89Np32', 'ExpiryTime': 1792549718}
```
We can then use that auth code (will not be the same for a user) to edit forecast
information.
```
> Edit Forecast Data Request|89Np32|Location_S_BOS; Date_D_2026-10-20;Temp_F_58;Desc_S_Sunny;PChance_I_99
Raw Response: Edit Forecast Data Response||Location_S_Boston;Old/Desc_S_Storms;Old/PChance_I_41;Old/Temp_F_60.3;New/Desc_S_Sunny;New/PChance_I_99;New/Temp_F_58.0
Message Type: Edit Forecast Data Response
Message Parameters: {'Location': 'Boston', 'NestedData': {'Old': {'Desc': 'Storms', 'PChance': 41, 'Temp': 60.3}, 'New': {'Desc': 'Sunny', 'PChance': 99, 'Temp': 58.0}}}
```
Calling Forecast Request to confirm the changes shows they were successful:
```
> Forecast Request || Location_S_BOS;ConditionNames_LS_(Temp,,Desc,,PChance); AdditionalDays_I_2
Raw Response: Locations Response||Location_S_BOS;0/Desc_S_Sunny;0/PChance_I_99;0/Temp_F_58.0;1/Desc_S_Sunny;1/PChance_I_49;1/Temp_F_63.2;2/Desc_S_Cloudy;2/PChance_I_40;2/Temp_F_57.1
Message Type: Locations Response
Message Parameters: {'Location': 'BOS', 'NestedData': {'0': {'Desc': 'Sunny', 'PChance': 99, 'Temp': 58.0}, '1': {'Desc': 'Sunny', 'PChance': 49, 'Temp': 63.2}, '2': {'Desc': 'Cloudy', 'PChance': 40, 'Temp': 57.1}}}
```
etc. etc.
## Known limitations
<!-- Anything unfinished or deliberately out of scope. Honesty here is free marks. -->
During implementation, it became apparent that the order errors were checked in was
patently absurd. The specified ordering had parameters (An unknown location) being
evaluated before the message type was even known!  
We opted to not use this particular ordering, as it is much easier to check for
parameter mismatches *after* the higher level error possibilities have been evaluated.

We had discussed the possibility of both including the possibility of Celsius 
temperatures, and of time zone conversion for queries where the client is in a 
different time zone.  
While we likely could've fashioned a time zone converter using local date/time 
differences, we ran out of time to implement it.   
Celsius would have required an additional field in temperature-related requests that
was not in spec (which we ran out of time on).