# Task-003
Develop automatic speech recognition (ASR) for persian language using [NEMO](https://github.com/NVIDIA/NeMo) toolkit.

## Working steps:
1. Download and install nemo library.
2. Download dataset of common voice for persian (in here I'm using persian common voice [v.6](https://commonvoice.mozilla.org/)).
3. Preprocessing the manifest or text for normalization (remove punctuations, normalize special character like س ش and etc).
4. Config model that exists in config file (10x5 jusper model used with 4.5 milion paprameters).
5. Number of classes is **48**
6. Train model for 100 epoch using colab.
7. Best result is: **WER = 80%**



# Clone project 
```shell
$ git clone https://github.com/YasinEnigma/mci-chatbot
$ cd mci-chatbot/task-003
$ open and run in jupyter
```


# TODO
- [ ] Improve the system accuracy by increase epoch numbers.
- [ ] Using pre-train models and fine-tuning model.
- [ ] More preprocessing.
