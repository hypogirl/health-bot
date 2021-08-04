#!/bin/bash
[[ -d $HOME/logs/ ]] || mkdir ~/logs

if ! pgrep -f 'python.*bot.py'
then
    echo "$(date) Not running... Starting up" >> /home/hackermans/logs/health-bot.log
    /usr/bin/python3 -u /home/hackermans/src/health-bot/bot.py >> /home/hackermans/logs/health-bot.log 2>&1 &
#else
    # Commenting this out, no need for it anymore
    #echo "$(date) running" >> /home/hackermans/logs/health-bot.log
fi
