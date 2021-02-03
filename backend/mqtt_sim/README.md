The scripts here performs two actions:

1. Since the original traffic sensors described in the City of Montreal's [Informations de circulation en temps réel](https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel)
    page have gone offline in Jaunary 2021, the pub_sim.py script simulates the data and topics of those original sensors and publishes
   them over the hivemq broker 
   
2. the collect_sim.py script performs fetching and parsing of these data for use in the visualizations of the dashboard.

