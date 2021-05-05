#!/bin/bash

#simple cron job to make sure the bot is up
if ! pgrep -f 'bot.py'
then
    nohup python3 /home/hackermans/health-bot/bot.py & > /var/tmp/bot.out
# run the test, remove the two lines below afterwards
else
    echo "running" > ~/out_test.txt
fi


