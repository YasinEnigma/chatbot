from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
import asyncio

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import Restarted
from rasa_sdk.events import FollowupAction
import zomatopy
import json
import time
import re
from user_functions import get_soundex, get_last_action
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
        
    async def run(self, dispatcher, tracker, domain):
        start_time = time.time()
        #print("i am inside action_search_restaurants")
        # My API Key of Zomato
        config = {"user_key":"f9c893da39750138e222b042c8070293"}
        zomato = zomatopy.initialize_app(config)

        # Price range determination
        price = tracker.get_slot('price')
        print(price)
        # Get the user selected cuisine
        # Slot 'cuisine' would have been updated in the ActionCheckCuisine() with correct cuisine name
        cuisine = tracker.get_slot('cuisine')
        print(cuisine)
        # Get the user selected location
        # Slot 'location' would have been updated in the ActionCheckCity() with correct city ID as per Zomato API		
        city_id = tracker.get_slot('location')
        print(city_id)

        # Check if slots are correctly filled or not

        # If location slot is not filled, ask for city name
        if city_id == None:
            print("no city entered 1")
            # As per https://rasa.com/docs/action-server/sdk-dispatcher/
            dispatcher.utter_message(template = "utter_ask_location")
            return[FollowupAction("action_listen")]
        # Slot is filled but action was not carried out
        elif get_last_action(tracker.events, "action_check_city") == False:
            print("no city entered 2")
            return[FollowupAction("action_check_city")]

        # If cuisine slot is not filled, ask for cuisine
        if cuisine == None:
            print("no cuisine entered 1")
            dispatcher.utter_message(template = "utter_ask_cuisine")
            return[FollowupAction("action_listen")]
        # Slot is filled but action was not carried out
        elif get_last_action(tracker.events, "action_check_cuisine") == False:
            print("no cuisine entered 2")            
            return[FollowupAction("action_check_cuisine")]

        # If price slot is not filled, ask for price range
        if price == None:
            print("no price entered 1")
            dispatcher.utter_message(template = "utter_ask_price_range")
            return[FollowupAction("action_listen")]
        # Slot is filled but action was not carried out
        elif get_last_action(tracker.events, "action_check_price") == False:
            print("no price entered 2")
            return[FollowupAction("action_check_price")]

        # Cuisines code (used by zomato)
        # Source: https://developers.zomato.com/documentation?lang=tr#/
        cuisines_dict = {'american':1,'chinese':25,'mexican':73,'italian':55,'north indian':50,'south indian':85}

        # Prepare the response
        response = []
        initialResponse = ""
        # As long as there is a valid location specified
        if (city_id != 'unlisted'):
            # get_location gets the lat-long coordinates of 'loc'
            #location_detail = zomato.get_location(loc, 1)
            # Store retrieved data as a dict
            #d = json.loads(location_detail)
            #city_id = d["location_suggestions"][0]["city_id"]
            # Fetch results
            # If cuisine is specified, then use that to search restaurants
            if (cuisine != 'unlisted'):
                count = 0
                #Zomato api only lets us fetch 100 records, after that it starts returning blank json
                for offset in range(0, 100, 20):
                    #results = zomato.restaurant_search_by_city(city_id, str(cuisines_dict[cuisine]), offset)
                    loop = asyncio.get_event_loop()
                    if loop.is_running() == False:
                        results = asyncio.run(zomato.restaurant_search_by_city_async(city_id, str(cuisines_dict[cuisine]), offset))
                    else:
                        results = await zomato.restaurant_search_by_city_async(city_id, str(cuisines_dict[cuisine]), offset)

                    d1 = json.loads(results)
                    if offset == 0:
                        maxData = d1['results_found']
                    if (count>=10) or (offset>maxData):
                        break
                    # If no results match with the user mentioned criteria
                    if maxData == 0:
                        initialResponse = "No restaurants found matching your criteria"
                        dispatcher.utter_message(initialResponse)
                    else:           
                        initialResponse =  "Here are the top rated restaurants as per your criteria:"+"\n"
                        for restaurant in d1['restaurants']: 
                            if count>=10:
                                break
                            # Getting Top 10 restaurants for the lower price range
                            if ((float(price) == 1) and (restaurant['restaurant']['average_cost_for_two'] < 300) and (cuisine.title() in restaurant['restaurant']['cuisines'])):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+".")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1

                            # Getting Top 10 restaurants for the mid price range
                            elif ((float(price) == 2) and (restaurant['restaurant']['average_cost_for_two'] >= 300) and (restaurant['restaurant']['average_cost_for_two'] <= 700) and (cuisine.title() in restaurant['restaurant']['cuisines'])):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+"\n")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1 

                            # Getting Top 10 restaurants for the higher price range                       
                            elif ((float(price) == 3) and (restaurant['restaurant']['average_cost_for_two'] > 700) and (cuisine.title() in restaurant['restaurant']['cuisines'])):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+"\n")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1
                            
            # Cuisine is not specified, hence search for all cuisine types
            else:
                count = 0
                #print("inside else cuisine")
                for offset in range(0, 100, 20):
                    #results = zomato.restaurant_search_by_city(city_id, "", offset)
                    loop = asyncio.get_event_loop()
                    if loop.is_running() == False:
                        results = asyncio.run(zomato.restaurant_search_by_city_async(city_id, '', offset))
                    else:
                        results = await zomato.restaurant_search_by_city_async(city_id, '', offset)

                    d1 = json.loads(results)
                    if (count>=10) or (offset>d1['results_found']):
                        break
                    # If no results match with the user mentioned criteria
                    if d1['results_found'] == 0:
                        initialResponse = "No restaurants found matching your criteria"
                        dispatcher.utter_message(initialResponse)
                    else:           
                        initialResponse = "Here are the top rated restaurants as per your criteria:"+"\n"
                        for restaurant in d1['restaurants']: 
                            if count>=10:
                                break
                            # Getting Top 10 restaurants for the lower price range
                            if ((float(price) == 1) and (restaurant['restaurant']['average_cost_for_two'] < 300)):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+".")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1

                            # Getting Top 10 restaurants for the mid price range
                            elif ((float(price) == 2) and (restaurant['restaurant']['average_cost_for_two'] >= 300) and (restaurant['restaurant']['average_cost_for_two'] <= 700)):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+"\n")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1 

                            # Getting Top 10 restaurants for the higher price range                       
                            elif ((float(price) == 3) and (restaurant['restaurant']['average_cost_for_two'] > 700)):
                                response.append(str(restaurant['restaurant']['name'])+ " in "+ str(restaurant['restaurant']['location']['address'])+ " has a rating of "+ str(restaurant['restaurant']['user_rating']['aggregate_rating'])+"\n")
                                response.append("The average price of Rs."+ str(restaurant['restaurant']['average_cost_for_two'])+ " for two persons" + "\n")
                                count = count + 1

                
            # If no results obtained
            if(count == 0):
                initialResponse = "Sorry, No results found for your criteria. Please type modified criteria?"
                dispatcher.utter_message(initialResponse)
                return [Restarted()]
            # Display the results
            else:
                dispatcher.utter_message(initialResponse)
                for res in response[::2][:5]:
                    dispatcher.utter_message(res)

        # If no valid location is given
        else:
            response = "Sorry, we don’t operate in this city. Please specify some other location"
            dispatcher.utter_message(response)
        print(offset)   
        print("--- %s seconds ---" % (time.time() - start_time))
        return [SlotSet('emailmsg',response)]

