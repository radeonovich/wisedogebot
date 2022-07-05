# Wisedogebot  
  

This bot allows your subscribers to suggest image posts to publish it in your channel with scheduling system.  
  

Bot is under the progress now. 




### Features development state:  
# 
✔️Receive images from users and store it  
✔️Moderate received images and store accepted images  
⏳ Post instantly from moderation mode  
⏳ Send accepted images in the channel with a scheduler  
⏳ Undo last accepted image  
✔️SQL support  
⏳ User stats with send/accepted/denied counters  
  
  



### Setup  
At the moment bot is most likely useless for you - there is no ability to post in the channel yet. But of course you can implement it yourself!

Install pyTelegrambotAPI:
```
pip install pyTelegramBotAPI
```



Run main.py. At first start a new config file will be generated. You need to open it and set your token, channel name and moderator id's list.
Now you can run main.py again, and it will be ready to work with.

Done!

