# Databases

The following file contains a list of all PSQL tables Didier uses. Every table has a description on when/where it is used, which columns it contains, and what type of value those columns hold.

The schemes below can also help you figure out which index corresponds to which column.

This should be enough for you to set up a local PSQL database to test your code in.

Keep in mind that you can create and edit SQL databases in PyCharm, so that you don't have to write any SQL statements yourself. This also makes it _a lot_ easier to change the behaviour of a column.

### birthdays

Used in birthdays.py - Birthay commands & the daily Task that checks if it's anyone's birthday.

    0 userid: bigint, unique, primary key               | The Discord id of the user
    1 day: integer                                      | The day of the user's birthday
    2 month: integer                                    | The month of the user's birthday
    3 year: integer                                     | The year of the user's birthday

### channel_activity

Used in stats.py - Stats.Channels & the daily task that updates the message count. Keeps track of the amount of messages sent in every channel.

    0 channel_id: bigint, unique, primary key           | The channel id of this channel
    1 message_count: numeric                            | The amount of messages sent in this channel

### currencytable

Used in all Currency commands (Dinks, Bank, Bitcoin, Gambling, ...)

    0 userid: bigint, unique, primary key               | The Discord id of the user
    1 dinks: numeric, default 0.0                       | The amount of Didier Dinks the user has
    2 banklevel: integer, default 1                     | The user's bank level
    3 investedamount: numeric, default 0.0              | The amount of Didier Dinks the user has currently invested
    4 investeddays: integer, default 0                  | The amount of days the user has invested in their bank
    5 profit: numeric, default 0.0                      | The current amount of profit the user has gained from interest
    6 defense: integer, default 1                       | The user's bank's defense level
    7 offense: integer, default 1                       | The user's bank's offense level
    8 bitcoins: numeric, default 0.0                    | The amount of Bitcoins the user currently has
    9 nightly: integer, default 0                       | The timestamp when the user last claimed their Nightly
    10 nightly_streak: integer, default 0               | The user's current Nightly Streak

### custom_commands

Used to store custom commands that replace Dyno.

    0 id: integer, auto-increment, unique, primary key  | The id of the command
    1 name: text, unique                                | The name of the command
    2 response: text                                    | The response sent when the command is used

### custom_command_aliases

Used to store aliases for custom commands.

    0 id: integer, auto-increment, unique, primary key  | The id of the alias
    2 command: integer                                  | The id of the command this alias is for
    3 alias: text                                       | The name of the alias

### dad_jokes

Used in fun.py - Dadjoke command.

    0 id: integer, auto-increment, unique, primary key  | The id of the joke
    1 joke: text                                        | The joke itself

### faq_categories

Used in faq.py - FAQ commands, provides a list of valid categories.

    0 id: integer, auto-increment, unique, primary key  | The id of the category
    1 name: text                                        | The name of the category

### faq_entries
    
Used in faq.py - FAQ commands, provides a list of entries for every category.

    0 id: integer, auto-increment, unique, primary key  | The id of this entry
    1 category_id: integer                              | The id of the category this entry belongs to
    2 question: text                                    | The question of this entry
    3 answer: text                                      | The answer for this entry
    4 answer_markdown: text, default null               | A variant of the answer supporting markdown which are possible in embeds, but not normal messages (like hyperlinks).

### githubs

Used in selfpromo.py - Github commands.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 githublink: text                                  | A string containing the links to the user's Git pages, separated by newlines

### info

Used in poke.py - Poke commands. Used to store specific info for users, currently only whether or not they've blacklisted themselves.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 poke_blacklist: boolean, default false            | A boolean indicating whether or not the user has blacklisted themself

### inventory

Used in store.py - Store commands, and dinks.py - Dinks commands. Holds a list of all items a user has, the item's id's & counts

    0 userid: bigint                                    | The user's Discord id
    1 itemid: integer                                   | The id of the item the user has bought
    2 amount: integer, default 0                        | The amount of this item the user possesses

### memes

Used in fun.py - Meme commands. Contains all info about a certain meme to generate it via the API.

    0 id: bigint                                        | The id of the meme
    1 name: text                                        | The name of the meme, lowercase
    2 fields: integer                                   | The amount of fields the meme has

### muttn

Used in events.py - Reaction events, and muttn.py - Muttn commands.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 stats: numeric                                    | The user's muttn percentage
    2 count: integer                                    | The amount of muttn reacts the user has received
    3 message: bigint                                   | The id of the last message the user got an increase by
    4 highest: integer, default 0                       | The highest amount of reacts the user's last message had, avoiding spam abuse

### personalstats

Used in stats.py - Stats commands. Tracks the user's personal stats to award achievements.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 poked: integer, default 0                         | The amount of times the user has been poked
    2 robs_success: integer, default 0                  | The user's amount of successful robs
    3 robs_failed: integer, default 0                   | The user's amount of failed robs
    4 robs_total: numeric, default 0.0                  | The total amount of Didier Dinks the user has robbed
    5 longest_streak: integer, default 0                | The longest nightly streak the user has achieved
    6 nightlies_count: integer, default 0               | The total amount of Nightlies the user has claimed
    7 profit: numeric, default 0.0                      | The total amount of profit the user has claimed
    8 cf_wins: integer, default 0                       | The amount of coinflips the user has won
    9 cf_profit: numeric, default 0.0                   | The amount of profit the user has made with coinflips
    10 bails: integer, default 0                        | The amount of times the user has bailed themselves out
    11 messages: integer, default 0                     | The amount of messages the user has sent
    12 xp: bigint, default 0                            | The amount of message xp the user has gained
    13 last_message: bigint, default 0                  | The timestamp of the user's last message that awarded xp

### poke

Used in poke.py - Poke commands. Keeps track of the currently poked person.

    0 current: bigint                                   | The Discord id of the person that is currently poked
    1 poketime: bigint                                  | The timestamp of when the user was poked
    2 previous: bigint                                  | The Discord id of the previously poked user

### prison

Used in dinks.py - Prison commands. Contains information on who is in prison.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 bail: numeric                                     | The cost to bail this user out of prison
    2 days: integer                                     | The remaining days this user has to spend in prison
    3 daily: numeric                                    | The amount of Didier Dinks that [daily] decreases by every day

### remind

Used in tasks.py - sendReminders task.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 nightly: boolean, default false                   | A boolean indicating whether or not the user wants Nightly reminders
    2 les: boolean, default false                       | A boolean indicating whether or not the user wants Les reminders

### store

Used in store.py - Store commands. Contains info on items that are available for purchase.

    0 itemid: integer, auto-increment, primary key      | The item's id
    1 name: text                                        | The name of the item
    2 price: bigint                                     | The price of the item
    3 limit: integer                                    | The item's buy limit
    
### trump

Used in oneliners.py - Trump command. Stores a list of Trump quotes.

    0 id: integer, auto-increment, primary key          | The quote's id
    1 quote: text                                       | The quote itself
    2 date: text                                        | The date on which the quote was said
    3 location: text                                    | The location and/or event where the quote was said

### twitch

Used in selfpromo.py - Twitch commands. Contains a list of everyone's Twitch links.

    0 userid: bigint, unique, primary key               | The user's Discord id
    1 link: text                                        | The link to the user's Twitch channel