# Cuisine selection
# Cuisine details for the restaurant search
class ActionCheckCuisine(Action):
    
    def name(self):
        return 'action_check_cuisine'
        
    def run(self, dispatcher, tracker, domain):
        
        #print("i am inside action_check_cuisine")
        #dispatcher.utter_message("i am inside action_check_cuisine")
        # Available cuisines and their soundex codes
        cuisines = {get_soundex('chinese'):'chinese', get_soundex('mexican'):'mexican', get_soundex('italian'):'italian', get_soundex('american'):'american', 
                    get_soundex('south indian'):'south indian', get_soundex('north indian'):'north indian'}

        # cuisine dropdown
        cuisines_dropdown = {'1':'chinese', '2':'mexican', '3':'italian', '4':'american', '5':'south indian', '6':'north indian'}

        # Get the user selected cuisine
        cuisine = tracker.get_slot('cuisine')

        print(cuisine)
        cuisine = cuisine.lower()
        # Check if the user has chosen from the dropdown or directly entered the cuisine
        # If user has chosen using the dropdown
        if cuisine in cuisines_dropdown.values():
            # If yes, get the correct cuisine name
            cuisine = cuisine
            print(cuisine)
        # User has directly input the cuisine choice
        else:
            # Check if the user selected cuisine is in the list
            if get_soundex(cuisine) in cuisines.keys():
                # If yes, get the correct cuisine name
                cuisine = cuisines[get_soundex(cuisine)]
                print(cuisine)
            # If the user has no preference in cuisine i.e. any cuisine is fine for the user
            elif ((cuisine == 'any') or (cuisine == 'anything') or (cuisine == 'no preference') or (cuisine == 'all')):
                # User does not have any cuisine preference. So the search will also be generic
                cuisine = 'unlisted'
            else:
                # Cuisine is not in the list
                # User will be asked again for the preference
                dispatcher.utter_message("Sorry, we don’t have reastaurants with that cuisine right now. Please specify a cuisine given in the list")
                cuisine = 'unlisted'	
                return [SlotSet('cuisine',cuisine), UserUtteranceReverted()]

        print(cuisine)    
        return [SlotSet('cuisine',cuisine)]  

