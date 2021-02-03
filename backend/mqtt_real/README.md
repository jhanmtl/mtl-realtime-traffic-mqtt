The script here was used for fetching and parsing realtime mqtt data from the sensors from the
City of Montreal's [Informations de circulation en temps réel](https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel)
page as part of its Open Data Initiative. The fetched and parsed data is then used in the visualizations of the dashboard.

Unfortunately, as of Jaunary 2021, these sensors seem to be offline. Considering that they were first installed as a 
pilot project in the 2017 ITS World Congress, this seems like a reasonable lifespan (4 years).

Therefore, to keep the dashboard supplied with meaningful data and exhibit the usage of MQTT protocols in realtime data
visualization, a separate script was written (see ../mqtt_sim/pub_sim.py) that simulates the topics that the original
sensors put out and then publishes them over the hivemq broker. 

These simulated topics are subscribed to by the collector script in ../mqtt_sim/collect_sim.py. These simulated sensor
data and topics are fetched, parsed, and subsequently fed into the dashboard.

It's unfortunate that the access to the original, real data is lost. However, the simulated data still serves as a 
valid replacement for the technological demonstration of integration mqtt, Dash, and Redis. 
