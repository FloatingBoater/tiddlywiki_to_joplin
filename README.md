# tiddlywiki_to_joplin
Script to convert a TiddlyWiki note export CSV file into a Joplin JEX file for import.

[GitHub Repository](https://github.com/FloatingBoater/tiddlywiki_to_joplin/)

## Args
    No external args, only internal constant definitions

## Parameters
    InputFile (str): Constant string filename of the CSV export from a TiddlyWiki

    OutputDir (str): Constant string directory name created to hold exported MD files.

    YourName  (str): default name used where 'creator' is not set.

## Usage
* Open your existing TiddlyWiki notebook in a browser as usual.
* Use the 'Export all tiddlers' function (icon upward arrow) to create a CSV file.
* Edit the filename parameters below.
* Run this script.
* Check the directory of individual *.md files, each containing one tiddler / Markdiwn formatted note.

* After checking the *.md files, create a tar file of the note files - which is what a JEX file consists of:
  ```
  $ cd tiddlywiki_notes
  $ tar cvf tiddlywiki_export.jex *.md
  ```
* You can them import the file 'joplin_conversion.jex' into Joplin.
"""
