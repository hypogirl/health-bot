#!/bin/bash

if ! pgrep -f 'python.*bot.py'
then
    echo "$(date) Not running... Starting up" >> /var/log/botden/health-bot.log
    /usr/bin/python3 -u ${HOME}/src/health-bot/bot.py >> /var/log/botden/health-bot.log 2>&1 &
fi