# Location detection
# City details for the restaurant search
class ActionCheckCity(Action):
    
    def name(self):
        return 'action_check_city'
        
    def run(self, dispatcher, tracker, domain):
        
        start_time = time.time()
        print("i am inside action_check_city")
        #dispatcher.utter_message("i am inside action_check_city")

        # Tier 1 and 2 cities listed in wikipedia: https://en.wikipedia.org/wiki/Classification_of_Indian_cities
        city_list = ['Ahmedabad', 'Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune', 'Jaipur', 
                  'Coimbatore', 'Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 
                  'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'Bokaro Steel City', 
                  'Chandigarh', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 
                  'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 
                  'Hamirpur', 'Hubli-Dharwad', 'Indore', 'Jabalpur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 
                  'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 
                  'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 
                  'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 
                  'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 
                  'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 
                  'Trichy', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vijayawada', 'Visakhapatnam', 
                  'Vellore', 'Warangal']

        cities = {}
        # Get the soundex code of each city and create a dictionary
        for city in city_list:
            cities.update({get_soundex(city):city})

        # Considering the alternate colloquial names of the cities
        # Source: general knowledge and https://www.scoopwhoop.com/news/whats-in-a-name/#.45rdcz1m2
        # Only those names are considered which generate different Soundex codes than the original city name
        cities_alt = {get_soundex('Bendakaluru'):'Bangalore', get_soundex('Madras'):'Chennai', get_soundex('New Delhi'):'Delhi', 
                    get_soundex('Calcutta'):'Kolkata', get_soundex('Bombay'):'Mumbai', get_soundex('Belagavi'):'Belgaum', 
                    get_soundex('Bokaro'):'Bokaro Steel City', get_soundex('Hubli'):'Hubli-Dharwad', get_soundex('Dharwad'):'Hubli-Dharwad', 
                    get_soundex('Cawnpore'):'Kanpur', get_soundex('Cochin'):'Kochi', get_soundex('Calicut'):'Kozhikode', 
                    get_soundex('Puducherry'):'Pondicherry', get_soundex('Tanjore'):'Thanjavur', 
                    get_soundex('Trivandrum'):'Thiruvananthapuram', get_soundex('Trichinapoly'):'Trichy', get_soundex('Tiruchirappalli'):'Trichy', 
                    get_soundex('Baroda'):'Vadodara', get_soundex('Banares'):'Varanasi', get_soundex('Vizag'):'Visakhapatnam',
                    get_soundex('Vasai'):'Mumbai', get_soundex('Virar'):'Mumbai', get_soundex('Vasai-Virar City'):'Mumbai'}

        # Get the user selected location
        loc = tracker.get_slot('location')

        # Check if the user selected city is in the list
        if get_soundex(loc) in cities.keys():
            # Yes, get the correct city name
            city = cities[get_soundex(loc)]
        # else check if the name entered is the alternate name of the city
        elif get_soundex(loc) in cities_alt.keys():
            # Yes, hence map it to the correct city name
            city = cities_alt[get_soundex(loc)]
        else:
            # City is not in the list
            city = 'unlisted'	

        # Output pre-defined message if the city is not in the list
        if city == 'unlisted':
            dispatcher.utter_message("Sorry, we don’t operate in this city. Please specify some other location")
            city_id = 'unlisted'
            return [SlotSet('location',city_id), UserUtteranceReverted()] 
        # Zomato has a ID for each city. We need that to search for restaurants
        else:
            config = {"user_key":"f9c893da39750138e222b042c8070293"}
            zomato = zomatopy.initialize_app(config)

            location_detail = zomato.get_location(city, 1)
            d = json.loads(location_detail)
            city_id = d["location_suggestions"][0]["city_id"]
  
        print("--- %s seconds ---" % (time.time() - start_time))
        return [SlotSet('location', city_id)]     

