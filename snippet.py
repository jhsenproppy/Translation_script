import json
import os

def convert_to_snippet_format(input_json):
    snippet_json = {}

    for key, value in input_json.items():
        identity = value.get("identity")
        en_translation = value.get("en")

        # First format (with `this.translateService.translate`)
        snippet_json[en_translation] = {
            "scope": "javascript,typescript,html",
            "prefix": str(identity) + 'j',
            "body": [
                f"this.translateService.translate('{identity}', this.general_json)"
            ],
            "description": en_translation
        }

        # Second format (with `proppyTranslate`)
        snippet_json[en_translation + ".h"] = {
            "scope": "javascript,typescript,html",
            "prefix": str(identity) + 'h',
            "body": [
                f"{{{{general_json | proppyTranslate : '{identity}'}}}}"
            ],
            "description": en_translation
        }

    return snippet_json

# Read JSON file
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Write snippet JSON to a file in the current directory
def write_snippet_json(snippet_data, output_file_name):
    with open(output_file_name, 'w', encoding='utf-8') as file:
        json.dump(snippet_data, file, indent=4)

# Example usage
input_file = 'input_data.json'  # Path to your input JSON file
output_file = 'snippet_data.json'  # Output file name in the current directory

# TODO change this. Read input data
input_data = read_json_file(r"JSON FILE")

# Convert input data to snippet format
snippet_data = convert_to_snippet_format(input_data)

# Save the result in the current directory
write_snippet_json(snippet_data, output_file)
