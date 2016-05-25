watch_shows
===========

A poorly named set of python scripts which will eventually be condensed into a single main loop with a menu.
Any of these scripts simply automate the process of visiting a corresponding website and watching shows there.


Setup
=====

## Dependencies
python
mpv (apt-get or brew)
python lib: requests
python lib: beautifulSoup

At some point I'll include a little shell script to install all dependencies.

Use
===

1. python <script_for_website>.py SETUP
    You only need to do this now and then, this populates the .txt files you see on disk.

2. python anime_on_hand.py <show> <episode #>

3. python cartoononline.py <show> <season> <episode>

In addition, cartoon online script supposrt a season of "LIST" in which it lists the episodes of the season for the
value passed to episode.

python cartoononline.py <show> LIST <season #>

From there follow the prompts and easily watch anime from your command line, great for saving a bit of time and
just looking like a real fly guy.

## Notes

1. cartoononline.py is a bit more robust than anime_on_hand.py since it was written second.
2. Websites LOVE to not follow any convention for their URLS so if you find some combination of show and episode
that doesn't work right please comment or message so we can work to make this work for as many websites and shows
possible.


License
======

I'll add a real license at some point but whatever one means you can use for personal use but can't make money without
my permission... Is that a thing?  Sure let's say it is!



