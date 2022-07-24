import json

def write_empty_file(file_name):
    with open(file_name, 'w') as f:
        f.write('{}')

def is_empty(file_name):
    with open(file_name, 'r') as f:
        return f.read() == ''

if is_empty('.unistore.json'):
    write_empty_file('.unistore.json')

with open('.unistore.json') as f:
    data = json.load(f)

data["storeContent"] = []

title = 'Example Title'
author = 'Example Author'
description = 'Example Description'
category = 'Example Category'
console = 'Example Console'
icon_index = 'Example Icon Index'
sheet_index = 'Example Sheet Index'
last_updated = 'Example Last Updated'
license = 'Example License'
version = 'Example Version'


filename = 'Example-filename.cia'
size = '1 MiB'
fileurl = f'https://example.com/{filename}'
message1 = f'Downloading {filename}...'
output = f'sdmc:/{filename}'
type1 = 'downloadFile'

filepath = f'/{filename}'
message2 = f'Installing {filename}...'
type2 = 'installCia'

message3 = f'Deleting {filename}...'
type3 = 'deleteFile'

storeContent = {"info": {"title": title, "author": author, "description": description, "category": f"[{category}]", "console": f"[{console}]", "icon_index": icon_index, "sheet_index": sheet_index, "last_updated": last_updated, "license": license, "version": version}, f"Download {filename} ({size})": [{"file": fileurl, "message": message1, "output": output, "type": type1}, {"file": filepath,"message": message2, "type": type2}, {"file": output, "message": message3, "type": type3}]}

storetitle = "Example Title"
storeauthor = "Example Author"
storedescription = "Example Description"
storeurl = "https://example.com"
storefile = "Example-filename.unistore"
storesheetURL = "https://example.com/Example-filename.t3x"
storesheet = "Example-filename.t3x"
storebg_index = "1"
storebg_sheet = "0"
revision = "1"
version = "1.0.0"

data["storeInfo"] = {
    "title": storetitle,
    "author": storeauthor,
    "description": storedescription,
    "url": storeurl,
    "file": storefile,
    "sheetURL": storesheetURL,
    "sheet": storesheet,
    "bg_index": storebg_index,
    "bg_sheet": storebg_sheet,
    "revision": revision,
    "version": version
}

with open('.unistore.json', 'w') as f:
    data["storeContent"].append(storeContent)
    json.dump(data,  f, indent=4)