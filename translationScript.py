import re
import json
from bs4 import BeautifulSoup
import os
import pathlib
import glob

# TODO CHANGE THIS TO FALSE IF YOU DON'T WANT TO ADD THE IMPORTS TO COMPONENTS.TS FILE
add_comp = True

# TODO CHANGE THIS TO JSON TRANSLATION FILE PATH
json_dir = r'Directory'
# Get the parent directory of json_dir
parent_dir = os.path.dirname(json_dir)

# Search for files in the parent directory containing the word "general"
general_file = glob.glob(os.path.join(parent_dir, '*general*.json'))

# Check if a file is found
if general_file:
    general_file_dir = general_file[0]  # Get the first match

# Get current directory that the Python file is running in
script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = script_dir.replace('\\', '/')
root_dir = script_dir
html_files = []
json_files = []
all_missing_translations = []
missing_translation = []

# Regex to identify span and label in HTML
pattern = r'(<(span|label|ion-title)[^>]*>)(.*?)(<\/\2>)'
# pattern = r'(<(span|label)[^>]*>)([\s\S]*?)(<\/\2>)'
# Regex to text which has {{}} and text outside. IE: 'test {{hi}} test'
pattern_with_text = re.compile(r'\{\{.*?\}\}')
# Regex to text which has {{}} and no text outside. IE: '{{hi}}'
pattern_no_additional_text = re.compile(r'^\{\{.*?\}\}$')
# Regex to text which has {} and text outside. IE: 'test {hi} test'
single_pattern_with_text = re.compile(r'\{.*?\}')
# Traverse the directory tree and fetch all HTML files
for dirpath, dirnames, filenames in os.walk(root_dir):
    for file_name in filenames:
        if file_name.endswith('.html') or file_name.endswith('component.ts'):
            # Add the full file path to the list
            file_name = (os.path.join(dirpath, file_name)).replace('\\', '/')
            html_files.append(os.path.join(dirpath, file_name))
            
"""
 Function used to handle cases where there is variables between text in HTML
 Input: "You have {{num}} of {{var}}"
 Output 1: "You have {{0}} of {{1}}"
 Output 2: ['num','var']
"""
def replace_with_indices(input_string):
    # Find all occurrences of text within double curly brackets
    pattern = re.compile(r'\{\{(.*?)\}\}')
    
    # Extract all matches to a list
    matches = pattern.findall(input_string)
    
    # Create a list from matches to maintain order
    match_list = matches.copy()
    
    # Replace each match in the string with its index
    index = 0
    def replace_match(match):
        nonlocal index
        result = f"{{{index}}}"  # Replace with current index
        index += 1
        return result

    # Use sub with a callback function to replace text
    replaced_string = pattern.sub(replace_match, input_string)
    
    # Return the modified string and the list of original placeholders
    return replaced_string, match_list
"""
Function to replace the text inside the tags

"""
def replace_text(match):
    bad_string = False
    full_tag = match.group(0)  # Full tag with attributes and content
    # Use BeautifulSoup to extract the content within the tag
    soup = BeautifulSoup(full_tag, 'html.parser')
    tag = soup.find(['span', 'label','ion-title'])
    try:
        before, match, after = full_tag.partition(tag.string)
    except Exception as e:
        try:

            outer_text = re.search(r'<span[^>]*>([^<]*)<', full_tag)
            before, match, after = full_tag.partition(outer_text.group(1).strip())
            bad_string = False
        except Exception as e:
            missing_translation.append(full_tag)
            unprocessed_content = full_tag
            content = "bad string"
            bad_string = True
    if not bad_string:
        opening_tag = before.strip()  # Capture the opening tag with attributes
        content = match.strip().replace("\n", " ").replace("\r", " ").replace('"', '\"')     # Capture the content inside the tag
        content  = " ".join(content.split())
        content = content.strip()
        # print(content)
        closing_tag = after.strip()  # Capture the closing tag
        unprocessed_content = content[:]
        if pattern_with_text.search(unprocessed_content) and not pattern_no_additional_text.match(unprocessed_content):
            content, extracted_list = replace_with_indices(unprocessed_content)

    if content not in en_to_identity:
        # if not pattern_with_text.search(content): 
        if "proppyTranslate" not in (content): 
        # print(content)
            missing_translation.append((str(unprocessed_content).replace('\n',"")).strip())
        return f'{full_tag}'  # Return the original tag with its content unchanged
    else:
        if pattern_no_additional_text.match(content):
            res = content
        elif single_pattern_with_text.search(content) and not pattern_no_additional_text.match(content):
            res = "{{"+str(json_file).replace("-","_")+'_json | proppyTranslate : '+"'" +str(en_to_identity[content])+"' : "+str(extracted_list) +"}} " 
        else :
            res = "{{"+str(json_file).replace("-","_")+'_json | proppyTranslate : '+"'" +str(en_to_identity[content])+"'}}"
        return f'{opening_tag}{res}{closing_tag}'

