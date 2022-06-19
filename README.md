# Wisedogebot  
  

This bot allows your subscribers to suggest image posts to publish it in your channel with scheduling system.  
  

Bot is under the progress now.  Here is features development state:  
  



### Features development state:  
# 
✔️Receive images from users and store it  
✔️Moderate received images and store accepted images  
⏳ Post instantly from moderation mode  
⏳ Send accepted images in the channel with a sheduler  
⏳ Undo last accepted image  
⏳ SQL support  
⏳ User stats with send/accepted/denied counters  
  
  



### Setup  
At the moment bot is most likely useless for you - there is no ability to post in the channel yet. But of course you can implement it yourself!

Install pyTelegrambotAPI:
```
pip install pyTelegramBotAPI
```
Then create a file in project folder named token.txt and put your bot token in it. Use @BotFather. 

In main.py in the beginning of file find lines: 
```python
channelName = '...'  # channel to post to
moderators = [...]  # who can moderate
```
Put your info instead of ... . You can use @userinfobot to get your id. *I'm about to move all these settings to one text file, like token.txt but for all parameters you can set.*

Make sure that moderationQueue.txt and postQueue.txt files exist and are empty (last is not necessary, but there is usually my debug info there). 
Run main.py and write something to your bot.

Done!  
