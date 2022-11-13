# Task-006 Part 01
Launch Rasa initial demo (English)

## Working steps:
1. Setup Rasa Enivironment
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
2. Create new project with rasa
```shell
$ rasa init
```
3. Train project according to your training data in /data directory
```shell
$ rasa train
```
4. Run project and connect to your model using API, etc
```shell
$ rasa run
```
5. Working with you demo using shell
```shell
$ rasa shell
```
6. Enjoy your first project :)


# TODO
- [ ] Create a chatbot for resturant reserving.
- [ ] Create a chatbot for ticket booking.
- [ ] Create a multilingual chatbot.
