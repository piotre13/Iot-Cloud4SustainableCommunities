# Project proposal

*Italic text = hints / smart-home example: delete it in your proposal.*

## 1. Name of the use case

| | |
|---|---|
| Name of the use case | |
| Version no. | 1.0 |
| Submission date | |
| Team members (name, student ID) | 1. <br> 2. <br> 3. <br> 4. |

## 2. Scope and objectives

| | |
|---|---|
| Scope | |
| Objective(s) | |
| Domain(s) | |
| Stakeholder(s) | |
| Short description | |

*Example (smart home): scope = comfort and energy saving in a house; objectives = keep temperature and humidity inside user thresholds; domain = smart building; stakeholders = inhabitants, building manager; description = sensors publish measurements, a controller compares them with the thresholds stored in the catalog and switches the HVAC, the user is notified on Telegram.*

## 3. Diagram of the use case

*Draw actors and microservices and the links between them, labelling each link REST or MQTT (e.g. device connector -MQTT-> controller -REST-> catalog; controller -MQTT-> HVAC actuator; Telegram bot -REST-> catalog; ThingSpeak adaptor -REST-> ThingSpeak). Insert the image here.*

![diagram](diagram.png)

## 4. Complete description of the system

*Describe each microservice (what it does, its REST endpoints / MQTT topics, its configuration file), the data formats exchanged (JSON examples), how devices/users/contexts are added at run-time, and how the user interacts with the system.*

## 5. Desired hardware components

*Only among those the course can provide.*

| Device name | Quantity | Needed for... |
|---|---|---|
| | | |
| *Example: temperature/humidity sensor* | *2* | *measuring the room, published via MQTT* |
| *Example: relay / LED as HVAC actuator* | *1* | *switching heating/cooling from the controller* |
