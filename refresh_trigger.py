import json
import os
import time
from typing import Dict, List, Any, Optional

# Constants
REFRESH_TRIGGER_FILE = "refresh_trigger.json"

def init_refresh_file():
    """Initialize the refresh trigger file if it doesn't exist"""
    if not os.path.exists(REFRESH_TRIGGER_FILE):
        with open(REFRESH_TRIGGER_FILE, 'w') as f:
            json.dump({
                "last_refresh": int(time.time() * 1000),
                "last_saved_state": None,
                "last_saved_preset": None,
                "states": [],
                "presets": []
            }, f)

def get_refresh_data():
    """Load data from the refresh trigger file"""
    init_refresh_file()
    try:
        with open(REFRESH_TRIGGER_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading refresh trigger data: {e}")
        return {
            "last_refresh": int(time.time() * 1000),
            "last_saved_state": None,
            "last_saved_preset": None,
            "states": [],
            "presets": []
        }

def update_refresh_data(data):
    """Save data to the refresh trigger file"""
    try:
        with open(REFRESH_TRIGGER_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving refresh trigger data: {e}")

def trigger_refresh():
    """Update the last_refresh timestamp in the refresh trigger file"""
    data = get_refresh_data()
    data["last_refresh"] = int(time.time() * 1000)
    update_refresh_data(data)
    return data["last_refresh"]

def record_saved_state(name, icon_params, r_target, g_target, b_target):
    """Record a saved state in the refresh trigger file"""
    data = get_refresh_data()
    
    # Update last saved state
    data["last_saved_state"] = {
        'name': name,
        'icon_params': icon_params,
        'target': {'r': r_target, 'g': g_target, 'b': b_target}
    }
    
    # Update states list, maintaining uniqueness by name
    state_exists = False
    for i, state in enumerate(data["states"]):
        if state["name"] == name:
            data["states"][i] = data["last_saved_state"]
            state_exists = True
            break
    
    if not state_exists:
        data["states"].append(data["last_saved_state"])
    
    # Update refresh timestamp
    data["last_refresh"] = int(time.time() * 1000)
    
    # Save updated data
    update_refresh_data(data)
    
    return data["last_refresh"]

def record_saved_preset(name, params):
    """Record a saved preset in the refresh trigger file"""
    data = get_refresh_data()
    
    # Update last saved preset
    data["last_saved_preset"] = {
        'name': name,
        'params': params
    }
    
    # Update presets list, maintaining uniqueness by name
    preset_exists = False
    for i, preset in enumerate(data["presets"]):
        if preset["name"] == name:
            data["presets"][i] = data["last_saved_preset"]
            preset_exists = True
            break
    
    if not preset_exists:
        data["presets"].append(data["last_saved_preset"])
    
    # Update refresh timestamp
    data["last_refresh"] = int(time.time() * 1000)
    
    # Save updated data
    update_refresh_data(data)
    
    return data["last_refresh"]

def get_saved_states():
    """Get all saved states from the refresh trigger file"""
    data = get_refresh_data()
    return data["states"]

def get_saved_presets():
    """Get all saved presets from the refresh trigger file"""
    data = get_refresh_data()
    return data["presets"]

def delete_saved_state(name):
    """Delete a saved state from the refresh trigger file"""
    data = get_refresh_data()
    
    # Remove from states list
    data["states"] = [state for state in data["states"] if state["name"] != name]
    
    # If it was the last saved state, clear it
    if data["last_saved_state"] and data["last_saved_state"]["name"] == name:
        data["last_saved_state"] = None
    
    # Update refresh timestamp
    data["last_refresh"] = int(time.time() * 1000)
    
    # Save updated data
    update_refresh_data(data)
    
    return data["last_refresh"]

def delete_saved_preset(name):
    """Delete a saved preset from the refresh trigger file"""
    data = get_refresh_data()
    
    # Remove from presets list
    data["presets"] = [preset for preset in data["presets"] if preset["name"] != name]
    
    # If it was the last saved preset, clear it
    if data["last_saved_preset"] and data["last_saved_preset"]["name"] == name:
        data["last_saved_preset"] = None
    
    # Update refresh timestamp
    data["last_refresh"] = int(time.time() * 1000)
    
    # Save updated data
    update_refresh_data(data)
    
    return data["last_refresh"]