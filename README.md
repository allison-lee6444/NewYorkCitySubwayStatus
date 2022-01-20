# NewYorkCitySubwayStatus
This project is an alexa skill that checks the NYC Subway status. 

This skill uses the GTFS feed to capture every delays and service alerts that MTA posted, planned or unplanned. While some of the other skills stopped updating since October, this skill uses the newest GTFS format to get information directly from the MTA server. In other words, the alerts will be in-sync with what you would see on the MTA website at the moment.

Previously, the skills available used the old API feed, which the MTA ceased to support since October 2021. In order to access the real time service changes on the New York City Subway system in 2022 and onwards, I completed this project to allow Alexa users to receive accurate and up-to-date information.

# Installation
Please visit https://www.amazon.com/dp/B09QLM99Q9
# Usage
Once installed on your alexa device, say:
add the [line] train - add the requested line into memory, and check its status automatically when opened next time
delete the [line] train - delete the line from memory
delete all lines - clear memory
list all the lines - list all remembered lines
check the [line] train - check the status of the line without remembering it

# Credits
Special thanks to the author of NYCT-GTFS library. I learned a lot about GTFS formatting from their code. The library is located at https://github.com/Andrew-Dickinson/nyct-gtfs
