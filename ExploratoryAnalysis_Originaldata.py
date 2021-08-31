#!/usr/bin/env python
# coding: utf-8

# ## OpenStreetMaps Project- Mapping Trenton, Princeton & Plainsboro City Area,  New Jersey
# ### Udacity Data Science Nanodegree course- Final Project
# ## Data Wrangling with Mongo DB
# ### By: Mubina Arastu
# ### MArastu@wgu.edu
# 

# ## Summary
# This project details my analysis and cleanup of the OpenStreetMap.org map data for the majority of Trenton, Princeton & Plainsboro cities of New Jersey. I focused on street addresses and amenities listed within the map.I choose these cities because I live and work in these areas.
# #### I have used sample OSM data 9.5 MB (9528 kb) and the original size of OSM file (150 MB) for this project. Both the compressed XMLs are provided for the reviewer. This report is based on original XML data.
# This writeup list out few problems that were encountered in the dataset, and gives an high level overview of the data. Exploratory data analysis, wrangling and cleaning of this project can be seen in python notebook.
# 
# ## Problems With the Dataset
# Initialy I faced difficulty in downloading a reasonable size dataset. After few attempts, I finally downloaded sample OSM file that includes Trenton area of New Jersey.
# 
# As per my exploratory analysis of the dataset, I found few issues that need to be cleaned up:
# 
# 1. Over abbreviated city names like (“Twp”,"twp) to clean up.
# 2. Over abbreviated Street types like ("Blvd") to clean up.
# 3. Wrong street type like 'Nassau Parl Blvd" to clean up
# 3. Brand names doesn't have a 'type' tag. "Wikipedia" tag need to be updated as "type".
# 4. Amenities like shops have some wierd data like 'doityourself" to clean up.
# 
# 

# ### Check Tag Types & Map Area Boundaries

# In[1]:


## Create a variable to store xml file name
file='Trenton-Princeton_original.xml'


# In[2]:


import xml.etree.ElementTree as ET
import pprint

#Below code is to find max and minimum latitude and longitude of the map area
def count_tags(filename):
    tags = {}
    bounds = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag == "bounds":
            for latlong in elem.attrib:
                bounds[latlong] = elem.attrib[latlong]
        if elem.tag in tags.keys():
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags, bounds

## below code is to read from the file
with open(file, 'rb') as mapfile:
    tags, bounds = count_tags(mapfile)
    print ("Found number oftags:")
    pprint.pprint(tags)
    print ("\nMap Area Boundaries:")
    pprint.pprint(bounds)


# ### Check k-values
# 
# Below code is to check if there are any k values with special characters and also to see K:Ktype colon seperated pairs.
# Below code is to check if there are any k values with special characters and also to see K:Ktype colon seperated pairs.

# In[7]:


import xml.etree.ElementTree as ET
import pprint
import re


## Below code is to check if there are any k values with special characters and also to see K:Ktype colon seperated pairs. 

lowercase_characters = re.compile(r'^([a-z]|_)*$')
lowercase_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
specialchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
lowercase_colon_vals = {}

##Key_type function search for lower case characters,lower case and colon values and special characters if any.
def key_type(element, keys):
    if element.tag == "tag":
        kval = element.attrib['k']
        if re.search(lowercase_characters, kval):
            keys['lower case'] += 1
        elif re.search(lowercase_colon, kval):
            keys['lower case & colon values'] += 1
            colvals = kval.split(':')
            if colvals[0] not in lowercase_colon_vals.keys():
                lowercase_colon_vals[colvals[0]] = set()
            lowercase_colon_vals[colvals[0]].add(colvals[1])
        elif re.search(specialchars , kval):
            keys['special characters'] += 1
        else:
            keys['other'] += 1
        
    return keys

