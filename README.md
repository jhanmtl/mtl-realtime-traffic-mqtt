# mtl-realtime-traffic-mqtt


This project performs realtime IoT data fetching and visualization from 9 thermal and radar sensors embedded along 
Rue Notre-Dame by Montreal as a pilot project for the 2017 ITS World Congress. Data from these sensors are made
available as part of the City's Open Data initiative. Each sensor publishes traffic data in 60s intervals over the 
MQTT protocol. Details about the data source [can be found here](https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel).

The resulting dashboard displays vehicle speed, vehicle count, and vehicle gaptime reported by each sensor at 15 second
intervals. Focus is placed on clarity and interactivity. Users have the option of viewing historic data of each sensor,
choose the data type displayed, as well as compare sensor datas. Furthermore, each sensor location is cross referenced with 
existing live traffic cam feed to give user option of view live traffic conditions via video.

Check out the gif below, or better yet, [visit the live dashboard](http://54.237.57.126:8080/)!

![Alt Text](./data/gifs/update.gif)

**Unfortunately, as of Jaunary 2021, these sensors seem to be offline. Considering that they were first installed as a 
pilot project in the 2017 ITS World Congress, this seems like a reasonable lifespan (4 years).

Therefore, to keep the dashboard supplied with meaningful data and exhibit the usage of MQTT protocols in realtime data
visualization, a separate script was written (see ../mqtt_sim/pub_sim.py) that simulates the topics that the original
sensors put out and then publishes them over the hivemq broker. 

