# Put your persistent store models in this file

import os
import uuid
import json
from .app import Heda as app


def add_new_data(site_name, owner):
    """
    Persist new dam.
    """
    # Serialize data to json
    
    new_data_id = uuid.uuid4()
    data_dict = {
        'id': str(new_data_id),
        'name': site_name,
        'owner': owner,
        
    }

    
    data_json = json.dumps(data_dict)

    # Write to file in app_workspace/dams/{{uuid}}.json
    # Make dams dir if it doesn't exist
    app_workspace = app.get_app_workspace()
    data_dir = os.path.join(app_workspace.path, 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # Name of the file is its id
    file_name = str(new_data_id) + '.json'
    file_path = os.path.join(data_dir, file_name)

    # Write json
    with open(file_path, 'w') as f:
        f.write(data_json)

        
                
def fetch_data(site_name, event_id):
    """
    fetch data from hydroshare server
    """
    