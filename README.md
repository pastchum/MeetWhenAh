# WhenMeetAh?
###### A Telebot built for coordination between  you and your friends

Ever planned out a day out with your friends, but couldnt find the perfect day to go because of scheduling conflicts? Never again, with the WhenMeetAh? telegram bot!

## Features
- Set date range for the event
- Signing up for event and setting availability is at the simple click of a button. 
- Simple and seamless Web-UI that is built into Telegram

## How to use?
Simply message /start to the bot https://t.me/meetwhenah_bot, and it will guide you from there. Don't worry, its fairly self explanatory!

## Technologies
###### Telebot
- pytelegrambotAPI
- uvicorn
- fastAPI
- Google FireBase

###### Frontend0
- React
- Next.JS
- Vite
- Shadcn/UI




## Deployment

This project requires the user to have a __functional server for webhooks__, and another to deploy the webpages. 

To deploy Telegram Bot:

Zrok is a tunneling service that is set up custom for this project's testing, and should be removed when deploying to production.
```bash
  uvicorn telegram:app --host 0.0.0.0 --port 8001
  zrok share reserved when2meetbot
```

