#!/usr/bin/python3
""" tiddlywiki_to_joplin.py 

James Derrick

https://github.com/FloatingBoater/tiddlywiki_to_joplin/blob/master/README.md
Mon  1 Apr 18:42:31 BST 2019

Script to convert from a CSV file exported from a TiddlyWiki notebook to Joplin notes

Args:
    No external args, only internal constant definitions

Parameters:
InputFile (str): Constant string filename of the CSV export from a TiddlyWiki

OutputDir (str): Constant string directory name created to hold exported MD files.

YourName  (str): default name used where 'creator' is not set.

Usage:
Open your existing TiddlyWiki notebook in a browser as usual.
Use the 'Export all tiddlers' function (icon upward arrow) to create a CSV file.
Edit the filename parameters below.
Run this script.
Check the directory of individual *.md files, each containing one tiddler / Markdiwn formatted note.

After checking the *.md files, create a tar file of the note files - which is what a JEX file consists of:
  $ cd tiddlywiki_notes
  $ tar cvf tiddlywiki_export.jex *.md
You can them import the file 'joplin_conversion.jex' into Joplin.
"""

import datetime
import csv
import uuid
import os
import re        # needed to regexp basic format conversions


###
### change these values
###
#InputFile = 'tiddlers.csv'
InputFile = '2019-04-01 1_tech_spellbook tiddlywiki export tiddlers.csv'
OutputDir = 'tiddlywiki_notes'
YourName  = 'James Derrick'


def tiddler_to_markdown( text ):
    """ tiddler_to_markdown( str )
    Very basic conversion from TiddlyWiki formatting to Markdown
    No attempt is made to be complete, just fix the basics like headings.

    Args:
        text (str): String in TiddlyWiki format

    Returns:
        text (str): String in Markdown format
    """
    # Heading conversions
    # Markdown uses a different heading character, and needs a space.
    # As headings are anchored to the start of a line, the regexp is relatively safe.
    #
    # %s/^!!!!/#### /
    # %s/^!!!/### /
    # %s/^!!/## /
    # %s/^!/# /
    text = re.sub('^\!\!\!\!', '#### ', text, 0, re.M)
    text = re.sub('^\!\!\!',   '### ' , text, 0, re.M)
    text = re.sub('^\!\!',     '## '  , text, 0, re.M)
    text = re.sub('^\!',       '# '   , text, 0, re.M)

    # Table formmatting is rather different, with Markdown requiring a table header row
    # after the header '---|---'
    #
    # This is rather hard to do automagically, expecially as `|` and `!` are 
    # heavily used in scripts and code fragments.

    # URLs
    # Links between tiddlers are too hard, as double square brackets are also used in some logfiles:
    # [[OpenHABian Backup]]
    #
    # External links are converted using non-greedy matching with two groups for text and URL
    # TiddlyWiki: `[ext[LinkText|https://example.org/]]`
    # Joplin:     `[LinkText](http://example.com)`
    text = re.sub('\[ext\[(.*?)\|(.*?)\]\]', '[\\1](\\2)', text, 0, re.M)

    return text


if not os.path.exists(InputFile):
    print("InputFile does not exist - check script filename <" + InputFile + ">.")
    quit(-1)

