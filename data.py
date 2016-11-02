# -*- coding: utf-8 -*-
"""
Created on Thu Oct 06 10:40:47 2016

@author: JasonMedina
"""

import xml.etree.cElementTree as cET
import re
import codecs
import json
import string
import pprint
from collections import defaultdict


# set filename to sample data
# /!\ update file name in two places, see line 154 for json file size
filename = "/Users/JasonMedina/Downloads/culver-city_sample.osm"
path = "/Users/JasonMedina/Downloads"


# common regex to identify problemchars
lower = re.compile(r'^([a-z]|_)*$') 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# valid ending street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", 
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons",
            "Plaza", "Pointe", "Circle", "Stars", "Way", "Terrace", "Marina",
            "Seabluff", "East", "South","North"]
            
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
            "Centinela": "Centinela Avenue"}
 
# update street names
def update_name(name, mapping):    
    for key in mapping:
        if key in name:
            name = string.replace(name,key,mapping[key])
    return name
"""
The function below will use a regex to update the zip codes
this function.  Each zip code should be 5 digits long starting with 90.
"""          

badzip = { "CA ": ""
           }

# dict for zip codes
def add_to_dict(data_dict, item):
    data_dict[item] += 1


# find zip codes
def get_postcode(element):
    if (element.attrib['k'] == "addr:postcode"):
        postcode = element.attrib['v']
        return postcode
    
# update zip codes
def update_postal(postcode, badzip):
        for v in badzip:
            # skip records without postcode to contain none values            
            if postcode is None:
                continue
            else:
                if re.match(v,postcode):
                    postcode = postcode.replace(v,badzip[v])
        return postcode

    
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    node["created"]={}
    node["address"]={}
    node["pos"]=[]
    refs=[]
    
    # only process node and way tags
    if element.tag == "node" or element.tag == "way" :
        if "id" in element.attrib:
            node["id"]=element.attrib["id"]
        node["type"]=element.tag

        if "visible" in element.attrib.keys():
            node["visible"]=element.attrib["visible"]
      
        # key-value pairs with attributes from CREATED list
        for elem in CREATED:
            if elem in element.attrib:
                node["created"][elem]=element.attrib[elem]
                    
        # appending lat and lon to pos array
        
        if "lat" in element.attrib:
            node["pos"].append(float(element.attrib["lat"]))
        
        if "lon" in element.attrib:
            node["pos"].append(float(element.attrib["lon"]))

        # exclude problem characters and update_names
        for tag in element.iter("tag"):
            if not(problemchars.search(tag.attrib['k'])):
                if tag.attrib['k'] == "addr:housenumber":
                    node["address"]["housenumber"]=tag.attrib['v']
                    
                if tag.attrib['k'] == "addr:postcode":
                    node["address"]["postcode"]=tag.attrib['v']
                    if  get_postcode(tag):
                            postcode = get_postcode(tag)                    
                            postcode = update_postal(postcode, badzip)
                            # initialize default dictionary                            
                            data_dict = defaultdict(int)
                            add_to_dict(data_dict, postcode)
                            return data_dict                    
                    
                if tag.attrib['k'] == "addr:street":
                    node["address"]["street"]=tag.attrib['v']
                    node["address"]["street"] = \
                    update_name(node["address"]["street"], mapping)

                if tag.attrib['k'].find("addr")==-1:
                    node[tag.attrib['k']]=tag.attrib['v']
                    
        for nd in element.iter("nd"):
             refs.append(nd.attrib["ref"])
                
        if node["address"] =={}:
            node.pop("address", None)

        if refs != []:
           node["node_refs"]=refs
            
        return node
    else:
        return None

# set pretty to false for large files
# see data.py quiz for reference: creates json output
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in cET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

# run mongod.exe from /cygdrive/c/'Program Files'/MongoDB/Server/3.2/Bin
# from cygwin else connection refused
data = process_map(filename,True)

# inserting data can take several minutes
import os
from pymongo import MongoClient
client = MongoClient()
db = client.culverCityOSM
collection = db.culverCityMAP
collection.insert_many(data)

# file size for new json
# note suboptimal hardcoded file name in os.path.join
print "\nNew json file size"
print(os.path.getsize(os.path.join(path\
# change file name up to culver-city_sample - leave .osm.json
, "culver-city_sample.osm.json"))/1024/1024)

# file size for original XML
print "\nOriginal xml file size"
print(os.path.getsize(filename)/1024/1024)

# number of documents
print "\nDocument count"
print(collection.count())

print "\nNode count"
# count nodes
print(collection.find({"type":"node"}).count())

print "\nWay count"
# count ways
print(collection.find({"type":"way"}).count())

print "\nUU count"
# count distinct users
print(len(collection.group(["created.uid"], {}, {"count":0}\
    ,"function(o, p){p.count++}")))

print "\nTop 10 Users"
# top ten users
pipeline = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)


print "\nRatio of user contributions\n" 
# top ten users ratio of countributions
pipeline = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$project": {"ratio": {"$divide" :["$count"\
            ,collection.find().count()]}}},
            {"$sort": {"ratio": -1}},
            {"$limit": 10}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

print "\nTop 20 sources"
# top 20 sources
pipeline = [{"$match":{"source":{"$exists":1}}},
            {"$group":{"_id": "$source",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit":20}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

print "\nAmenities near me"    
# amenities near me
# exclude any document without amenity or name
pipeline = [{"$match":{"amenity":{"$exists":1}, "name":{"$exists":1}}},  
            {"$group":{"_id":"$amenity", "count":{"$sum":1}}},
            {"$sort":{"count":-1}},
            {"$limit":30}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

print "\nTop ten count different fast food amenities"    
# top ten count different fast food amenities
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"fast_food"\
            , "name":{"$exists":1}}},
            {"$group":{"_id":"$name", "count":{"$sum":1}}},
            {"$sort":{"count":-1}},
            {"$limit":10}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

print "\nSample restaurant amenity data"
# sample data for restaurant amenity
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant" \
            , "name":{"$exists":1}}},
            {"$sort":{"count":-1}},
            {"$limit":3}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)  

print "\nRestaurant amenties by cusine type"
# restaurant amenities by cusine type
pipeline = [{"$match":{"amenity":{"$exists":1} #, "amenity":"restaurant"\
            , "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

print "\nOpening Hours for cafes"
# opening hours for cafe amenity
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"cafe" \
            , "opening_hours":{"$exists":1}}},
            {"$group":{"_id":"$opening_hours", "count":{"$sum":1}}},
            {"$sort":{"count":-1}},
            {"$limit":20}]
result = collection.aggregate(pipeline)
for doc in result:
    pprint.pprint(doc)

#remove data for cleansing
collection.remove()