# Price Range selection
# Price Range for two person details for the restaurant search
class ActionCheckPrice(Action):
    
    def name(self):
        return 'action_check_price'
        
    def run(self, dispatcher, tracker, domain):

        print("i am inside action_check_price")
        # Default value of price range is mid range
        price_range = "2"

        # Get price range for two from the user
        price = tracker.get_slot('price')
        price = price.lower()
        print(price)  
        # Price slot will either have values 1,2,3 (indicating low. mid and high range) or will have a string. For example:
        # 'less than 500', 'more than 300', '<300', etc. So logic should detect both these types and determine the price range accordingly

        # Upper limit words for the price range
        price_low = ['maximum', 'max', 'less than', 'lesser than', 'cheaper than' 'not more than', 'within', 'not above', '<=', '<']
        # Lower limit words for the price range
        price_hi = ['minimum', 'min', 'more than', 'higher than', 'not less than', 'not lesser than', 'not below', '>=', '>']

        # Remove the word Rupee or similar words if present as it is not needed		
        rupee = ['rs.','rs','rupees.','rupee.','rupees','rupee']
        for r in rupee:
            if r in price:
                price = price.replace(r, '')
        
        # Consider a special case where user specifies the price range himself
        # User could say "Find me restaurants between Rs.300 and Rs.500"
        # Check if there are two numbers present in the string
        if len(re.findall(r'\d+', price)) == 2:
            # Consider the upper limit as the price (e.g.: in Rs.300 and Rs.500, it will select 500)
            price = sorted(re.findall(r'\d+', price))[1]

        # If it is a pure number, then it is either the price range option (1, 2 or 3), or directly holds the amount
        if re.search(r'^[\s]*\d+[\s]*$', price):
            # Remove white spaces if any
            price = price.strip(" ")
            # Check if the user has chosen using the dropdown i.e. if the slot 'price' already has the value 1, 2 or 3
            if float(price) in range(1,4):
                # If yes, then correct price range is mentioned
                price_range = price
            # Check if the user has directly input the price range, then assign the proper value to the slot 'price' accordingly
            elif float(price) < 300:
                # It is in low price range
                price_range = "1"
            elif (float(price) >= 300) and (float(price) <= 700):
                # It is in mid price range
                price_range = "2"
            elif float(price) > 700:
                # It is in high price range
                price_range = "3"
            else:
                # Price is not mentioned
                # Choose default i.e. mid range
                price_range = "2"
        # It is not a pure number. It means it contains a string. Extract the price (which will be a number) and determine the price range
        else:
            # At first, three special cases are considered: 
            # User could say "Find me restaurants below Rs. 500" or he could say "Find me restaurants not below Rs. 500"
            # First case is finding a cheaper restaurant and second case is finding an expensive restaurant
            if ('below' in price) and ('not' not in price):
                price = price.replace('below', 'less than')

            # User could say "Find me restaurants above Rs. 500" or he could say "Find me restaurants not above Rs. 500"
            # First case is finding an expensive restaurant and second case is finding a cheaper restaurant
            if ('above' in price) and ('not' not in price):
                price = price.replace('above', 'more than')

            # User could say "Find me restaurants priced = 500"
            # '=' can be considered as user wants to consider restaurant budget below that amount
            if ('=' in price) and ('>=' not in price) and ('<=' not in price):
                price = price.replace('=', 'less than')

            # If the user has provided the upper limit for the price range 
            # (for example "within Rs.400", "cheaper than Rs.500", etc)
            for p in price_low:
                if p in price:
                    # Extract the amount
                    amount = float(re.findall(r'\d+', price)[0])
                    if amount < 300:
                        # It is in low price range
                        price_range = "1"
                    elif (amount >= 300) and (amount <= 700):
                        # It is in mid price range
                        price_range = "2"
                    elif amount > 700:
                        # It is in high price range
                        price_range = "3"
                    else:
                        # Choose default i.e. mid range
                        price_range = "2"
                    break

            # If the user has provided the lower limit for the price range 
            # (for example "minimum Rs.400", "more than Rs.500", etc)
            for p in price_hi:
                if p in price:
                    # Extract the amount
                    amount = float(re.findall(r'\d+', price)[0])
                    if 700 < amount:
                        # It is in high price range
                        price_range = "3"
                    elif (700 >= amount) and (300 <= amount):
                        # It is in mid price range
                        price_range = "2"
                    elif 300 > amount:
                        # It is in low price range
                        price_range = "1"
                    else:
                        # Choose default i.e. mid range
                        price_range = "2"
                    break
        print(price_range)        
        return [SlotSet('price', price_range)]  

