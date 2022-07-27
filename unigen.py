import json, glob, os, re, time, math, sys
from sre_constants import CATEGORY_DIGIT
import shutil
from operator import iconcat
from textwrap import indent
from igdb.wrapper import IGDBWrapper
from dotenv import load_dotenv
from datetime import date
from subprocess import Popen, PIPE, run

cwd = os.getcwd()

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.6+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def write_empty_file(file_name):
    with open(file_name, 'w') as f:
        f.write('{"storeContent": []}')

def is_empty(file_name):
    with open(file_name, 'r') as f:
        return f.read() == ''

def find_id():
        with open('titles.txt', 'r', errors='replace') as f:
            gameid = f.readlines()[4]
            gameid = gameid.replace('|', '').replace(' ', '')
            gameid = gameid[1:]
            gameid = gameid[:9]
            gameid = gameid[:3] + gameid[5:]
            f.close()
        return gameid

def create_t3x(t3s_file_number):
    while True:
        try:
            command = f"tex3ds.exe -i t3s/unigen{t3s_file_number}.t3s -o t3x/{t3s_file_number}.t3x"
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            output = result.stderr
            try: 
                output = re.findall(r"'(.*?)'", output)[0].replace('/t3s', '')
            except:
                break
            if len(output) > 35:
                break
            print(f'The icon of the game with the id {output} was not found')
            with open(f"t3s/unigen{t3s_file_number}.t3s", 'r') as f:
                lines = f.readlines()
            with open(f"t3s/unigen{t3s_file_number}.t3s", 'w') as f:
                for line in lines:
                    if line.strip('\n') == 'data/UNIGENDEFAULT/icon.png\n':
                        pass
                    elif line.strip('\n') != output:
                        f.write(line)
                    else :
                        f.write('data/UNIGENDEFAULT/icon.png\n')
        except:
            break
    shutil.copyfile(f'{cwd}/t3x/unigen{t3s_file_number}.t3x', f'{cwd}/server/{t3s_file_number}.t3x')

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
error_count = 0
t3x_sheet = 0


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

os.system('cls' if os.name == 'nt' else 'clear')

ciagames_path = glob.glob(gamedir + '/*.cia')
ciagames_names_with_cia = [os.path.basename(x) for x in ciagames_path]

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
IGDB_API_TOKEN = os.getenv('IGDB_API_TOKEN')
wrapper = IGDBWrapper(CLIENT_ID, IGDB_API_TOKEN)

count = -1

for game_with_cia in progressbar(ciagames_names_with_cia, "Progress: ", 40):
    while True:
        try:
            game = re.sub(r"\([^()]*\)", "", game_with_cia[:-4])
            byte_array = wrapper.api_request(
                'games',
                'fields *; search "' + game + '"; limit 1;',
            )
            game_response=json.loads(byte_array)

            for gameinfo in game_response:
                try: 
                    title = gameinfo['name']
                except:
                    title = game_with_cia[:-4]
                
                try : 
                    authors = gameinfo['involved_companies']
                    authors = authors[0]
                    time.sleep(0.5) #preventing rate limiting
                    byte_array2 = wrapper.api_request(
                        'companies',
                        f'fields name; where id = {str(authors)}; limit 1;',
                    )
                    author_response=json.loads(byte_array2)
                    authors = author_response[0]['name']
                except:
                    authors = 'Unknown'

                try :
                    description = gameinfo['summary']
                except:
                    description = 'No description'

                if len(description.split()) > 20:
                    description = ' '.join(description.split()[:20]) + '...'
                category = "games"
                console = "3DS"
                last_updated = date.today().strftime("%d-%m-%Y")
                license = "Proprietary"
                if 'Europe' in game_with_cia:
                    version = "Europe"
                elif 'America' in game_with_cia:
                    version = "America"
                elif 'Japan' in game_with_cia:
                    version = "Japan"
                elif 'Australia' in game_with_cia:
                    version = "Australia"
                else:
                    version = "Unknown"
                filename = game_with_cia
                size = (os.path.getsize(f"{gamedir}/{filename}"))
                size = str(math.floor(size/ 1024 / 1024)) + " MiB"
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

                p = Popen(["TidGen.exe", f"{gamedir}/{filename}"], stdin=PIPE, shell=True)
                p.communicate(input=b'\n')
                
                gameid = find_id()

                print(f'The game {title} has the id {gameid}')

                #every time count hits a multiple of 419 add 1 to the value of sheet_index

                if count % 419 == 0 and count != 0:
                    create_t3x(t3x_sheet)
                    t3x_sheet += 1
                with open(f't3s/unigen{t3x_sheet}.t3s', 'a') as f:
                    count += 1
                    if is_empty(f't3s/unigen{t3x_sheet}.t3s'):
                        f.write(f'--atlas -f rgba -z auto\n\n')
                    f.write('t3s/data/' + gameid + '/icon.jpg\n')
                
                sheet_index = t3x_sheet

                icon_index = count

                with open(f'unigen.html', 'a') as f:
                    f.write(f'<a href="/games/{console}/{game_with_cia}" download>{game_with_cia}</a><br>\n')

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
            if error_count > 5:
                print(f'Error: {e}')
                break
            error_count += 1
            print(e) 
            print(f'{game} has encountered an error... Retrying...')
            continue
        break

time.sleep(0.3)

if count < 419:
    create_t3x(1)

shutil.copyfile(f'{cwd}/.unistore.json', f'{cwd}/server/.unistore')
shutil.copyfile(f'{cwd}/unigen.html', f'{cwd}/server/unigen.html')

print('Done')