#!/usr/bin/python3

import os, shutil, random, sys, time
from PIL import Image
from PIL.ExifTags import TAGS

ALLOWED_EXTENSTIONS = set([".jpeg", ".jpg", ".jfif", ".png"])
#import pdb; pdb.set_trace()



def getAllFiles(dir, recursion = False, fullPath = True):
    #scan interals and get files
    files = []
    
    with os.scandir(dir) as it:
        for entry in it:
            if not entry.name.startswith('.'):
                if entry.is_file():
                    files.append(os.path.join(dir, entry.name) if fullPath else entry.name)
                if recursion and entry.is_dir():
                    files.extend(getAllFiles(os.path.join(dir, entry.name), recursion, fullPath))
    return files

def tagAll(files, dirTo, dirFrom):
    #import pdb; pdb.set_trace()
    stats = {}
    modded = set(getAllFiles(dirTo, False, False))
    amt = len(files)
    num = 0
    for filepath in files:
        num += 1
        name = os.path.basename(filepath)
        (tail, ext) = os.path.splitext(name)
        
        if ext not in ALLOWED_EXTENSTIONS:
            continue
            
        d = os.path.dirname(filepath)
        
        #nice ui
        print("Tagging: ", f'{(num):04}', "/", f'{(amt):04}', end = '\r')
        
        #create image object
        image = Image.open(filepath)
        exifdata = None
        
        teststring = tail + ".jpeg"
        if teststring in modded:
            with Image.open(os.path.join(dirTo, teststring)) as im:
                exifdata = im.getexif()
        else:
            exifdata = image.getexif()
            
        try:
            if (d != dirFrom):
                tag = d.split("/")
                tag = tag[len(tag) - 1]
                tag = tag.replace(" ", "_")
                stats[tag] = stats.get(tag, 0) + 1
            tags = exifdata.get(0x9286, "")
            if tag not in tags.split(" "):
                exifdata[0x9286] = (tags + " " if len(tags) > 0 else "") + tag
            if ext == ".png":
                rgb = image.convert("RGB")
                rgb.save(os.path.join(dirTo, tail + ".jpeg"), "JPEG", exif=exifdata)
            else:
                image.save(os.path.join(dirTo, tail + ".jpeg"), "JPEG", exif=exifdata)
            modded.add(tail + ".jpeg")
        except:
            sys.stdout.write("\033[K")
            print("failed something on file:", "\n" + name[:40] + (name[40:] and '..'), end = "\n")
        
        image.close()
    print("", end = "\n")
    print("sorted:")
    for key, value in stats.items():
        print(key, " - ", value)


def getTags(path):
    try:
        with Image.open(path) as im:
            return im.getexif().get(0x9286, "").split(" ")
    except:
        print("File not found")

def selectTags(dir, tags, recursion = False, fullPath = False):
    files = getAllFiles(dir, recursion, fullPath)
    if (tags == {''}):
        return files
    ans = []
    for p in files:
        with Image.open(p) as im:
            t = im.getexif().get(0x9286, "").split(" ")
            for i in t:
                if i in tags:
                    ans.append(p)
                    break
    return ans

def randomStuff(amt, files, dirTo, rename = True):
    cwd = os.getcwd()
    offset = 0

    for i in os.listdir(dirTo):
        try:
            n = int(os.path.splitext(i)[0])
            offset = max(offset, n)
        except:
            pass
            
    
    random.seed()
    p = 0
    for i in random.sample(files, min(amt, len(files))):  
        print("Copying: ", f'{(p + 1):04}', "/", f'{(amt):04}', end = '\r')
        basename = os.path.basename(i)
        (name, ext) = os.path.splitext(basename)
        if rename:
            shutil.copyfile(i, os.path.join(dirTo, f'{(p + offset + 1):04}' + ext))
        else:
            shutil.copyfile(i, os.path.join(dirTo, name + ext))
        p += 1
        
    print("Copying: done!", end = '')
    sys.stdout.write("\033[K\n")
    sys.stdout.flush()

def main():
    cwd = os.getcwd()
    dirFrom = ""
    dirTo = ""
    recursion = False
    command = ""
    amt = 1
    rename = True
    if len(sys.argv) > 1:
        skip = False
        command = sys.argv[1]
        for i in range(len(sys.argv)):
            if skip:
                skip = False
                continue
            if sys.argv[i] == "-norename":
                rename = False
            if sys.argv[i] == "-from" or sys.argv[i] == "-f":
                skip = True
                try:
                    dirFrom = sys.argv[i + 1]
                except:
                    pass
            elif sys.argv[i] == "-r":
                recursion = True
            elif sys.argv[i] == "-o" or sys.argv[i] == "-out":
                skip = True
                try:
                    dirTo = sys.argv[i + 1]
                except:
                    pass
                
            else:
                try:
                    amt = int(sys.argv[i])
                except:
                    pass
    else:
        print("usage: imageTagger.py <command> <-from <filename>> <-out <filename>> [-r] [amount]")
        print("available commands: edit, tag, generate")
        quit()
    
    if dirFrom == "": 
        print("please specify <-from <filename>> <-out <filename>>")
        quit()
    if dirTo == "":
        print("please specify <-from <filename>> <-out <filename>>")
        quit()
    
    if command == "" or command == "edit":
        filename = ""
        while True:
            filename = input("current directory:" + str(os.path.join(cwd, dirFrom)) + "\nEdit file ('q' to exit): ")
            if (filename == "q" or filename == "quit"):
                break;
            try:
                with Image.open(os.path.join(dirFrom, filename)) as im:
                    exifdata = im.getexif()
                    print("current tags:", exifdata.get(0x9286, ""))
                    tags = input("replace with tags: ")
                    exifdata[0x9286] = tags
                    im.save(os.path.join(dirFrom, filename), exif = exifdata)
            except:
                print("File not found")
            
    elif command == "tag":
        
        files = getAllFiles(dirFrom, recursion)
    
        print("Found", len(files), "files\nin:", dirFrom)
        print("They will replace or update files in:", dirTo)
        s = input("Are you sure? (y/n): ")
        if (s != 'y' and s != 'Y'):
            exit()
    
        tagAll(files, dirTo, dirFrom)
    
    elif command == "generate":
    
        tags = set(input("tags(empty for all): ").split(" "))
        print("chosen tags: ", tags)
        files = selectTags(dirFrom, tags, recursion, True)
        
        print("Found", len(files), "files that have one or more of specified tagsin:\n" + dirFrom)
        print(min(amt, len(files)), "of them chosen at random will be placed in:\n" + dirTo)
        s = input("Are you sure? (y/n): ")
        if (s != 'y' and s != 'Y'):
            exit()
        
        randomStuff(amt, files, dirTo, rename)
    elif command == "count":
        tags = set(input("tags(empty for all): ").split(" "))
        print("chosen tags: ", tags)
        files = selectTags(dirFrom, tags, recursion, True)
        print("found", len(files), "files")
    
    else:
        print("usage: imageTagger.py <command> <-from <filename>> <-out <filename>> [-r] [amount]")
        print("available commands: edit, tag, generate")
        
#import pdb; pdb.set_trace()
main()