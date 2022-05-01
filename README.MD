 # TODO
   1. Finish the Hints API
   2. Find a good host for the api # done
   3. Make an Image api that makes a new random foodle banner every 24hrs (same uri path)


# Guide to adding a new route
1. in the request function add 
`app.stats.LogRequest(request.full_path, *ROUTE CODE*)` if it doesnt have any uri arguments
if it does 
use ` app.stats.LogRequest(RemoveUriArguments(request, 'LIST THE ARGS HERE'), *ROUTE CODE*)`
`
but replace `*ROUTE CODE*` with the routes code 
2. guide to route codes
0-99: reserved for the base routes (e.g. /)
100-199  reserved for info routes (e.g. /routes, /stats and /version)
200-299: reserved for the game routes (e.g. win/lose)