with open(InputFile) as csv_file:
    tiddlywiki = csv.DictReader(csv_file, delimiter=',')

    # Create a directory for tiddlers as Joplin notes
    if not os.path.exists(OutputDir):
        os.mkdir(OutputDir)
        print("Output directory ", OutputDir,  " created")
    else:    
        print("Output directory ", OutputDir,  " already exists")


    # Create a Notebook called TiddlyImport to contain imported tiddlers
    parent_id = uuid.uuid4().hex
    TiddlerFile = open(OutputDir + '/' + parent_id + '.md', 'x')

    TiddlerFile.write('TiddlyWiki Import' + '\n')
    TiddlerFile.write('\n')
    TiddlerFile.write('id: ' + parent_id + '\n')
    dt_created  = datetime.datetime.now()
    TiddlerFile.write('created_time: ' + dt_created.isoformat('T','milliseconds') + '\n')
    TiddlerFile.write('updated_time: ' + dt_created.isoformat('T','milliseconds') + '\n')
    TiddlerFile.write('user_created_time: ' + dt_created.isoformat('T','milliseconds') + '\n')
    TiddlerFile.write('user_updated_time: ' + dt_created.isoformat('T','milliseconds') + '\n')
    TiddlerFile.write('encryption_cipher_text: ' + '\n')
    TiddlerFile.write('encryption_applied: 0' + '\n')
    # blank parent_id as top-level notebook
    TiddlerFile.write('parent_id: ' + '\n')
    # no '\n' on the last line - causes Joplin import errors
    TiddlerFile.write('type_: 2')

    TiddlerFile.close()


    # step through the exported CSV file line by line
    line_count = 0
    for tiddler in tiddlywiki:
        note_id = uuid.uuid4().hex
        if line_count == 0:
            # f prefix = f-string, formatted string loteral PEP 498.
            print(f'Column names are:\t{", ".join(tiddler)}\n')
            print(f'parent_id:\t{parent_id}\n')
            line_count += 1
            continue

        if (tiddler['title'] == 'New Tiddler'):
            #default template tiddler - skip
            print ('DEBUG template - skip')
            continue

        if (tiddler['title'] == 'SiteTitle'):
            print ('DEBUG SiteTitle - skip')
            continue

        if (tiddler['title'] == 'SiteSubtitle'):
            print ('DEBUG SiteSubtitle - skip')
            continue

        if (len(tiddler['creator'])  == 0):
            tiddler['creator'] = YourName

        if (len(tiddler['modified'])  == 0):
            # An unmodified tiddler doesn't have all fields set, so use creation values
            #print ('DEBUG Unmodified - copy creation to modified')
            tiddler['modified'] = tiddler['created']
            tiddler['modifier'] = tiddler['creator']

        # convert text formats
            
        TiddlerFile = open(OutputDir + '/' + note_id + '.md', 'x')
        print('DEBUG ', tiddler['title'])

        TiddlerFile.write(tiddler['title'] + '\n')
        TiddlerFile.write('\n')
        TiddlerFile.write(tiddler_to_markdown(tiddler['text']) + '\n')
        TiddlerFile.write('\n')
        TiddlerFile.write('id: ' + note_id + '\n')
        TiddlerFile.write('parent_id: ' + parent_id + '\n')

        # Tiddly uses '20181231235900123'
        #              %Y  %m%d%H%M%S%f
        # Joplin uses '2017-12-07T12:56:17.000Z' which is basically ISO 8601 format with mS
        #              %Y  -%m-%d%H%M%S%f
        #              isoformat(timespec='milliseconds')
        #print('DEBUG created: <', tiddler['created'], '>')
        dt_created  = datetime.datetime.strptime(tiddler['created'],  '%Y%m%d%H%M%S%f')
        TiddlerFile.write('created_time: ' + dt_created.isoformat( 'T','milliseconds') + '\n')
        dt_modified = datetime.datetime.strptime(tiddler['modified'], '%Y%m%d%H%M%S%f')
        TiddlerFile.write('updated_time: ' + dt_modified.isoformat('T','milliseconds') + '\n')

        TiddlerFile.write('is_conflict: 0' + '\n')
        TiddlerFile.write('latitude: 55.088' + '\n')
        TiddlerFile.write('longitude: -1.5863' + '\n')
        TiddlerFile.write('altitude: 0.0000' + '\n')
        TiddlerFile.write('author: ' + tiddler['creator'] + '\n')
        TiddlerFile.write('is_todo: 0' + '\n')
        TiddlerFile.write('todo_due: 0' + '\n')
        TiddlerFile.write(f'todo_completed: 0' + '\n')
        TiddlerFile.write('source: com.tiddlywiki' + '\n')
        TiddlerFile.write('source_application: org.jamesderrick.tiddly_to_joplin' + '\n')
        TiddlerFile.write('application_data: ' + '\n')
        TiddlerFile.write('order: 0' + '\n')
        TiddlerFile.write('user_created_time: ' + dt_created.isoformat('T', 'milliseconds') + '\n')
        TiddlerFile.write('user_updated_time: ' + dt_modified.isoformat('T', 'milliseconds') + '\n')
        TiddlerFile.write('encryption_cipher_text: ' + '\n')
        TiddlerFile.write('encryption_applied: 0' + '\n')
        # no '\n' on the last line - causes Joplin import errors
        TiddlerFile.write('type_: 1')

        TiddlerFile.close()
        line_count += 1

    print('===============')
    print(f'Processed {line_count} lines.')
    print(f'created a new Notebook with parent_id:\t{parent_id}\n')

