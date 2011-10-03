# lexiconator

## Introduction

Lexiconator is a very simple learning aid to help improve your vocabulary, much like flash cards, primarily intended for use by candidates preparing for various tests that emphasize a large vocabulary, like the GRE. It lets you rate words as you encounter them. Using these ratings, you can filter for words based on a rating range, thus letting you revise only those words that you found intimidating. (This app was inspired by the ordeals that I saw my younger brother experience as I was helping him prepare for the vocabulary section of the GRE.)

## Requirements

Written in Python, it has a console based GUI (based on curses) and hence will run "as is" on most Posix systems with Python (version >= 2.6) installed. Will work on Windows with Cygwin (not tested). As such, its only requirements are the aforementioned Python interpreter.

Lexiconator will lookup word definitions from the Wiktionary database when it is online. In offline mode, it looks up word definitions from the offline Wordnet database packaged with the client. Note that in offline mode, no usage examples are be available since the WordNet database does not provide any.

## Installation Procedure

There isn't any. To run the client, just navigate to the **lexiconator-client** directory in your terminal and run:

`
./lexiconator
`

NOTE: You may have to give exec permissions when running the lexiconator shell script for the first time. In most *nix like systems you can do this with:

`
chmod 777 lexiconator
`

## Screen Shots:

![Apologies to aardvarks for the strong language used here](http://www.balajeerc.info/lexiconator-scrn.png)