## Below function "check_KValues" returns key type element
def check_KValues(filename):
    keys = {"lower case": 0, "lower case & colon values": 0, "special characters": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

## below code is to read from the file
with open(file, 'rb') as mapfile:
    keys = check_KValues(mapfile)
    print ("Types of k-values and their counts:")
    pprint.pprint(keys)
    print ("Types of colon-separated k-values:")
    pprint.pprint(lowercase_colon_vals)


# ### One of the tag that starts with brand has a subtype as 'wikipedia'. Will change it to 'Type'.

# In[8]:


import xml.etree.ElementTree as ET
from collections import defaultdict
import pprint

#below function is used to update tag that starts with 'brand' and has a k value of 'wikipedia' to 'type'.
def append_type(filename):
    brands = defaultdict(set)
    for event, elem in ET.iterparse(mapfile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                k = tag.attrib['k'] 
                v = tag.attrib['v']
                if k.startswith('brand'):
                    ka = k.split(':')  # create a list of k-values, split on : (creates array of len 1 if no :)
                    if len(ka) == 1:  # wasn't colon-separated, so was a "type" of lift. Create "type" of lift
                        ka.append('type')
                    if ka[1] == 'wikipedia': # bad tag -- ignore it
                        continue
                    else:
                        brands[ka[1]].add(v)
    return brands

#below code is to read the fie
with open(file, 'rb') as mapfile:
    brands = append_type(mapfile)
    pprint.pprint(brands)


# ## Check Unique User Ids and Names

# In[10]:


import xml.etree.ElementTree as ET
import pprint
import re

## This function is to get the UID
def get_userid(element):
    return element.attrib['uid']

# This function is to get the User
def get_username(element):
    return element.attrib['user']

# This function is to process map uid and usernames
def get_distinctUsers(filename):
    userids = set()
    usernames = set()
    for _, element in ET.iterparse(filename):
        if 'uid' in element.attrib.keys():
            userid = get_userid(element)
            userids.add(userid)
        if 'user' in element.attrib.keys():
            username = get_username(element)
            usernames.add(username)

    return userids, usernames

with open(file, 'rb') as mapfile:
    userids, usernames = get_distinctUsers(mapfile)
    print ("There are %d unique user IDs" % len(userids))
    print ("There are %d unique usernames" % len(usernames))


# ## Auditing Street Types & Cities
# ### Find if there are any possible street type problems

# In[12]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

## create a list expetced that has expected values for street types
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

## below function is used to match street type with 'expected' street type values and find if there are any unexpected vallues.
def audit_street_type(street_types, street_name, street_types_count):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in street_types_count.keys():
            street_types_count[street_type] = 1
        else:
            street_types_count[street_type] += 1
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
    return street_types_count

##below function is used to store colon seperatd k value into element
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

## below function returns unexpected street types and unexpected street types counts
def audit(mapfile):
    street_types = defaultdict(set)
    street_types_count = {}
    for event, elem in ET.iterparse(mapfile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    street_types_count = audit_street_type(street_types, tag.attrib['v'], street_types_count)

    return street_types, street_types_count

##open file
with open(file, 'rb') as mapfile:
    street_types, street_types_count = audit(mapfile)
    print ("Find if there are any street type problems:")
    pprint.pprint(street_types)
    print ("Count of Street Types:")
    pprint.pprint(street_types_count)
    
    
############################################    
 ### below code is to find if any issues with city names
import xml.etree.ElementTree as ET
import pprint

def find_city_errors(filename):
    city = defaultdict(set)
    for event, elem in ET.iterparse(mapfile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                k = tag.attrib['k'] 
                v = tag.attrib['v']
                if k.startswith('addr:city'):
                    ka = k.split(':')  # create a list of k-values, split on : (creates array of len 1 if no :)
                    if len(ka) == 1: 
                        if ka[1] == 'city': 
                            continue
                    else:
                        city[ka[1]].add(v)
    return brands

##Open file
with open(file, 'rb') as mapfile:
    city = find_city_errors(mapfile)
    pprint.pprint(city)
    
    


# ### Following issues are found from above output: I will handle these issues in Mongo DB.
# 1. Abbreviated terms like: twp,Twp. These should be changed to Township.
# 2. Wrong spelling found: Nassau Parl Blvd- It should be Nassau Park Boulevard.

# ### First clean up data and then save into JSON file format.¶

# In[14]:


import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    pos = ['lat', 'lon']
    created = ['version', 'changeset', 'timestamp', 'user', 'uid']
    if element.tag == "node" or element.tag == "way" :
       
        node['created'] = {}
        node['type'] = element.tag
        for attrib, value in element.attrib.items():
            if attrib in pos:
                if 'pos' not in node.keys():  
                    node['pos'] = [0,0]  # only create position sub-document if position is one of the attributes
                if attrib == 'lat':
                    node['pos'][0] = float(value)
                else:
                    node['pos'][1] = float(value)
            elif attrib in created:
                node['created'][attrib] = value
            else:
                node[attrib] = value
        
# Format addresses into subdocument
        for tag in element.iter("tag"):
            k = tag.attrib['k']
            v = tag.attrib['v']
            if k.startswith('addr'): # Format addresses into subdocument
                addrtag = k.split(':')
                if len(addrtag) > 2:
                    continue
                if 'address' not in node.keys():
                    node['address'] = {}
                node['address'][addrtag[1]] = v
#Below code is to Format brand into types
            elif k.startswith('brand'):
                atag = k.split(':')  # create a list of k-values, split on :
                if len(atag) == 1:  
                    atag.append('type')
                if atag[1] == 'wikipedia': # bad tag -- ignore it
                    continue
                if 'brand' not in node.keys():
                    node['brand'] = {}
                node['brand'][atag[1]] = v
                #else:
                #node[k] = v
                
        for tag in element.iter("nd"):
            if 'node_refs' not in node.keys():
                node['node_refs'] = []
            ref = tag.attrib['ref']
            node['node_refs'].append(ref)
    
    return node

## Write to Json file- write corrected xml into JSON
def create_JSON(file_in, pretty = False):
    file_out = "Trenton_Princeton_original_Maps.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data



with open(file, 'rb') as mapfile:
    data_array = create_JSON(mapfile, False)


# ## Auditing ends here. Data is loaded into JSON. Rest of the data cleanup will be done in Mongo DB.

# # MongoDB
# ## Open Connection to MongoDB
# 

# In[15]:


#import modules
import pymongo
from pymongo import MongoClient
import pprint

#Open Connection
client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000')


# ## Open Database

# In[16]:


#Open Database
db = client.db_Trenton_Princeton
db = client['db_Trenton_Princeton']
print(db)


# ## Print Collections

# In[17]:


#Print Collections
collections = db.list_collection_names()
print ("collections:", collections, "\n")


# ### For this project we will be using collection: TrentPrincemaps

# ### Lets clean up street types and city errors found while auditing 

# In[128]:


# Using update_one function to update 'twp' to Township
city=db.TrentPrincemaps
city.update_many({'address.city': 'Hopewell twp'}, {'$set': {'address.city': 'Hopewell Township'}})
city.update_many({'address.city': 'Ewing twp'}, {'$set': {'address.city': 'Ewing Township'}})
city.update_many({'address.city': 'Princeton twp'}, {'$set': {'address.city': 'Princeton Township'}})
city.update_many({'address.city': 'West windsor twp'}, {'$set': {'address.city': 'West Windsor Township'}})
city.update_many({'address.city': 'Lawrence Twp'}, {'$set': {'address.city': 'Lawrence Township'}})


# In[126]:


#Get all cities
cityreplaced  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$address.city", 
         "count" : {"$sum" : 1}}},
          { '$sort' : { 'count' : -1 } }
                             ])
