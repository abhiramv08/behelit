#TODO: each client will contact a primary server for reqs
#on put, primary will update its replica and send puts to other servers
#also order it (check if the user clock = timestamp-1)
#then increment the server clock (map: user to clock)
#on get, primary just returns latest data