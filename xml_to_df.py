import pandas as pd
from datetime import datetime as dt
import requests
from bs4 import BeautifulSoup
import numpy as np
import time

def parse_element(element, parsed=None):
    """ Collect {key:attribute} and {tag:text} from thie XML
    element and all its children into a single dictionary of strings."""
    try: 
        if parsed is None:
            parsed = dict()

        for tag in element.descendants:
            #this if necessary because bs4 reads strings as tags with None name
            if tag.name is not None:
                #set the key in the dictionary (aka the bit that becomes the field name to the tag name)
                key = tag.name
                #if the tag has a parent, then prepend the soon-to-be field name with the parent tag names (up to "entry")
                for parent in tag.parents:
                    if parent.name == 'entry':
                        break
                    elif parent is not None:
                        key = parent.name+'_'+key
                
                #for tags with attributes, append the attribute name to the soon-to-be field name
                for att in tag.attrs:
                    key1 = key+'_'+str(att)
                    if key1 not in parsed:
                        parsed[key1] = tag.attrs[att]
                    else:
                        parsed[key1] = parsed[key1]+','+tag.attrs[att]
                    
                #actually get the text from between the tags. If there is more than one tag with the same name (such as source_category), then concatenate the values as a comma separated string 
                if tag.string:
                    if key not in parsed:
                        parsed[key] = tag.string
                    else:
                        parsed[key] = parsed[key]+','+tag.string

        return parsed
    except Exception as e:
        logger.error(e)  

def parse_entries (all_entries,list):
    #for each "entry" parse all the tags
    try:
        for entry in all_entries:
            row = parse_element(entry)
            list.append(row)
    except Exception as e:
        logger.error(e)

# this is the list that will get converted to a df
l = []

#location of the xml you want to parse
url = r'https://www.amnesty.org/en/rss/'

# this variable is whatever the top level tag of the thing you want to parse is. In this case, 'item'
parent_tag = 'item'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'xml')
parse_entries(soup.find_all(parent_tag),l)

df = pd.DataFrame(l)
