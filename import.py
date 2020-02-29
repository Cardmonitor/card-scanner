from slugify import slugify

import json
import os.path
import string
import time
import timeit
import urllib2

def set_filename(card):
    #  Nur ASCII siehe rename_originals.py
    filename = card['set'] + '-' + card['collector_number'] + '-' + card['lang'] + '-' + slugify(card['name']) + '.jpg'
    return ''.join(c for c in filename if c in string.printable)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download(card):

    global i
    directory = os.path.join('original', card['set'])
    filename = set_filename(card)

    if 'image_uris' not in card:
        print(str(i) + ': Datei ' + filename + ' nicht vorhanden')
        return 0

    if 'large' not in card['image_uris']:
        print(str(i) + ': Datei ' + filename + ' nicht vorhanden')
        return 0

    response = urllib2.urlopen(card['image_uris']['large'])
    data = response.read()

    # Write data to file
    create_directory(directory)
    path = os.path.join(directory, filename)


    if os.path.isfile(path):
        print(str(i) + ': Datei ' + filename + ' schon vorhanden')
        return 0

    file_ = open(path, 'w')
    file_.write(data)
    file_.close()
    print(str(i) + ': Datei ' + filename + ' heruntergeladen')
    time.sleep(.100)
    return 1

i = 46507
start = timeit.default_timer()
with open('import/scryfall-default-cards.json') as f:
    cards = json.load(f)

# print(json.dumps(cards[0], indent=4, sort_keys=True))
# print set_filename(cards[0])
# download(cards[0])

downloads = 0
for card in cards[i:]:
    downloads += download(card)
    i += 1
    # if (downloads > 10):
    #     break;
print('Anzahl Downloads: ' + str(downloads))
stop = timeit.default_timer()
print 'Dauer: ' + str(round((stop - start), 2)) + ' Sekunden'