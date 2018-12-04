import params
import requests
from requests.auth import HTTPDigestAuth
import json
import pprint
import pymongo
from pymongo import MongoClient

# Single octet whitelist entries
single_octets = []

# Return the 1st 2 octets of an IP address
def getNetwork(ip):
    ip_octets = ip.split('.')

    # Track whitelist entries that only define the 1st octet.
    if ip_octets[1] == "0":
        single_octets.append(ip_octets[0])

    # If the IP address is in our list of single octet whitlist entries, then just return this 1st octect
    if ip_octets[0] in single_octets:
        network = ip_octets[0]
    else:
        network = ip_octets[0] + "." + ip_octets[1]

    return network

# Establish connection to Atlas
client = MongoClient(params.conn_string)
db = client[params.database]

## Set up PrettyPrinter
pp = pprint.PrettyPrinter(depth=6)

## Get Whitelist Entries
url = "https://cloud.mongodb.com/api/atlas/v1.0/groups/" + params.project_id +"/whitelist"
resp = requests.get(url, auth=HTTPDigestAuth(params.user, params.password))

if(resp.ok):

    ## Grab the white list entries, remove the subnet mask and create a new dict w/ just the 
    ## first 2 octets a they key. 

    # A new dict for the whitelist entries
    whitelist_clean = {}

    # Convert the JSON response to a dict
    whitelist = json.loads(resp.content)    
    print ("Their are {0} whitelist entries".format(len(whitelist["results"])))
    
    ## Pretty print the results
    #print(json.dumps(jData, indent=4, sort_keys=True))
    #print (jData["results"])
    
    # Get the IP Address and Description and add to the new whitelist_clean dict
    for key in whitelist["results"]:
        description = key['comment']       
        cidr = key['cidrBlock']
        whitelist_ip_mask = cidr.split('/')
        whitelist_ip = whitelist_ip_mask[0]
        ## Ideally the whitelist entry includes at least 2 octets of the IP address. If not, we'll deal with it.
        network = getNetwork(whitelist_ip)
        entry = {}
        entry['ip'] = whitelist_ip
        entry['desc'] = description
        whitelist_clean[network] = entry

    # pp.pprint(whitelist_clean)

    # Get the current operations running on MongoDB
    opData = db.current_op(True)
    print ("Their are {0} current operations".format(len(opData['inprog'])))
    
    #pp.pprint(opData['inprog'])
    
    # Drop the existing operations and connection_analysis collection
    db.operations.drop()
    db.connection_analysis.drop()

    for op in opData['inprog']:
        
        # Store the current operations in MongoDB (this is optional)
        #db.operations.insert_one(op)
        
        # Create a new connection object to store in MongoDB
        conn = {}
        conn['active'] = op['active']

        # We're most intersted in operations that have a client
        if 'client' in op:
            client = op['client']
            client_ip_port = client.split(':')
            client_ip = client_ip_port[0]

            conn['ip'] = client_ip

            network = getNetwork(client_ip)

            if network in whitelist_clean:    # This will skip local IPs like 192. or 127.
                conn['desc'] = whitelist_clean[network]['desc']
            else:
                conn['desc'] = 'System'
        
        # Log operations w/out a client (internal w/ no whitelist entry)
        else:
            conn['desc'] = op['desc']

        # Add the record to MongoDB
        db.connection_analysis.insert_one(conn)


else:
    resp.raise_for_status()

print("Analysis Complete")