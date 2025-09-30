import json
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
