# L13 - Revision and exam practice (1.5 h)

## Goals
- See the whole course as one map (OOP, REST, catalog, MQTT, ThingSpeak, Telegram, integration).
- Know the written exam format and how it is scored.
- Practise on a full mock exam and on the three kinds of coding questions asked so far.

## Revision map
| Block | What to remember | Lessons |
|---|---|---|
| OOP | classes, inheritance (also multi-level), polymorphism, composition (a room "has" sensors and an HVAC) | L02, L03 |
| REST | resources and URLs, GET/POST/PUT/DELETE, status codes, JSON, CherryPy `MethodDispatcher` with `exposed = True` | L04, L05 |
| Catalog | a JSON registry exposed over REST; service discovery: clients ask the catalog instead of hard-coding addresses | L06 |
| MQTT | broker, topics and wildcards (`+`, `#`), QoS 0/1/2, retained, clean session, SenML payloads | L07, L08 |
| ThingSpeak | channel, write API key (kept in `.env`), 15 s limit between updates, MQTT-to-REST adaptor | L09 |
| Telegram | BotFather, token in `.env`, commands, inline keyboards, notifications | L10, L11 |
| Integration | all services together, a house added at runtime, microservices vs monolith | L12 |

## Exam format (written)
| Part | Count | Scoring |
|---|---|---|
| Multiple choice | 6 | +1 correct, 0 not answered, -0.5 wrong |
| Open questions | 2 | max 5 points each |
| Coding (RESTful web service, CherryPy, OOP, JSON) | 1 | max 16 points |

Wrong MCQ answers cost points. A blind guess among 4 options has a negative expected value (-0.125); with one option excluded it is zero; with two excluded it is positive (+0.25). So: guess only if you can exclude at least two options.

Real exams so far ask a REST service in the coding part (fake sensors, calculator, unit converter). MQTT coding is possible in principle, so one practice exercise is included.

## Tips for the coding question
1. Read the request twice; underline inputs, outputs, ranges, error cases.
2. Choose the HTTP method and say why (GET = read-only, no state change; PUT = update a known resource; POST = create/command with a body).
3. Choose where the input goes: path for "which resource/operation", query string for optional parameters, body (JSON) for data to store.
4. OOP is mandatory: put the logic in a class, the HTTP layer in another (or at least methods, not loose code).
5. Respond with JSON in exactly the requested keys; return 400 for bad input (missing, not a number, out of range, unknown operation).
6. Always write an example URL and the expected response, even if not asked.

## How to use this folder
```
exam_practice/
  mock_exam.md              one full mock exam (do it in 90 minutes, no notes)
  mock_exam_solutions.md    answer key, model answers, grading hints
  theory_questions.md       question bank: ~25 MCQ + ~10 open questions
  extra_mqtt_practice.md    optional MQTT coding exercise (practice only)
  coding_solutions/         runnable reference solutions + test_solutions.py
```
Suggested plan for the session: 15 min revision map, 45 min mock exam (the coding part first, live), 20 min correction, 10 min questions.

Run the reference solutions (from `exam_practice/coding_solutions/`):
```
python mock_coding.py 8080        # then: curl "http://localhost:8080/comfort?temperature=28&humidity=45"
python test_solutions.py          # starts every solution on ports 8170-8173, checks, stops them
```
Try the exam first, then compare with the solution. Do not memorise code: understand the pattern (class + `MethodDispatcher` + JSON + 400 on bad input).
