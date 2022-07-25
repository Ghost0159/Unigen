import json, glob, os, re, time
from textwrap import indent
from igdb.wrapper import IGDBWrapper
from dotenv import load_dotenv
from datetime import date

def write_empty_file(file_name):
    with open(file_name, 'w') as f:
        f.write('{"storeContent": []}')

def is_empty(file_name):
    with open(file_name, 'r') as f:
        return f.read() == ''

if is_empty('.unistore.json'):
    write_empty_file('.unistore.json')
    empty = True
else:
    empty = False


with open('.unistore.json') as f:
    data = json.load(f)   

if empty == True:
    data["storeContent"] = [] 

gamedir = input('Game directory: ')
domain = input('Domain name (without http://): ')
storeinfo = input('Do you want to create/update the store informations? (y/n) : ')


if storeinfo == 'y':
    storetitle = input('Store title: ')
    storeauthor = input('Store author: ')
    storedescription = input('Store description: ')
    storeurl = input('Store url: ')
    storefile = input('Store file: ')
    storesheetURL = input('Store sheet url: ')
    storesheet = input('Store sheet: ')
    storebg_index = input('Store background index: ')
    storebg_sheet = input('Store background sheet: ')
    revision = input('Store revision(s): ')
    version = input('Store version: ')

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

ciagames_path = glob.glob(gamedir + '/*.cia')
ciagames_names_with_cia = [os.path.basename(x) for x in ciagames_path]
ciagames_names = [x[:-4] for x in ciagames_names_with_cia]
ciagames = []
for game in ciagames_names:
    game = re.sub(r"\([^()]*\)", "", game)
    ciagames.append(game)

#use igdb api to get game info


load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
IGDB_API_TOKEN = os.getenv('IGDB_API_TOKEN')
wrapper = IGDBWrapper(CLIENT_ID, IGDB_API_TOKEN)

n = -1
for game in ciagames:
    n = n + 1
    try:
        byte_array = wrapper.api_request(
            'games',
            'fields *; search "' + game + '"; limit 1;',
        )
        game_response=json.loads(byte_array)

        for gameinfo in game_response:
            title = gameinfo['name']
            try : 
                authors = gameinfo['involved_companies']
                authors = authors[0]
                time.sleep(0.5)
                byte_array2 = wrapper.api_request(
                    'companies',
                    f'fields name; where id = {str(authors)}; limit 1;',
                )
                author_response=json.loads(byte_array2)
                authors = author_response[0]['name']
            except:
                authors = 'Unknown'
                print('No author found for ' + game)
            description = gameinfo['summary']
            category = "games"
            console = "3DS"
            icon_index = "A FAIRE"
            sheet_index = "A FAIRE"
            last_updated = date.today().strftime("%m-%d-%Y")
            license = "Proprietary"
            if 'Europe' in ciagames_names_with_cia[n]:
                version = "Europe"
            elif 'America' or 'USA' in ciagames_names_with_cia[n]:
                version = "America"
            elif 'Japan' in ciagames_names_with_cia[n]:
                version = "Japan"
            elif 'Australia' in ciagames_names_with_cia[n]:
                version = "Australia"
            else:
                version = "Unknown"
            filename = ciagames_names_with_cia[n]
            size = (os.path.getsize(f"{gamedir}/{filename}"))
            size = str(size/ 1024 / 1024) + " MiB"
            fileurl = f"http://{domain}/{filename}"
            message1 = f'Downloading {filename}...'
            output = f'sdmc:/{filename}'
            type1 = 'downloadFile'

            filepath = f'/{filename}'
            message2 = f'Installing {filename}...'
            type2 = 'installCia'

            message3 = f'Deleting {filename}...'
            type3 = 'deleteFile'
            print(f'The game {title} was found in the database')
            with open('.unistore.json') as f:
                data = json.load(f)

            storeContent = {
                "info": {
                    "title": title,
                    "author": authors,
                    "description": description,
                    "category": f"[{category}]",
                    "console": f"[{console}]",
                    "icon_index": icon_index,
                    "sheet_index": sheet_index,
                    "last_updated": last_updated,
                    "license": license,
                    "version": version},
                f"Download {filename} ({size})": [
                    {
                        "file": fileurl,
                        "message": message1,
                        "output": output,
                        "type": type1
                    },
                    {
                        "file": filepath,
                        "message": message2,
                        "type": type2
                    },
                    {
                        "file": output, 
                        "message": message3, 
                        "type": type3
                    }
                ]
            }
            with open('.unistore.json', 'w') as f:
                data["storeContent"].append(storeContent)
                json.dump(data,  f, indent=4)
            time.sleep(0.5) #prevent rate limiting


    except Exception as e: 
        print(e) 
        print(f'{game} not found')
        continue