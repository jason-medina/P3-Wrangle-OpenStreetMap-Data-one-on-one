# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 18:36:38 2016

@author: JasonMedina
ref: https://discussions.udacity.com/t/updating-zip-codes/43619

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re


# indicate file to be read
osmfile = "/Users/JasonMedina/Downloads/culver-city_sample.osm"


badzip = { "CA ": ""
           }

# create the dict to put zipcodes into
def add_to_dict(data_dict, item):
    data_dict[item] += 1


# find the zipcodes
def get_postcode(element):
    if (element.attrib['k'] == "addr:postcode"):
        postcode = element.attrib['v']
        return postcode
    #for tag in element:
        #if (tag.attrib['k'] == "addr:postcode"):
            #postcode = tag.attrib['v']
            #return postcode


# update zipcodes
def update_postal(postcode, badzip):
    #postcode = postcode.replace("TX ", "")
    #return postcode
    for v in badzip:
        if postcode is None:
            continue
        else:
            if re.match(v,postcode):
                postcode = postcode.replace(v,badzip[v])
    return postcode


# put the list of zipcodes into dict
def audit(osmfile):
    osm_file = open(osmfile, "r")
    data_dict = defaultdict(int)

    for event, elem in ET.iterparse(osm_file, events=("start",)):  
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if  get_postcode(tag):
                #print postcode
                    postcode = get_postcode(tag)                    
                    postcode = update_postal(postcode, badzip)
                    add_to_dict(data_dict, postcode)
                    return data_dict


# test the zipcode audit and dict creation
def test():
    cleanzips = audit(osmfile)
    pprint.pprint(dict(cleanzips))
            


if __name__ == '__main__':
    test()

"""
import re
import xml.etree.cElementTree as cET

osmfile = "/Users/JasonMedina/Downloads/culver-city_sample.osm"

#takes osm xml file to creates postcode dictionary for node & way tags
def audit_zipcodes(osmfile):
    # open osm xml file as read-only
    osm_file = open(osmfile, "r")
    # create dictionary for zip_codes    
    zip_codes = {}
    # iterative parsing
    for event, elem in cET.iterparse(osm_file, events=("start",)):
        # node and way tags only        
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                # search for postcode keys not starting with 90                
                if tag.attrib['k'] == "addr:postcode" \
                    and re.compile(r'^90\d{3}$') and tag.attrib['v'].startswith('90'):
                    # count of zip codes not starting with 90         
                    if tag.attrib['v'] not in zip_codes:
                        zip_codes[tag.attrib['v']] = 1
                    else:
                        zip_codes[tag.attrib['v']] += 1
    return zip_codes

zipcodes = audit_zipcodes(osmfile)
for zipcode in zipcodes:
    print zipcode, zipcodes[zipcode]


# convert dict to list  
zip_list = dict.items(zipcodes)
print(type(zip_list[0]))


postcodes = re.match(r'^90\d{3}$', str(zip_list[0]))

print(postcodes)
print "text\n"
print "text"

zip_code_re = re.compile(r'(\d{5})')


def get_zip_codes(filename):
    zips = set()
    for _, element in cET.iterparse(filename):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if 'k' in tag.attrib and tag.attrib['k'] == "addr:postcode":
                    zips.add(tag.attrib['v'])
    return zips

def update_zip_code(zip):
    matched = zip_code_re.match(zip)
    if matched:
        zip_code = int(matched.group(1))
        return zip_code
    return None

print(update_zip_code(str(postcodes)))
"""