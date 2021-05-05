#!/bin/bash

if ! pgrep -f 'bot.py'
then
    echo "$(date) Not running... Starting up" >> /home/hackermans/out_test
    /usr/bin/python3 /home/hackermans/health-bot/bot.py >> /home/hackermans/out_test 2>&1 &
 # run the test, remove the two lines below afterwards
else
    echo "$(date) running" >> /home/hackermans/out_test
fi