# Sending Email with restaurant details
class ActionSendMail(Action):
    def name(self):
        return 'action_send_email'
    
    def run(self, dispatcher, tracker, domain):

        start_time = time.time()
        # Read email
        to_user = tracker.get_slot('email')

        # Check if the email address is entered i.e. whether the user wants the results to be sent over email
        if (to_user != "unknown"):
            # Setup email response
            from_user = 'restosearch.bot@gmail.com'
            password = 'restobotrasa123'
            subject = 'Foodie has found you the restaurants'
            msg = MIMEMultipart()
            msg['From'] = from_user
            msg['TO'] = to_user
            msg['Subject'] = subject
            # Read the search results
            response = tracker.get_slot('emailmsg')
            #formatting the body of the email
            rest_name = []
            rest_address = []
            rest_rating = []
            rest_budget = []
            for res in response[::2]:
                rest_name.append(res.split(' in ')[0])
                rest_address.append(res.split(' in ')[1].split(' has a rating of ')[0])
                rest_rating.append(res.split(' in ')[1].split(' has a rating of ')[1][:-1])
            for budget in response[1::2]:
                rest_budget.append(budget[:-1])
            txt = ""
            for idx in range(len(response)//2):
                txt = txt + '<b>Restaurant Name:</b> ' + rest_name[idx] + '<br>'
                txt = txt + '<b>Restaurant locality address:</b> ' + rest_address[idx] + '<br>'
                txt = txt + '<b>Budget:</b> ' + rest_budget[idx] + '<br>'
                txt = txt + '<b>Zomato user rating:</b> ' + rest_rating[idx] + '<br>'
                txt = txt + '<br>'
            html = """\
                    <html>
                      <body>
                        <p>Greetings from Foodie!,<br>
                           <h3>Here are the top rated restaurants as per your criteria:</h3> <br>"""
            html = html + txt
            html = html + """
                           <br><b><i>Itadakimasu,</b></i><br><b>Foodie Team</b>
                        </p>
                      </body>
                    </html>
                    """
            msg.attach(MIMEText(html,'html'))
            text = msg.as_string()
           # Create a secure SSL context
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(from_user,password)
                    server.sendmail(from_user,to_user,text)
                    server.close()
                    # Inform the user
                    dispatcher.utter_message("The details have been emailed to you, you should receive it shortly. Bon Appetit!")
            
            except:
                dispatcher.utter_message("Sorry, we are having some problem in sending email to you. Please try after some time")

        print("--- email sending %s seconds ---" % (time.time() - start_time))
        return [SlotSet('email', to_user)] 