p = pathlib.PureWindowsPath(json_dir)

json_dir = str(p.as_posix())
json_dir = json_dir

for dirpath, dirnames, filenames in os.walk(json_dir):
    for file_name in filenames:
        if file_name.endswith('.json'):
            # Add the full file path to the list
            file_name = (os.path.join(dirpath, file_name)).replace('\\', '/')
            json_files.append(os.path.join(dirpath, file_name))

# Modify file B by inserting the new import at the top and code block after class declaration
def update_component_file(file_path, relative_paths, json_filenames, code_to_insert):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Insert the import statement at the top of the file
    for i in range(len(relative_paths)):
        import_statement = f'import * as {json_filenames[i]} from "{relative_paths[i]}";\n'
        lines.insert(i, import_statement)

    # Find the line that starts with 'export class FacilitiesComponent implements OnInit {'
    for i, line in enumerate(lines):
        if 'export class' in line:
            lines.insert(i + 1, code_to_insert)  # Insert the code block after the class declaration
            break
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)       
dictionary = {}
json_file = os.path.splitext(os.path.basename(json_dir))[0].split('.')[0]
for html_file_path in html_files:
    if "component.ts" in html_file_path:
        json_path = os.path.relpath(json_dir, os.path.dirname(html_file_path))
        general_path = os.path.relpath(general_file_dir, os.path.dirname(html_file_path))

        json_path = json_path.replace("\\", "/")  # Convert to Unix-style path for TypeScript
        general_path = general_path.replace("\\", "/")  # Convert to Unix-style path for TypeScript
        relative_paths = [json_path,general_path]

        # Extract JSON filename and replace hyphens with underscores
        json_filename = os.path.basename(json_path).replace('-', '_').replace('.json', '').replace('component','')
        general_json_filename = "general_json"
        json_filenames = [json_filename,general_json_filename]
        code_block = f'''
//Dictionary mapping all english translations to their keys
  general_json = JSON.parse(JSON.stringify(general_json))
  {json_filename}_json = JSON.parse(JSON.stringify({json_filename}))
//  translationMap = Object.keys(this.{json_filename}_json).reduce((map, key) => {{
//    const item = this.{json_filename}_json[key];
//    map[item.en] = item.identity;
//    return map;
//    }}, {{}} as any);
        '''
        if add_comp:
            update_component_file(html_file_path, relative_paths, json_filenames, code_block)
    else:
        missing_translation = []
        with open(json_dir, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        if len(missing_translation) == 0:
            path = str(os.path.splitext(html_file_path)[0])
            parts = path.replace('\\', '/').split('/')
            # Get the last num_parts components
            last_parts = parts[-4:]
            # Join the last components back into a path
            pathText = '/'.join(last_parts)
            missing_translation.append(pathText)
        # Example HTML (you would read this from a file)
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()


        en_to_identity = {v['en'].strip(): k for k, v in translations.items()}
        modified_html = re.sub(pattern, replace_text, html_content, flags=re.DOTALL)
        first_element = missing_translation[0]
        rest_of_list = missing_translation[1:]

        # Sort the rest of the list
        rest_of_list_sorted = sorted(rest_of_list)

        # Combine the first element with the sorted rest
        sorted_missing_translations = [first_element] + rest_of_list_sorted
        all_missing_translations.append(sorted_missing_translations)
        # Generate the output file path based on the HTML file path
        output_file_path = os.path.splitext(html_file_path)[0] + '_modified.html'
        # Write the modified HTML to the new file
        # TODO Change html_file_path to output_file_path if you do not want to directly replace the file
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(modified_html)
    

# Using dictionary keys to filter unique strings
# unique_strings = list(dict.fromkeys(missing_translation))
output_file_path = os.path.splitext(script_dir)[0] + '/missing_translation.txt'
with open(output_file_path, 'w') as file:
    for sublist in all_missing_translations:
        for item in sublist:
            file.write(f"{item}\n")
        file.write("\n")  
        
