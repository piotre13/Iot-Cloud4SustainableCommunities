# Theory question bank

Answers to the multiple-choice questions are in the answer section at the end.

## Multiple choice

**1.** In Python, `class B(A)` and `class C(B)`. An instance of `C` calls a method defined only in `A`. What happens?
a) AttributeError  b) the method of A runs  c) it needs `super()` in C  d) it needs `A` imported in C

**2.** Which layer of ISO/OSI do TCP and UDP belong to?
a) Network  b) Transport  c) Session  d) Application

**3.** Which statement about TCP vs UDP is correct?
a) UDP guarantees ordered delivery  b) TCP is connection-oriented with retransmission  c) TCP has lower overhead than UDP  d) UDP uses a three-way handshake

**4.** SGML is:
a) a database language  b) a standard meta-language for defining markup languages  c) a JavaScript library  d) a transport protocol

**5.** Which statement about JSON is WRONG?
a) it is a lightweight data-interchange format  b) it is a markup language  c) it supports objects and arrays  d) it is language independent

**6.** Which HTTP method is idempotent and used to replace/update a known resource?
a) POST  b) PUT  c) CONNECT  d) none

**7.** Which status code means "resource created"?
a) 200  b) 201  c) 204  d) 301

**8.** A client sends a malformed JSON body. The best status code is:
a) 200  b) 400  c) 404  d) 500

**9.** Which URL is a correct GET request with two query parameters?
a) `http://host:8080/sensors&type=light?unit=lux`
b) `http://host:8080/sensors?type=light&unit=lux`
c) `http://host:8080/sensors?type=light?unit=lux`
d) `http://host:8080/sensors/?type=light;&unit=lux?`

**10.** In CherryPy, with `MethodDispatcher`, a class handles `GET` requests when:
a) it has a method `GET` and `exposed = True`  b) it has a method `index`  c) it uses `@cherrypy.expose` on `POST` only  d) it is mounted on port 80

**11.** Which is a RESTful URL design for the rooms of house 2?
a) `GET /getRooms?house=2`  b) `GET /houses/2/rooms`  c) `POST /rooms/get/2`  d) `GET /house2_rooms.php`

**12.** MQTT QoS 1 means:
a) at most once  b) at least once  c) exactly once  d) in order

**13.** In MQTT, `+` in a topic filter matches:
a) any number of levels  b) exactly one level  c) zero or one character  d) only numbers

**14.** Which filter is invalid?
a) `a/+/c`  b) `a/#`  c) `a/#/c`  d) `#`

**15.** A retained message is:
a) delivered twice  b) stored by the broker and sent to every new subscriber of the topic  c) encrypted  d) delivered only to the first subscriber

**16.** With a persistent session (clean session false / clean start false) a client that reconnects:
a) loses its subscriptions  b) keeps subscriptions and receives queued QoS 1/2 messages  c) becomes the broker  d) needs a new client id

**17.** Which statement correctly differentiates HTTP and MQTT?
a) both are broker based  b) HTTP request/response, MQTT publish/subscribe  c) MQTT is synchronous  d) HTTP is push only

**18.** Which fields identify a SenML measurement?
a) `bn`, `bt`, and a list `e` of `n`, `u`, `t`, `v`  b) `id`, `name`, `val`  c) `topic`, `qos`  d) `key`, `field1`

**19.** What is the purpose of the catalog in the smart-home project?
a) to store all measurements  b) service/device discovery: registry of houses, rooms, devices, thresholds, broker  c) to send Telegram messages  d) to replace MQTT

**20.** The ThingSpeak free account accepts updates at most every:
a) 1 s  b) 15 s  c) 5 min  d) 1 h

**21.** Where should a Telegram token or a ThingSpeak write key be stored?
a) in the source code  b) in a `.env` file kept out of git, loaded at startup  c) in the README  d) in the topic name

**22.** Which is a property of microservices?
a) one shared database and one deployable  b) small independent services, released independently  c) no network communication  d) hard to test

**23.** A monolithic application typically has:
a) easy independent scaling of parts  b) limited modularity and harder maintainability as it grows  c) many deployables  d) per-service languages

**24.** PaaS (Platform as a Service) provides:
a) raw virtual machines only  b) a platform to develop and deploy applications without managing the underlying infrastructure  c) finished software for end users  d) physical sensors

**25.** Which is true for JSON compared with XML?
a) JSON supports namespaces natively  b) JSON is usually more compact and easier to parse  c) JSON has XSLT  d) JSON requires closing tags

**26.** Why must a paho `on_message` callback not raise exceptions?
a) it would stop the broker  b) it can kill the client's network loop  c) it deletes the topic  d) it is asynchronous HTTP

## Open questions (key points in brackets)

1. MQTT QoS levels and their characteristics. [0 at most once, 1 at least once with PUBACK and possible duplicates, 2 exactly once with 4-step handshake; overhead grows; effective QoS = min(pub, sub)]
2. TCP vs UDP. [connection-oriented, reliable, ordered, flow/congestion control vs connectionless, no guarantee, low overhead, low latency; examples: HTTP/MQTT on TCP, DNS/CoAP on UDP]
3. The HTTP protocol and its main properties. [application layer, client/server, request/response, stateless, text-based, methods, status codes, headers, runs over TCP, resources identified by URL]
4. Requirements of data formats for web data exchange, JSON vs XML. [platform independent, readable, compact, easily parsed, nested structure, standard; JSON light/easy, XML verbose but schemas/namespaces]
5. REST principles and resource design. [resources as nouns in URLs, uniform interface via HTTP methods, stateless, representations (JSON), status codes; example `/houses/2/rooms/kitchen/thresholds`]
6. When to use GET, POST, PUT, DELETE (with safe/idempotent). [GET safe+idempotent; PUT idempotent; DELETE idempotent; POST neither, creates/commands]
7. MQTT topics and wildcards, retained messages, clean session, last will. [levels, `+` one level, `#` multilevel last; retained last value for new subscribers; session persistence; will on abnormal disconnection]
8. Explain publish/subscribe vs request/response and when each fits. [decoupling in space/time/sync, broker; many-to-many telemetry vs one-to-one queries and commands with immediate answer]
9. Service discovery with the catalog and why not hard-code addresses. [devices register; clients ask the catalog for broker, thresholds, rooms; add a house at runtime with no code change; REST endpoints GET/POST/PUT]
10. Microservices vs monolith, with the smart-home as example. [catalog, device connector, controller, adaptor, bot as separate processes; independent release/scale/failure isolation vs coordination, network, deployment complexity; monolith simple but not modular]
11. Describe the ThingSpeak adaptor (MQTT to REST). [subscribes to topics, maps topic to field, writes with API key from `.env`, respects 15 s between updates]
12. SenML: purpose and fields. [standard JSON measurement format; bn base name, bt base time, e list of entries with n name, u unit, t relative time, v value]

## Answers (multiple choice)

<details>
<summary>Show answers</summary>

1 b (inheritance is transitive) - 2 b - 3 b - 4 b - 5 b ("JSON is a markup language" is the wrong one) - 6 b - 7 b - 8 b - 9 b (first `?`, then `&`) - 10 a - 11 b (nouns, hierarchy, no verbs) - 12 b - 13 b - 14 c (`#` only last) - 15 b - 16 b - 17 b - 18 a - 19 b - 20 b (free plan, 15 s) - 21 b - 22 b - 23 b - 24 b - 25 b - 26 b

</details>
