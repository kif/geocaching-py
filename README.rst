==========================
GeoCaching tools in Python
==========================

Rationale
=========

This project started from the sad fact that there is no official
Garmin browser plugin for Linux.

Most modern Garmin devices can be connected to a Linux PC and will be
automatically recognized as a mass storage device and mounted.

These tools can download information about geocaches from the
`geocaching.com`_ website and save it in Garmin-recognizable .gpx
files. You can copy these files to your navigator, unmount and
disconnect it from your Linux PC and enjoy paperless geocaching
experience.

Installation and configuration
==============================

You will need the following python libraries installed:

- `lxml <http://codespeak.net/lxml/>`_ (Fedora package python-lxml).
- `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_
  (Fedora package python-BeautifulSoup).

You can install all these under Fedora Linux using this command::

  sudo yum install -y python-lxml python-BeautifulSoup

The project itself requires no special installation steps. To
configure run any of the scripts once to create the configuration
directory (``$HOME/.config/geocaching-py/``). Launch your editor and
create a file ``$HOME/.config/geocaching-py/login`` containing a
single line with your `geocaching.com`_ account login and password
separated by a semicolon, like this::

  harrypotter:topsecret

These tools do not require premium membership account, a free account
is sufficient.

You are now ready to use the applications.

Applications
============

save-gpx.py
-----------

Save information about a geocache to a gpx file with auto-generated
file name. Accepts any number of geocache IDs (like GCxxxx) or GUIDs
(long sequences numbers seen after ``guid=`` on geocache page URLs).

The file would have a name of GCXXXXX.gpx where GCXXXX is the geocache
ID. For example, this command::

  ./save-gpx.py GC26BXM ac4169d7-314d-432a-804b-5109a6bd350e

would create two files, GC26BXM.gpx and GC2CW2B.gpx, containing
information about `Duck and Cover`_ and `A Yarn in the Hand`_ geocaches.

.. _`Duck and Cover`: http://www.geocaching.com/seek/cache_details.aspx?guid=791ef98f-a199-411b-b25d-610cbf623879
.. _`A Yarn in the Hand`: http://www.geocaching.com/seek/cache_details.aspx?guid=ac4169d7-314d-432a-804b-5109a6bd350e

save-for-address.py
-------------------

Find geocaches around a given address within the given radius, print
their listing and save information about geocaches. The first argument
for the command should be the radius of search in km. The rest of the
command line is concatenated into an address, so the following two
commands provide identical results::

  ./save-for-address.py 100 Palo Alto, CA
  ./save-for-address.py 100 "Palo Alto, CA"

This command is interactive. It will first display a number of
geocaches and number of search results pages found for your address
and ask for a number of caches you would like to download. The search
results are usually sorted by distance from your point of search, so
it is often not necessary to download all caches available. Please
note, that the number of search results include also *archived* and
*disabled* caches, which would NOT be downloaded by this tool.

Enter the number of caches to download or just hit enter to download
all caches and wait. All available caches matching your query will be
downloaded and saved in gpx files in your current directory.

Author
======

This software is written by Lev Shamardin <shamardin@gmail.com>. Feel
free to contact me on any related questions.

.. _`geocaching.com`:  http://geocaching.com
