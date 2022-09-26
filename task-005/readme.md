# Task-005
Develop an voice telegram bot that recognition and translation of spoken voice into text.

## Working steps:
1. Create an new bot using @botfather telegram bot using /newbot command.
2. Select and name and id for your bot.
3. Save your token in token file.
4. Install [telebot](https://github.com/eternnoir/pyTelegramBotAPI) library.
5. Write a function for read the audio file.
6. Read audio file using 'librosa' and using different framework to convert to text
7. Using [Vosk](https://alphacephei.com/vosk/), [Nemo](https://github.com/NVIDIA/NeMo) for ASR.
6. Send message to your bot and show result :). 

# Clone project 
```shell
$ git clone https://github.com/YasinEnigma/mci-chatbot
$ cd mci-chatbot/task-005
$ open using jupyter notebook or colab
$ using your specific language model and download vosk model from [this](https://alphacephei.com/vosk/models)
$ copy your token id in API_TOKEN variable
$ Run cells :)
```


# TODO
- [ ] Create a bot for reading sound and reply appropriate response to message in text format.
- [ ] Create a bot for reading sound and reply appropriate response to message in speech format.