for k in cityreplaced:
    print(k)


# In[136]:


# Using update_many function to clean street error
street=db.TrentPrincemaps
street.update_many({'address.street': 'Nassau Parl Blvd'}, {'$set': {'address.street': 'Nassau Park Boulevard'}})
street.update_many({'address.street': 'Nassau Park Blvd'}, {'$set': {'address.street': 'Nassau Park Boulevard'}})


# ### Find Documents

# In[127]:


db.TrentPrincemaps.count_documents({}) 


# ## Find Nodes

# In[19]:


#Find Nodes
nodes=db.TrentPrincemaps.count_documents({'type':'node'}) 
pprint.pprint("count of nodes")
pprint.pprint(nodes)


# ## Find Ways

# In[20]:


#Find Ways
ways=db.TrentPrincemaps.count_documents({'type':'way'})
pprint.pprint("count of ways")
pprint.pprint(ways)


# ## Find unique Users

# In[9]:


u=len(db.TrentPrincemaps.distinct('created.user'))
pprint.pprint("Number of Unique Users")
pprint.pprint(u)


# ## Top 5 Users

# In[21]:


topusers  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$created.user", 
         "count" : {"$sum" : 1}}},
          { '$sort' : { 'count' : -1 } }, { '$limit' : 5 }
                             ])
