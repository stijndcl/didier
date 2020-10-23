# Ignored Files

A list of all ignored files with copy-pastable templates. Useful for when you want to work on commands that use these, for obvious reasons. Every file has a copy-pastable template to make it easy for you to use.

These are usually files which would be overkill to make a PSQL table for. Other possibilities are files that are never edited, but should be different on every machine (Discord token, status message, ...).

### files/client.txt

Contains the application's token to connect to Discord. You can create your own bot & put it's token in this file to run & test Didier code.

    token_goes_here

### files/database.json

Contains the credentials needed to connect to the PSQL database. This is ignored so that I don't have to leak my IP address, but also so that you can set up a local database to mess around without affecting the Live one or having to change any code.

```json
{
  "username": "username",
  "password": "password",
  "host": "host_address",
  "database": "database_name"
}
```

When connecting to a local PSQL database, `host` should be `"localhost"`.

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

### files/readyMessage.txt

Contains the message printed in your terminal when Didier is ready.

    I'M READY I'M READY I'M READY I'M READY
    
In case you were wondering: yes, this is a Spongebob reference.

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

### files/status.txt

Contains Didier's status message for when he logs in. Keep in mind that his activity is set to `Playing `. This was first used in Didier V1 to show whether or not he was in sandbox mode.

    with your Didier Dinks.