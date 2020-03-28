FROM ngoroth/python-scipy:latest

WORKDIR /app
ADD . /app

COPY . .

CMD [ "python", "./TelegramBot.py" ]
