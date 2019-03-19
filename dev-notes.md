Dev-Notes
=========

## Required Features

- Store list of routes, stations, timings
- Store user routes (ie. what the route/trip a user takes every day: Bramalea <-> Union)


## Definitions

- A route consists of a Depart Station code and an Arrival Station code.


## GO API
---------

### Check Eligibility

#### Request
POST https://secure.gotransit.com/service/EligibilityService.svc/CheckEligible

Payload:
`{"dateString":"03082019","arrivalstationCode":"UN","tripNumber":"3806","lang":"en"}`

#### Response
```json
{"CheckEligibleResult":{"Reason":"This trip is not eligible because it's arrival at your destination was delayed by less than 15 minutes.","ResultType":2,"StatusCode":200}}
```