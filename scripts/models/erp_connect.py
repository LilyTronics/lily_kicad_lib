"""
Model for connecting to the ERP system.
A JSON formatted file must be in the users folder with the URI, database name and credentials
Filename: erp_connect.json

{
    "url": "https://....",
    "database": "my_database",
    "username": "username",
    "password": "secret_password"
}

"""

import json
import os
import xmlrpc.client


_FIELDS = [
    "id",
    "name",
    "default_code"
]


def get_components_from_erp():
    print("Reading components from ERP database")
    json_filename = os.path.join(os.path.expanduser("~"), "erp_connect.json")
    if not os.path.isfile(json_filename):
        print("No configuration file present")
        return False, []

    try:
        config = json.load(open(json_filename, "r"))
    except Exception as e:
        print("Error reading configuration file")
        print(str(e))
        return False, []

    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(config["url"]))
        uid = common.authenticate(config["database"], config["username"], config["password"], {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(config["url"]))
        records = models.execute_kw(config["database"], uid, config["password"], 'product.template',
                                    'search_read', [[["categ_id", "=", "Electronic components"]]], {'fields': _FIELDS})
    except Exception as e:
        print("Error reading records")
        print(str(e))
        return False, []

    return True, records


if __name__ == "__main__":

    result = get_components_from_erp()
    if result[0]:
        for record in result[1]:
            print(record)
