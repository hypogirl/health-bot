# HEALTH BOT
Python discord bot for the server of the American music band HEALTH.

**Note:** This code is written specifically for the [HEALTH discord server](http://discord.gg/health "HEALTH discord server") as it includes specific channel and role IDs. In the future I might make the code flexible for other servers, but, for now, if you decide to use this bot, you should be careful with those.

## User-friendly features


- ### Commands
**!timeout**<br>
Allows a user to take a break for a given period of time by muting them from all the server channels.

- ### Triggers
Name taken from carlbot, the bot formally used to moderate the server. They're, essentially, quick and simple commands that can be used by any user.
Usually, these will be reaction images - or memes - stored in a database and can be added/removed by the moderators.

- ### Message reactions
There are two main type of reactions the bot can generate.
  1. Compliments or insults, to which the bot will react with a happy or sad emoji, respectively.
  2. Mentions of HEALTH songs or albums, to which the bot with react with the respective album cover.

Note: The code for this feature takes the content of the message, removes the spaces and tries to find specific expressions in it. The plainness of this process makes it possible for unrelated messages to be flagged as, e.g., a HEALTH song or album. This feature is also not available in the ``#on-the-real`` channel, which is reserved for serious conversations.

---

## Moderator-friendly features
- ### Commands
**!ban ~~(and !unban)~~, !kick, !warn, !mute (and !unmute)**<br>
These commands make it easier for moderators to take action right away when an incident might be occuring. They are very intuitive and work with both the mention of the user the action is directed to or their ID.

**!createtrigger and !deletetrigger**<br>
These two commands are very simple and are used to add or remove a specific trigger from the database.

**!purge**<br>
Purges a given number of messages from a channel, counting from the most recently sent.

**!motd**<br>
There's a tradition of giving a special role named "Member Of The Day" to users who boost the server or users celebrating their birthday. This command automates the process and takes the role away from the user 24 hours after giving it. It will work with both the mention of the user the action is directed to or their ID.

**!spam**<br>
This featured is mostly useless but it exists, so it'll, at least, be described here. It sends out the message "spam" a given number of times. It is easily abusable and there is no limit number of messages to be sent.

- ### #mod-log and #big-brother-is-watching
The bot uses two channels to log events.
  1. ``#mod-log`` is used for most events.<br>
    - Firstly, this channel logs bans, unbans, kicks, warns, muting and unmuting, whether they were made with the help of the bot or manually; if these events were created with the bot, the logs will include a link that allow the mods to jump to the message that caused the event.<br>
    - Secondly, this channel will also log the users who leave the server, showing how long they had been there and what roles they had.<br>
    - A third important type of event is the creation of invites, assuming they can be used for less desired purposes like raiding or bot spamming, the bot keeps logs of the user who created the role and whether or not they have a default Discord profile picture (as silly as this might sound, it can be useful to know if an account is recent or a bot). On top of that, the bot allows moderators to delete the invite by simply reacting to it with a "❌" emoji.<br>
    Probably the less occuring event is the use of the !purge command. The bot logs which users got their messages deleted and how many messages those were.
  2. ``#big-brother-is-watching`` simply logs whenever a message is edited or deleted and shows the content of it (in the case of editing, it shows the content before and after the editing).

