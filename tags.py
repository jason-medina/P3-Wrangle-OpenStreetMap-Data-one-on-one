# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 08:06:42 2016

@author: JasonMedina
"""

import xml.etree.ElementTree as ET
import pprint
import re

filename = "/Users/JasonMedina/Downloads/culver-city_ca.osm"

#for tags that contain only lowercase letters and are valid 
lower = re.compile(r'^([a-z]|_)*$') 
#for otherwise valid tags with a colon in their names
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
#for tags with problematic characters  
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# checks to see if "k" value for each tag can be valid keys in MongoDB
def key_type(element, keys):  
    if element.tag == "tag":
        for tag in element.iter('tag'):
            k = tag.get('k')
            if lower.search(k):
                keys['lower'] += 1
            elif lower_colon.search(k):
                keys['lower_colon'] += 1
            elif problemchars.search(k):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1

    return keys
    
#"other", for other tags that do not fall into the other three categories
def process_map(filename):  
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}

    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

keys = process_map(filename)  
pprint.pprint(keys)