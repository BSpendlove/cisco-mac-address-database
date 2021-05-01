# cisco-mac-address-database
A basic Database + Flask API to store MAC addresses in a database. API returns JSON data for MAC addresses. This is a test flask application that shouldn't be used in production because passwords are stored in the database as plain text to be used during the SSH session.

This app is an example on being able to obtain the network state for current MAC addresses in the network and allows the database to be maintained (automatically removes stale mac entries and adds new/updates existing mac entries in the mac_entry table...)

You can find below some documentation on the different routes/views for the API and examples of the returned output.

Don't use this in production, use something more scalable (if you don't want cancer, don't use ansible) like netpalm...

---

## API Views:
### /api/v1/<view>

#### /api/v1/users/
[GET] - Returns a list of all the users configured in the database
```json
{
    "data": [
        {
            "devices": [
                1
            ],
            "id": 1,
            "password": "ciscodisco",
            "secret": "ciscodisco",
            "username": "cisco"
        },
        {
            "comment": "more entries here..."
        }
    ],
    "error": false
}
```

#### /api/v1/users/<int:id>
[GET] - Returns JSON format of the user if it exist
```json
{
    "data": [
        {
            "devices": [
                1
            ],
            "id": 1,
            "password": "ciscodisco",
            "secret": "ciscodisco",
            "username": "cisco"
        }
    ],
    "error": false
}
```


[POST] - Creates a User and returns the JSON format of the created user if it doesn't exist
```json
{
    "data": [
        {
            "devices": [],
            "id": 2,
            "password": "ciscodisco",
            "secret": "ciscodisco",
            "username": "apiusertest"
        }
    ],
    "error": false
}
```

[DELETE] - Deletes a User and returns generic JSON response
```json
{
    "error": false,
    "message": "Successfully deleted user 2."
}
```

[PATCH] - Updates information for a given user if they exist. Returns the JSON format after successfully updating the device.
```json
{
    "data": [
        {
            "devices": [
                1
            ],
            "id": 1,
            "password": "newpassword",
            "secret": "ciscodisco",
            "username": "cisco"
        }
    ],
    "error": false
}
```

#### /api/v1/devices/
[GET] - Returns a list of all the devices configured in the database
```json
{
    "data": [
        {
            "authentication_user": 1,
            "friendly_name": "CSW01",
            "id": 1,
            "ip": "192.168.0.252",
            "mac_entries": [
                {
                    "address": "0100.0ccc.cccc",
                    "port": "CPU"
                }
            ],
            "netmiko_driver": "cisco_ios",
            "port": 22
        },
        {
            "comment": "more entries here..."
        }
    ],
    "error": false
}
```

#### /api/v1/devices/<int:id>
[GET] - Returns JSON format of the device if it exist
```json
{
    "data": [
        {
            "authentication_user": 1,
            "friendly_name": "CSW01",
            "id": 1,
            "ip": "192.168.0.252",
            "mac_entries": [
                {
                    "address": "0100.0ccc.cccc",
                    "port": "CPU"
                },
                {
                    "comment": "more entries here..."
                }
            ],
            "netmiko_driver": "cisco_ios",
            "port": 22
        }
    ],
    "error": false
}
```

[POST] - Creates a Device and returns the JSON format of the created device if it doesn't exist
```json
{
    "data": [
        {
            "authentication_user": 1,
            "friendly_name": "CSW02",
            "id": 2,
            "ip": "192.168.0.253",
            "mac_entries": [],
            "netmiko_driver": "cisco_ios",
            "port": 22
        }
    ],
    "error": false
}
```

[DELETE] - Deletes a Device and returns generic JSON response
```json
{
    "error": false,
    "message": "Successfully deleted device 2."
}
```

[PATCH] - Updates information for a given device if it exist. Returns the JSON format after successfully updating the device.
```json
{
    "data": [
        {
            "authentication_user": 1,
            "friendly_name": "CSW01",
            "id": 1,
            "ip": "192.168.0.252",
            "mac_entries": [
                {
                    "address": "0100.0ccc.cccc",
                    "port": "CPU"
                },
                {
                    "comment": "more entries here..."
                }
            ],
            "netmiko_driver": "cisco_asa",
            "port": 22
        }
    ],
    "error": false
}
```

---

### Important Note

There is a slight difference on the flask views below. If you include /ssh in the route, they will invoke an SSH session, create/update entries in the database and return them as intended.

However if you would like to just query the current information in the database without invoking an SSH session and creating/updating the current entries within the database, then you will need to call the view without the /ssh.

For example, if you would like to grab the current MAC addresses from a device and update the database you would call:

/api/v1/devices/<int:id>/ssh/get_mac_table - This view is described in more detail below.

However if you would just like to obtain the current MAC addresses stored in the database because you have only just updated the database 5 seconds ago and want speed to query the database (avoiding the time it takes to SSH to the device and update the database), then you can use:

/api/v1/devices/<int:id>/get_mac_table

---

#### /api/v1/devices/<int:id>/ssh/get_mac_table
[GET] - Establishes an SSH session with the device, checks the MAC address and manages the MacEntry database table as intended.

Any MAC addresses that exist in the database but are not found on the device will be removed from the device.

Any new MAC addresses will be added into the database.

Any existing MAC addresses will be updated if required (eg. found on a different VLAN/Port)

```json
{
    "data": [
        {
            "address": "000b.82f0.d3c6",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 21,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "0c8b.fd9a.952a",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 22,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "309c.2309.9146",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 23,
            "port": "Gi1/0/20",
            "vlan": "224"
        },
        {
            "address": "400d.10e4.10f0",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 24,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "4c8d.79ee.45ba",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 25,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "7054.b454.486f",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 26,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "be98.bd8f.71a0",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 28,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "e8d8.195d.fd2b",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 29,
            "port": "Gi1/0/11",
            "vlan": "224"
        },
        {
            "address": "e8f2.e2a4.7c71",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 30,
            "port": "Gi1/0/11",
            "vlan": "224"
        }
    ],
    "error": false
}
```

#### /api/v1/devices/<int:id>/ssh/macs_by_port
[POST] - Returns all MAC addresses on a port for a given device in JSON format.
Eg. Sending {"port": "Gi1/0/20"} in the HTTP POST body will result in the below:
```json
{
    "data": [
        {
            "address": "309c.2309.9146",
            "address_type": "DYNAMIC",
            "device_id": 1,
            "id": 23,
            "port": "Gi1/0/20",
            "vlan": 224
        }
    ],
    "error": false
}
```
