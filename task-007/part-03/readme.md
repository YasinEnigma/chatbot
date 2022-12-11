# Task-006 Part 03
Launch Rasa telegram bot

## Working steps:
1. Create an new bot using @botfather telegram bot using /newbot command.
2. Select and name and id for your bot.
3. Save the username and Http API token for next steps.
3. Setup Rasa Enivironment.
```shell
$ python3 --version
$ pip3 --version
$ sudo apt update
$ sudo apt install python3-dev python3-pip
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip3 install -U pip
$ pip3 install rasa
```
4. Create new project with rasa
```shell
$ rasa init
```
5. Download and install [ngrok](https://ngrok.com/)
6. add your authtoken to the default ngrok.yml with 
```shell
$ ngrok config add-authtoken ajfdaifaidfjakfjaoidfjaodfijalkfdjaiouqiutqoithuqyi
```
7. Connect the local machine and World Wide Web with
```shell
$ ngrok http 5005
```
8. Copy the word wide web https links that created by ngrok.
9. Copy the telegram bot username and API token and ngrok webhook url in credentials.yml file.
```shell
telegram:
  access_token: "your_bot_access_token"
  verify: "your_bot_username"
  webhook_url: "ngrok_webhook_url/webhooks/telegram/webhook"
```
10. Train project according to your training data in /data directory
```shell
$ rasa train
```
11. Working with you demo using shell
```shell
$ rasa shell
```
12. Run project and connect to your model using API, etc
```shell
$ rasa run
```
13. Send message to your bot and show result :). 
