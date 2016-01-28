# genius-bar
API backend for tracking mobile device with slack

- The bot should be in #general.
- All respond should be public in #general.
- with heroku server.

Commands
--

`/DeviceCheckout [device ID]`

- Respond: “@username checkout device [device ID]”
- Push "Device [device ID] check out by @username" to the oringal channel

`/DeviceList`

- Respond: a list of all Device ID | Device Name | Ownership

`/DeviceReg [device ID]`

- Respond: “[Device ID] / [Device Name] registered and own by @username”

`/DeviceDereg [Device ID] [reason]`

- Respond: “[Device ID] / [Device Name] de-registered by @username”

`/DeviceAudit [Device iD]`

- Respond: Show the list of last 20 register / deregister / own actions

Prerequisite
--
- python 3.5
- Mysql
- Set up Slack command   https://api.slack.com/

run
--

0. setup your command token, slack_url, sqlalchemy_url, port in config.ini

1. open a new vm with python 3.5

2. run `python3.5 setup.py develop`

3. install requirement  with `pip install freeze`

4. setup DB with alembic by `alembic -c config.ini upgrade head` 

5. run `pserver config.ini` 