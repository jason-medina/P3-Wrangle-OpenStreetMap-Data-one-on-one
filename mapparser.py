# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 15:42:27 2016

@author: JasonMedina
Iterative parsing excercise:
Uses iterative parsing to process OSM file to identify and count tags
"""

import xml.etree.ElementTree as ET
import pprint

filename = "/Users/JasonMedina/Downloads/culver-city_sample.osm"
 
# create dictionary to populate tags
tags = {}

# use iterparse to identify and count new top level tags
for event, elem in ET.iterparse(filename):
    if elem.tag in tags: tags[elem.tag] += 1
    else:                tags[elem.tag] = 1   

# use pretty print to print out count
pprint.pprint(tags)