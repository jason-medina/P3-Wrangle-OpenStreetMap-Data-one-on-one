# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:08:06 2016

@author: JasonMedina
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

filename = "/Users/JasonMedina/Downloads/culver-city_ca.osm"

# tested at http://www.regextester.com/
# regex to match last token in a string optionally ending in a period
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# list of expected street names, nb directions, floor, CA & phone/suite nums  
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", 
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons",
            "Plaza", "Pointe", "Circle", "Stars", "Way", "Terrace", "Marina",
            "Seabluff", "East", "South","North", "floor", "CA",
            "777-5877","246-0756","308","200","276-1562", "3190","858-1383"] 

# mapping with better names
mapping = { "Ave": "Avenue",
            "Ave,": "Avenue",
            "ave": "Avenue",
            "avenue": "Avenue",
            "Bl.": "Boulevard",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Bvd": "Boulevard",
            "St": "Street",
            "St.": "Street",
            "Dr": "Drive",
            "Rd.": "Road",
            "Rd": "Road",
            "Ln": "Lane",
            "A": "Drive",
            "E": "East",
            "Sepulveda": "Sepulveda Boulevard",
            "Centinela": "Centinela Avenue"
            }
            
# search for street names 
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# return street name attribute
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
    
def audit(filename):    
    # open osm xml file
    file_name = open(filename, "r")
    
    # initalize data storage
    street_types = defaultdict(set)
    
    # use interparse to sift elements
    for event, elem in ET.iterparse(file_name, events=("start",)):
        # check if tags are ways or node
        if elem.tag == "node" or elem.tag == "way":
            # iterate through tag children
            for tag in elem.iter("tag"):
                # audit if street name
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                    
    file_name.close()
    return street_types
    
def update_name(name, mapping):
    m = street_type_re.search(name)
    better_name = name
    if m:
        better_street_type = mapping[m.group()]
        better_name = street_type_re.sub(better_street_type, name)
        better_name = better_name.title()
        
    return better_name
    
street_types = audit(filename)

# show list of street types at top level
print "\n--List of unexpected street types\n"
print '\n'.join(street_types)

print "\n~~~~~new output~~~~~"
print "\n"

# show dict street types
print "\n--Dictionary with unexpected street types and values\n" 
pprint.pprint(dict(street_types))

print "\n~~~~~new output~~~~~\n"

# print names with new better name
print "\n--List of old and new street names\n"
for street_type, ways in street_types.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print name, "=>", better_name, "\n"