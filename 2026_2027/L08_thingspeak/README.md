# L08 - ThingSpeak, a third-party REST API (1.5 h)

## Goals
- Use a REST API we do not control (ThingSpeak) with `requests`.
- Keep secrets (API keys) out of the code and out of git.
- Finish the bridge MQTT -> aggregation -> REST: the ThingSpeak adaptor of our smart home.

## Theory
**ThingSpeak** stores time series in the cloud. A *channel* has up to 8 *fields* (field1 ... field8); each field is one series
(e.g. field1 = kitchen temperature). Each channel has a **write API key** (to send data) and a **read API key**.

**Write API**: `GET https://api.thingspeak.com/update?api_key=<WRITE_KEY>&field1=23.5&field2=60`
- Answer = the *entry id* (a number) when the value is stored, or `0` when it is refused (wrong key, too frequent...).
- Free plan: **one update every 15 s per channel**. That is why the adaptor does not send every MQTT message: it keeps the
  latest value of each field and sends all of them together in one update every 15 s (aggregation).
- A failed upload is put back in the queue and retried at the next round.

**Secrets**: a key in the code ends up on GitHub. Rule: keys live in `2026_2027/.env` (ignored by git) and are loaded with
`python-dotenv`. Copy `2026_2027/.env.example` to `2026_2027/.env` and fill `THINGSPEAK_WRITE_KEY`.
`config.py` has the helper `get_secret(name)`: it returns `None` if the key is missing, and then we work in **dry run**
(print what we would send, send nothing).

**Create a channel** (optional, needs a free account):
1. Sign up at thingspeak.com (MathWorks account).
2. Channels -> New Channel, give a name, enable Field 1 ... Field 6 and name them, Save.
3. Tab *API Keys*: copy the *Write API Key* into your `.env`.

## Files
`config.py` (catalog URL from `settings.json`, `get_broker`, `get_secret`), `mymqtt.py` (as in L06/L07), `senml.py` (solution only, used by the offline test),
`settings.json`, `ex1_write.py`, `thingspeak_adaptor.py`, `check_adaptor.py` (solution only: offline test).
Work in `starter/`, compare with `solution/`. Run everything from inside the folder.

## Exercises
### Ex1 - `ex1_write.py`
Send one value to `field1` with `requests`. Read the key with `get_secret("THINGSPEAK_WRITE_KEY")`.
Without a key, print the URL you would call (key masked as `***`) and exit. With a key, print the entry id (or "Refused" when the answer is `0`).

    python ex1_write.py 23.5

### Ex2 - `thingspeak_adaptor.py`
Complete `notify` and `upload`:
- `notify(topic, payload)`: build the key `house/room/kind` from the topic (HVAC state topic -> `house/room/hvac`, value 1 for ON, 0 for OFF), look up the field number in `self.fields` (from the catalog `GET /thingspeak`), keep only the latest value in `self.pending`. Unmapped rooms are ignored.
- `upload()`: send all pending values in ONE update; no key -> print `[dry run] ...`; if the answer is `0` or the request fails, put the values back in `self.pending`.

The adaptor needs the L07 system. Terminals (from the repo folder `2026_2027/`):
1. `mosquitto` (broker on 1883)
2. L07 solution: catalog + connectors + controller (or `cd smart_home && python launch_all.py`)
3. `cd L08_thingspeak/starter` then `python thingspeak_adaptor.py --dry-run` (add `--catalog URL` if the catalog is not on port 8080)

After at most 15 s you see: `[dry run] GET https://api.thingspeak.com/update {'field1': 21.5, 'field3': 1}`.
Offline test of the logic (solution folder): `python check_adaptor.py`.

### Ex3 - a new room in the mapping
While the adaptor runs, add a field for a new room in the catalog (`PUT /thingspeak` replaces the whole mapping, so send the old fields too):

    curl http://localhost:8080/thingspeak
    curl -X PUT http://localhost:8080/thingspeak -H "Content-Type: application/json" \
      -d '{"channel_id":0,"fields":{"house1/kitchen/temperature":1,"house2/living_room/temperature":7}}'

Within 15 s the adaptor reloads the map (no restart); when `house2/living_room` publishes a temperature you see `field7` in the next update.
