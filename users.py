# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 09:32:09 2016

@author: JasonMedina
"""

import xml.etree.ElementTree as ET
import pprint

filename = "/Users/JasonMedina/Downloads/culver-city_sample.osm"

# get user attribute, uid also works
def get_user(element):
    user = element.attrib['user']
    
    return user

# returns set of unique users
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "node" or element.tag == "way":
            users.add(get_user(element))
            
    return users

# run function with process map
def run(filename):
    users = process_map(filename)
    # pprint.pprint will print a list of all users
    pprint.pprint(users)

# execute run to see user names    
run(filename)

# print user count
users = process_map(filename)
print len(users)