import os
import string
import errno

src_dir = "original"
for filename in os.listdir(src_dir):
    if os.path.isdir(filename):
        continue
    parts = filename.split('-')
    if (len(parts) < 2):
        continue
    directory = os.path.join(src_dir, parts[0])
    if not os.path.exists(directory):
        #print 'make dir'
        os.makedirs(directory)

    #print os.path.join(src_dir, filename), os.path.join(directory, filename)
    #new_file_name = ''.join(c for c in file_name if c in string.printable)
    try:
        os.rename(os.path.join(src_dir, filename), os.path.join(directory, filename))
    except OSError:
        print os.path.join(src_dir, filename), os.path.join(directory, filename)
        break