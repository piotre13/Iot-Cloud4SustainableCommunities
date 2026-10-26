# Mock exam - IoT and Cloud for sustainable communities

Time: 90 minutes. Multiple choice: +1 correct, 0 not answered, -0.5 wrong. Open questions: max 5 each. Coding: max 16.

## Part 1 - Multiple choice (6 questions)

**Q1.** Class `Device` is extended by `Sensor`, which is extended by `TemperatureSensor`. Which statement is correct?
- A. `TemperatureSensor` inherits only from `Sensor`, not from `Device`
- B. `TemperatureSensor` inherits the attributes and methods of both `Sensor` and `Device`
- C. Python does not allow more than one level of inheritance
- D. `Device` inherits from `TemperatureSensor`

**Q2.** At which layer of the ISO/OSI model does the IP protocol operate?
- A. Data link
- B. Network
- C. Transport
- D. Application

**Q3.** In a smart-home deployment, which of the following MQTT topic filters is NOT valid?
- A. `smarthome/+/kitchen/temperature`
- B. `smarthome/#`
- C. `smarthome/#/temperature`
- D. `+/+/+/humidity`

**Q4.** Which statement correctly compares HTTP and MQTT?
- A. HTTP is asynchronous publish/subscribe, MQTT is synchronous request/response
- B. Both are synchronous request/response protocols
- C. HTTP is synchronous request/response, MQTT is asynchronous publish/subscribe through a broker
- D. HTTP needs a broker, MQTT does not

**Q5.** Which statement about microservices (compared with a monolithic application) is correct?
- A. They are harder to build and release independently
- B. Each service can be built, tested and released rapidly and independently
- C. They cannot communicate over the network
- D. They must all be written in the same language and share one process

**Q6.** Which is a correct SenML JSON message for a temperature of 21.5 Celsius degrees measured in the kitchen?
- A. `{"bn": "kitchen", "bt": 1791970000, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 21.5}]}`
- B. `{"bn": "kitchen", "bt": 1791970000, "e": {"n": "temperature", "u": "Cel", "t": 0, "v": 21.5}}`
- C. `<senml><n>temperature</n><v>21.5</v></senml>`
- D. `{"kitchen": "temperature = 21.5 Cel"}`

## Part 2 - Open questions (5 points each)

**Q7.** Describe the three MQTT QoS levels and the characteristics (delivery guarantee, overhead, duplicates) of each. Give one smart-home use case for QoS 0 and one for QoS 1 or 2.

**Q8.** Compare JSON and XML as data formats for web data exchange: list the requirements a data format should satisfy and the pros and cons of each of the two.

## Part 3 - Coding (16 points)

**Q9. Room comfort service.** Write a RESTful web service in Python with CherryPy, object-oriented, that answers with JSON.

The service receives the temperature (degrees Celsius) and the relative humidity (percent, 0-100) of a room and returns a comfort label and the suggested HVAC command. Hard-coded rules, checked in this order:
1. temperature below 18: label `too_cold`
2. temperature above 26: label `too_hot`
3. otherwise, humidity above 60: label `too_humid`
4. otherwise: label `comfortable`

The HVAC is a heater, as in the course project: the suggested command is `"ON"` when the room is `too_cold`, `"OFF"` in all other cases.

Response example:
```
{"temperature": 28, "humidity": 45, "comfort": "too_hot", "hvac_command": "OFF"}
```

Requirements:
- choose the most suitable HTTP method(s) and the way to pass the input (path, query, body) and justify your choice in one sentence;
- the logic must be in a class (OOP); the web service uses the CherryPy `MethodDispatcher`;
- missing, non-numeric or out-of-range input must give an error status code with a JSON message;
- port is 8080;
- write one example URL (or request) and the corresponding response.

Marking scheme: see the solution file.
