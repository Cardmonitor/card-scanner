import csv
import os.path
import timeit
import urllib2


def download(filename, url):

    print filename + ': ' + url
    response = urllib2.urlopen(url)
    data = response.read()

    # Write data to file
    path = 'cardmarket_images/' + filename

    if os.path.isfile(path):
        print('Datei ' + filename + ' schon vorhanden')
        return 0

    file_ = open(path, 'w')
    file_.write(data)
    file_.close()
    print('Datei ' + filename + ' heruntergeladen')
    return 1

downloads = 0
start = timeit.default_timer()
with open('import/singles.csv') as csvfile:
    cards = csv.reader(csvfile, delimiter=';')
    i = 0
    for row in cards:
        name = row[0]
        url = row[1]
        if (i == 0):
            i += 1
            continue

        downloads += download(name, url)
        i += 1
        break

print('Anzahl Downloads: ' + str(downloads))
stop = timeit.default_timer()
print 'Dauer: ' + str(round((stop - start), 2)) + ' Sekunden'

# print(json.dumps(cards[0], indent=4, sort_keys=True))
# print set_filename(cards[0])
#download(cards[0])

# downloads = 0
# for card in cards:
#     downloads += download(card)
#     # if (downloads > 10):
#     #     break;
# print('Anzahl Downloads: ' + downloads)
# stop = timeit.default_timer()
# print 'Dauer: ' + str(round((stop - start), 2)) + ' Sekunden'