for k in topusers:
    print(k)


# ## Find Amenities & Highways

# In[22]:


#Find Service Highways
s=db.TrentPrincemaps.count_documents({"highway": "service"})
pprint.pprint("count of services")
pprint.pprint(s)

#Find Residential Highways
r=db.TrentPrincemaps.count_documents({"highway": "residential"})
pprint.pprint("count of residential areas")
pprint.pprint(r)

#Find number of parking sites
p=db.TrentPrincemaps.count_documents({"amenity": "parking"})
pprint.pprint("count of parking areas")
pprint.pprint(p)


# ## List number of shops

# In[26]:


## Aggregate function is used to show olny top 30 shops based on counts sorted in descending order
shops  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$shop", 
         "count" : {"$sum" : 1}}},
          { '$sort' : { 'count' : -1 } }, { '$limit' : 30 }
                             ])
for sh in shops:
    print(sh)


# ### From above data one wierd name 'doityourself' is seen as a shop category. Will change doityourself to 'home_improvement'.

# In[27]:


# Using update_one function to update 'doityourself' to home_improvement
coll=db.TrentPrincemaps
updateResult = coll.update_one({'shop': 'doityourself'}, {'$set': {'shop': 'home_improvement'}})


# ### check if 'doityourself is updated to home_improvement with 1 count'

# In[28]:


## Using aggregate function with limit to show only 10 shops which is sorted from least to highest

updatedshops  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$shop", 
         "count" : {"$sum" : 1}}},
          { '$sort' : { 'count' : 1 } }, { '$limit' : 10}
                             ])
for upsh in updatedshops:
    print(upsh)


# In[29]:


#Count total number of amenities grouped by each amenity and display in  descending sorting order.
#***************************
print('Total Number of Amenities from highest to lowest counts')
from bson.son import SON
s=db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$amenity", 
         "count" : {"$sum" : 1}
         }},  { '$sort' : { 'count' : -1 } }, { '$limit' : 20 }
   
])
for k in s:
    print(k)


# ## Additional Exploration

# ### Number of Offices

# In[30]:


off=len(db.TrentPrincemaps.distinct('office'))
pprint.pprint("Number of Unique offices")
pprint.pprint(off)


# ### List out Offices

# In[31]:


topoffices  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$office", 
         "count" : {"$count" : {}}}},
         
                             ])
for k in topoffices:
    print(k)


# ###  List out Users Posts

# In[32]:


topusers  = db.TrentPrincemaps.aggregate([
    {"$group" : 
        {"_id" : "$created.user", 
         "count" : {"$count" : {}}}},
     { '$sort' : { 'count' : -1 } }
            ])
for k in topusers:
    print(k)


# ### Section 3: Additional Ideas
# Contributor statistics and gamification suggestion: The contributions of users seems incredibly skewed. Here are some user percentage statistics:
# 
# Top user contribution percentage (“iskra32”) - 26%
# Combined top 2 users' contribution (“iskra32”)” and “OceanVortex”) - 42%
# Combined Top 10 users contribution - 62.20%
# Users making up only 5% of posts (1/51079) 
# 
# Looking into these user percentages, I believe “gamification” is a motivating factor for contribution. In the context of the OpenStreetMap, if users data are more accurately displayed then more people will take interest in submitting edits to the map data.

# ### Section 4: Conclusion
# After this review of the data it’s obvious that the Trenton city area is incomplete, though I have cleaned up well for the purpose of this project. However, the improvement may bring more issues if not implemented correctly:
# 
# 1.Gamification may impact the quality of the data submitted from the contributors. We should keep in mind quality is
# more important then quantity.
# 
# 2.If the difference between the highest score and other scores is too large, users may easily loose their interest. Therefore, we should implement the logic in such a way that as the scores rise high, it should become more difficult to increase.
# 
# With a robust data processor, it would possibly input more cleaner data to OpenStreetMap.org.
