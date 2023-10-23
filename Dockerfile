FROM python:3.8
#FROM gorialis/discord.py
RUN pip3 install --upgrade pip
RUN pip3 install -U discord.py==1.7.3
RUN python3 -m pip install requests
RUN pip3 install pprintpp

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot
VOLUME ["/usr/src/bot"]


CMD [ "python3", "-u" ,"dcbot.py" ]
