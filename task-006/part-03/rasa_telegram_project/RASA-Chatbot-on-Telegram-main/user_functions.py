# Function to get the Soundex code of a word token
def get_soundex(token):
   
    token = token.upper()

    soundex = ''
    
    # First letter of input is always the first letter of soundex
    soundex += token[0]
    
    # Create a dictionary which maps letters to respective soundex codes. Vowels and 'H', 'W' and 'Y' will be represented by '.'
    dictionary = {"BFPV": "1", "CGJKQSXZ":"2", "DT":"3", "L":"4", "MN":"5", "R":"6", "AEIOUHWY":"."}

    # Figure out the soudex code for each of the letters in the word
    for char in token[1:]:
        for key in dictionary.keys():           
            if char in key:
                # Get the code for the letter
                code = dictionary[key]
                # Do not include AEIOUHWY
                if code != '.':
                    # Do not repeat the code of the last letter
                    if code != soundex[-1]:
                        soundex += code
    
    # Trim or pad to make soundex a 4-character code
    soundex = soundex[:4].ljust(4, "0")

    # Return the Soundex code    
    return soundex

########################################################################################################
# Function to check if a given action was executed earlier or not
def get_last_action(events, actionname):

    # Goes back through the list of events and finds if an action was called or not
    for event in reversed(events):
        if event.get('name') == actionname:
            return True

    return False