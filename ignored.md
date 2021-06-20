# Ignored Files

A list of all ignored files with copy-pastable templates. Useful for when you want to work on commands that use these, for obvious reasons. Every file has a copy-pastable template to make it easy for you to use.

These are usually files which would be overkill to make a PSQL table for. Other possibilities are files that are never edited, but should be different on every machine.

### .env

```.env
SANDBOX=true

URBANDICTIONARY=""
IMGFLIPNAME=""
IMGFLIPPASSWORD=""

DBUSERNAME=""
DBPASSWORD=""
DBHOST=""
DBNAME=""

TOKEN=""
HOSTIPC=false
READYMESSAGE=""
STATUSMESSAGE=""
```

### files/hangman.json

Contains info on the current Hangman game.

```json
{
  "guessed": [],
  "guesses": 0,
  "word": ""
}
```

### files/lastTasks.json

Contains timestamps for when every `task` in `cogs/tasks.py` ran for the last time. This makes sure it's been at least X amount of time between tasks (so that when the bot disconnects on an hour where the task should run, it doesn't run again).

```json
{
  "birthdays": 0,
  "channels": 0,
  "interest": 0,
  "lost": 0,
  "prison": 0,
  "poke": 0,
  "remind": 0
}
```

### files/locked.json

Contains a boolean indicating whether or not the server is currently locked, and the timestamp indicating when the lock ends.

```json
{
  "locked": false,
  "until": -1
}
```

### files/stats.json

Contains the stats to track for gambling games. Weren't made as a PSQL table because they would be too long (and every game is different).

```json
{
  "cf": {
    "h": 0,
    "t": 0
  },
  "dice": {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0,
    "5": 0,
    "6": 0
  },
  "rob": {
    "robs_success": 0,
    "robs_failed": 0,
    "bail_paid": 0.0
  }
}
```

### files/ufora_notifications.json

Stores ID's of all received Ufora notifications.

```json
{
  "Algoritmen en Datastructuren 2": [],
  "Communicatienetwerken": [],
  "Computerarchitectuur": [],
  "Functioneel Programmeren": [],
  "Multimedia": [],
  "Software Engineering Lab 1": [],
  "Statistiek en Probabiliteit": [],
  "Systeemprogrammeren": [],
  "Webdevelopment": [],
  "Wetenschappelijk Rekenen": []
}
```