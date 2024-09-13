# Sophos Firewall API 
#### version v 0.7.0
#
## General Informatin
The Sophos Firewall API is a tool that simplifies the management of Sophos Firewall systems. It follows the CRUD specification, which means that it allows you to create, read, update, and delete firewall entities. While the API is designed to make your daily firewall management tasks easier, it's important to note that there is no guarantee that everything will run seamlessly. You are free to use our code, but please remember that any responsibility for usage falls solely on the user.

***NOTE:***
Sophos Firewall API is still under development.

***Currente library***  
**SophosFirewallAPI.py** It utilizes the ***Jinja2*** library and can be used with the context manager and its own request templates. It supports error and request/response handling.
 
#
## How to Use
To view the entity structure, utilize the **```read(entity_type)```** method.\
The response obtained from this method can be used to generate data for the **```create(entity_type, entity_data)```** and **```update(entity_type, entity_data)```** methods.\
It's worth noting that while the syntax for **```read()```** and **```delete()```** are similar, their operations differ.
#
## Sophos Firewall password encryption

From Advanced Shell run:
```
aes-128-cbc-tool -k Th1s1Ss1mPlygR8API -t 1 -s <PASSWORD>
```
#
## Firewall CRUD API Description

### Entity Type
```python
entity_type = "FirewallRule"
entity_type = "IPHost"
```

For additional information check **entity_type.txt** file.
### Respone Format
API response is Python Diction with following format:
```python
response = {
    "status": "<STATUS_CODE>",
    "message": "<STATUS_DESCRIPTION_TEXT>",
    "data": [
        {...},
        {...},
        ...,
    ],
}
```

### Notes

- The `status` field is used to indicate the result of the API request. Codes are specific to the API's response patterns and might require reference to the API documentation for full understanding.
- The `message` field provides a human-readable explanation of the `status`.
- The `data` field contains the actual results of the query or operation if successful. If there are no records or if an error occurs, this field is an empty list.



### Imports
```python
from SophosFirewallAPI import Firewall, EQ, NOT, LIKE
```

### Initialization with context manager
```python
from SophosFirewallAPI import Firewall, EQ, NOT, LIKE

# Establish a connection to the firewall and read the specified entity type
with Firewall(username, password, firewall_ip, port=4444, certificate_verify=False, password_encrypted=False) as firewall:
    response = firewall.read(entity_type)
    # Code to process the response goes here
```
### Initialization without context manager
```python
from SophosFirewallAPI import Firewall, EQ, NOT, LIKE

firewall = Firewall(username, password, firewall_ip)
firewall = Firewall(username, password, firewall_ip, password_encrypted=True)
firewall = Firewall(username, password, firewall_ip, port, certificate_verify=True, password_encrypted=True)

firewall.close()
```

### You can use only
```python
from SophosFirewallAPI import Firewall, EQ, NOT, LIKE

# Initialize the firewall object with credentials and IP address
firewall = Firewall(username, password, firewall_ip)

# Read the specified entity type from the firewall
response = firewall.read(entity_type)

# Example usage of the firewall object
# Code to interact with the firewall goes here
# The firewall object can be used multiple times as required

# Close the firewall connection when it's no longer needed
firewall.close()
```

### CREATE Entity
Create entity with type **entity_type** from provided **entity_data**.
```python
response = firewall.create(entity_type, entity_data)
```
Some **entity_types** have additional **entity_data** that is required for the creation of the entity.
### READ Entity
Read entity with type **entity_type** and name **entity_name**. You can use **filter_type** for partial read.
```python
response = firewall.read(entity_type)
response = firewall.read(entity_type, entity_name)
response = firewall.read(entity_type, entity_name, filter_type)
```

### UPDATE Entity
Update entity with type **entity_type** with provided **entity_data**.
```python
response = firewall.update(entity_type, entity_data)
```
### DELETE Entity
Delete entity with type **entity_type** and name **entity_name**. You can use **filter_type** for bulk deletion.
```python
response = firewall.delete(entity_type, entity_name)
response = firewall.delete(entity_type, entity_name, filter_type)
```
### Filter Type

```python
EQ      # matches entities with an exact name match
NOT     # matches entities where the name does not match at all
LIKE    # matches entities with partial name matches
```
Filter Type is used for ***Read*** and ***Delete*** operations and applies to **entity_name**.\
Default Filter Type for ***Read Entity*** is **LIKE** and\
Default Filter Type for ***Delete Entity*** is ***EQ***.

## Examples
### Read/Download Entiy/Template
```python
response = firewall.read(entity_type)

response["status"]     # Result Code
response["message"]    # Result Description Text
response["data"]       # Result Data (List of Dict)
```
### Print All **IPHost**
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip)

entity_type = "IPHost"

response = firewall.read(entity_type)
print(f"Status: {response['status']} | Message: {response['message']} | Data: {response['data'] if response['data'] else 'No data available'}")
for index, item in enumerate(response["data"], start=1):
    print(f"{index:002}: {item}")

firewall.close()
```
### Create **IPHost**
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip)

entity_type = "IPHost"
entity_data = {
    "Name": "Host_172.16.17.100",
    "HostType": "IP",
    "IPAddress": "172.16.17.100",
}

firewall.create(entity_type, entity_data)
firewall.close()
```
### Read all **FirewallRules**
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip)

entity_type = "FirewallRule"

response = firewall.read(entity_type)

print(f"Status: {response['status']} | Message: {response['message']} | Data: {response['data'] if response['data'] else 'No data available'}")
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

firewall.close()
```
### Read all **IPHost** entities with **entity_name** in the Name
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip)
entity_type = "IPHost"
entity_name = "Internet"

print(f"\nREAD :: {entity_type} entity with {entity_name} in the 'Name'")
response = firewall.read(entity_type, entity_name)    # LIKE by Default
print(f"Status: {response['status']} | Message: {response['message']} | Data: {response['data'] if response['data'] else 'No data available'}")
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

```