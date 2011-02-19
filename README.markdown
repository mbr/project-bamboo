About the project
=================
Project Bamboo, which at some point will probably need a new name, is a virtual board game. It is currently being worked on, the goal is to have a playable version in a couple of weeks.

See below on how to install.

Screenshots
-----------
A few screenshots to give a quick impression of the current state (as of Feb 17, 2011):

* <http://dope.marcbrinkmann.de/download/8ec5663c-b522-41c5-9f60-8ffe24d26159>
* <http://dope.marcbrinkmann.de/download/e5551a51-a6b5-4b4b-bb61-830efaa8861b>
* <http://dope.marcbrinkmann.de/download/4bb84c7b-0df9-4490-bd42-a679caf72766>
* <http://dope.marcbrinkmann.de/download/e924aa06-2e52-4995-b0f1-4a965fdde34d>

Current state
-------------
At the moment, the game is "runnable", but hardly playable. Only a bit of game logic is implemented and it is not accessible through the interface.

The rendering of a game state is nearly complete, with the board done in 3D. Every time you start the application, you will get a new board laid out according to the rules, as well as some random cards and tokens placed.

You can also try out *picking* - clicking objects on the board - and see that they are colored differently once you click them.

When pressing the `m`-Key, the game will switch to mouse control. Press and hold the left and/or right mouse button to move the camera in this mode. If you only  see gray when switching the mode, restart the application, as you have inadvertently moved the camera position in the other mode.

Installation
============
There is no installer for the game yet, so installation must be done "by hand":

Required libraries
------------------
* [Python 2.5 or higher](http://python.org) (bundled with Panda on Windows and Mac)
* [Panda3D](http://panda3d.org) - a 3D game library for python
* [NetworkX](http://http://networkx.lanl.gov/), version 1.0 or higher - a graph library for python

There are binary packages for Fedora 12, Ubuntu 10.04, 10.10 of Panda3D on the Panda3D homepage. *NetworkX* must be installed manually. On Linux or Mac, pip or `easy_install` can be used to do this.

Example for a current Mac OS X:

    $ easy_install2.5 "networkx>=1.0"

This will install the *NetworkX* package.

Starting
--------
Once you have *Panda3D* and *NetworkX* installed, you can run the game with

    $ python boardtest.py

If that does not work, trying using `ppython` instead of `python` to start.

Unit tests
----------
*unittest2* or Python 2.7 are required to run unittests, as well as *[mock](http://www.voidspace.org.uk/python/mock/)*. If unittest2 is installed, simply run

    $ unit2 discover

to run the unittests.

If *[coverage](http://nedbatchelder.com/code/coverage/)* is installed as well, coverage can be run to check the test coverage with

    $ coverage run `which unit2` discover
    $ coverage html

which will create a directory `htmlcov` with the results.
