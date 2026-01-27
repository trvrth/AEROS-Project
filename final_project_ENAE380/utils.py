"""
utils.py

Trevor Thomas

ENAE 380

Section: 0106

12/14/25

"""
import os
import json

#finds data directory path
DATA_DIR = os.path.join(os.path.dirname(__file__), "data") 
#  __file__ is the path of current python file, and .join joins data and file path

def ensure_data_dir():
    # ensures that a path exists 
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR) #creates folder if no folder exists

def json_path(filename):
    #generates full path to JSON file inside data folder
    ensure_data_dir() #ensures path
    return os.path.join(DATA_DIR, filename) # returns a join between data directory and file

def load_json(filename, default_data):
    """
    Load JSON located in ./data/<filename>. If it doesn't exist, create it with default_data.
    Returns a dict.
    """
    path = json_path(filename) # find filename's paths
    if not os.path.exists(path):
        with open(path, "w") as f: #if path doesnt exists, open in write mode
            json.dump(default_data, f, indent=4) # writes json file
        return default_data.copy() # returns data copy
    with open(path, "r") as f: # opens in read mode if path exists
        return json.load(f) # converts into python dictionary

def save_json(filename, data): 
    #saves json file
    path = json_path(filename) #finds path
    with open(path, "w") as f: # opens in write mode
        json.dump(data, f, indent=4) # makes dictionary or overwrites it
