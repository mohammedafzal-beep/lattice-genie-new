import json
import datetime
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def load_data():
    return {
        "pages": ["Home", "Bravais", "Inverse Bravais", "Sheet TPMS", "Skeletal TPMS", "Strut-based"],
        "descriptions": load_json("desc_dict.json"),
        "crystal_images": load_json("crystal_images.json"),
        "subtypes_info": load_json("subtype_info.json"),
        "params_dict": {int(k): v for k, v in load_json("param_Dict.json").items()},
        "dict_key_map": {int(k): v for k, v in load_json("dict_key_map.json").items()},
        "system_prompt": open("instruction.txt").read()
    }

LOG_FILE = ".logs/chat_history.jsonl"
ALL_LOGS = ".logs/all_logs.jsonl"
def log_message(role, content):
    """Append a chat message to a JSONL log file with timestamp."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "role": role,
        "content": content
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    with open(ALL_LOGS, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

BUTTON_HISTORY_FILE = '.logs/button_history.jsonl'
def log_event(button_name,mode):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "button_name": button_name,
        "mode": mode
    }
    with open(BUTTON_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    with open(ALL_LOGS, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

LOG_SLIDER_CHANGES =  '.logs/log_slider_changes.jsonl'
def log_slider_changes(param_dict,mode):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "param_dict": param_dict,
        "mode": mode
    }

    # Ensure log file exists
    os.makedirs(os.path.dirname(LOG_SLIDER_CHANGES), exist_ok=True)
    if not os.path.exists(LOG_SLIDER_CHANGES):
        open(LOG_SLIDER_CHANGES, 'w', encoding='utf-8').close()

    # Read existing entries
    existing_entries = []
    with open(LOG_SLIDER_CHANGES, "r", encoding="utf-8") as f:
        for line in f:
            try:
                existing_entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    # Check if the same param_dict already exists
    existing_param_dicts = [entry["param_dict"] for entry in existing_entries]
    if param_dict not in existing_param_dicts:
        # Append to log files
        for file_path in [LOG_SLIDER_CHANGES, BUTTON_HISTORY_FILE, ALL_LOGS]:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")