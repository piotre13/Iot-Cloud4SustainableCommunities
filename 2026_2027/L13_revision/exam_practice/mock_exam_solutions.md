# Mock exam - solutions

## Multiple choice
| Q | Answer | Why |
|---|---|---|
| Q1 | B | Inheritance is transitive: a subclass gets everything from all its ancestors. |
| Q2 | B | IP routes packets between networks: Network layer (layer 3). |
| Q3 | C | `#` matches all remaining levels, so it must be the last character of the filter. |
| Q4 | C | HTTP: client sends a request and waits for the response. MQTT: publishers and subscribers are decoupled by a broker, asynchronous. |
| Q5 | B | Independent services can be built, tested and released rapidly; the monolith is the one with poor modularity and hard maintainability. |
| Q6 | A | Base name `bn`, base time `bt` and a list `e` of entries with `n`, `u`, `t`, `v`. B has an object instead of a list, C is XML, D is not SenML. |

## Open questions - model answers
**Q7 (QoS)**
- QoS 0, "at most once": fire and forget, no ack, no retransmission; message may be lost, never duplicated; lowest overhead.
- QoS 1, "at least once": PUBLISH acknowledged with PUBACK, sender retransmits until acked; delivered at least once, duplicates possible; medium overhead.
- QoS 2, "exactly once": 4-step handshake (PUBLISH, PUBREC, PUBREL, PUBCOMP); no loss, no duplicates; highest overhead and latency.
- The QoS is set by publisher and subscriber; the effective one is the minimum of the two.
- Use cases: QoS 0 for a temperature published every few seconds (a lost sample is irrelevant); QoS 1 for an HVAC command or an alert (must arrive, a repeated ON is harmless); QoS 2 for billing-like events.
- Grading: 1.5 per level correctly described, 1 for use cases and/or min(pub, sub) remark, 0.5 for clarity.

**Q8 (JSON vs XML)**
- Requirements: platform/language independence, human readable, compact (bandwidth for constrained devices), easy to parse, able to represent structured and nested data, standard and widely supported, extensible/self-describing, optional validation (schema).
- JSON: pros are light, easy to parse (maps to dict/list), native in JavaScript and most REST APIs; cons are no comments, no namespaces, limited types (no date), validation less standardised.
- XML: pros are a markup language with attributes, namespaces, schemas (XSD) and transformation (XSLT), strong validation, mixed content; cons are verbose, heavier parsing, more bandwidth.
- Conclusion: for IoT and REST, JSON is usually preferred; XML where validation/documents matter.
- Grading: 2 requirements, 1.5 JSON, 1.5 XML.

## Coding question - what earns points (16)
| Item | Points |
|---|---|
| Class with the comfort logic (OOP), correct thresholds and order of rules | 4 |
| CherryPy service class with `exposed = True`, `GET` method, `MethodDispatcher` config, mount and start | 4 |
| Method choice: GET (read-only computation, no state changed), input in the query string, justified | 2 |
| JSON output in the exact requested keys (`json_out` or `json.dumps`) | 2 |
| Input validation: missing, non-numeric, humidity outside 0-100 gives 400 and JSON error | 3 |
| Example URL and response, e.g. `GET http://localhost:8080/comfort?temperature=28&humidity=45` | 1 |

Common mistakes: logic written outside any class (lose OOP points); POST used for a computation with no state (acceptable only if justified, the data are not a resource to create); returning a Python `str(dict)` instead of JSON; crash (500) on `float("abc")`; wrong rule order; forgetting `exposed = True`.

Reference solution: `coding_solutions/mock_coding.py` (checked by `coding_solutions/test_solutions.py`).
