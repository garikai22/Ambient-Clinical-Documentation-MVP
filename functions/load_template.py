import json

def load_template(template_name, config_path):
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        
        if template_name in config_data["templates"]:
            return config_data["prompt"], config_data["templates"][template_name]
        else:
            raise ValueError(f"template '{template_name}' not found in config file.")
    except Exception as e:
        print(f"An error occurred while loading template: {str(e)}")