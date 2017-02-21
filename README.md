# IRC bro
IRC bot for fun and profit. Supports simple plugins

## Plugin
Some of the features are:
- Call when message is recived
- Access to backlog of last recived and sent messages 
- Chain call for output messages, so plugins can modify the sent message before it is sent.

###Documentaion

All plugins must have the IRC_PLUGIN class.
The class constuctor takes in the irc_bot object, so plugins
can modify the ```IRC_BOT```

# Depends
python fbchat

