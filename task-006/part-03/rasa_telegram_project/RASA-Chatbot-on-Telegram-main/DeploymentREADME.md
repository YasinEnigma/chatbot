# Foodie Restaurant search chatbot
Foodie is a chatbot which finds the highest rated restaurants for you based on the input query you give it in the form of a normal text sentence.
It gets the data from Zomato API and uses RASA version 2.0.0 to for creating the chatbot. We can deploy this chatbot on various platforms like 
slack, Telegram etc. We have deployed it on Telegram where it works really well. The video link is provided in a separate file called "youtube.txt" 

#RASA VERSION = 2.0.0

# Conda environment setup
#### use the below command to set up the environment to run our bot. You can find the requirements.txt file in the project
pip install -r requirements.txt 

# Steps to run our bot:-
After setting up the conda environment using the previously talked about way, run the following steps:-
1. Run the below command using conda command promt:- 
rasa train && rasa run actions
2. Open another Anaconda promt and then run the following command:-
rasa shell

#### That's it. Start talking to our bot

#Note:-
Internet fluctuations/delay in response from Zomato api etc can sometimes cause timeouts because the default timeout of rasa shell is 10 seconds only.
But we have optimized our code so much that most of the times, the users will never face timeouts if they have a decent internet connection and
and the Zomato api is responding fast(mostly it does). If you do face timeout in rasa shell, then below are the two things you can do:-
1. Run the rasa shell again to test it. 
2. Increase the timeout in <source folder>\anaconda3\envs\<conda env>\lib\site-packages\rasa\core\channels\console.py to a higher value.