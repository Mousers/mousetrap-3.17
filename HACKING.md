HACKING
=======

Getting Connected
-----------------

- Join the mailing list: http://mail.gnome.org/mailman/listinfo/mousetrap-list
    - Send an email to the mailing list to introduce yourself and find out when
      the regular IRC meetings are scheduled.
- Hang out on IRC: irc.gnome.org #mousetrap
- Project wiki is here: https://wiki.gnome.org/Projects/MouseTrap
- Issue tracker is here: https://bugzilla.gnome.org/
    - List of bugs:
      https://bugzilla.gnome.org/buglist.cgi?bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_status=NEEDINFO&bug_status=VERIFIED&list_id=5916&product=mousetrap&query_format=advanced
- The repositiory is here: https://github.com/GNOME-MouseTrap/mousetrap


Contributor License Agreement
-----------------------------

All contributions are assumed to be licensed under GPL v3. If you include code
from another project, you must include their license and give them credit for
the code. Only code with licenses compatible with GPL v3 will be accepted.


Contributing
------------

1. Find a bug or report one on bugzilla
2. Comment on the bug and let everyone know you are working on it.
3. Squash your work into a single commit, generate a patch, and post the patch
to original bug report when you are done.

If you stop working on a bug, or are stuck, let others know so that they can
help and/or pick up where you left off.


Version Numbers
---------------

Version numbers track GNOME's platform version numbers. So a release for GNOME
3.15 might be 3.15.6. The code base between releases has its version number
suffixed with `-pre`: e.g., `3.15.7-pre`. This indicates that that code base
will eventually become release `3.15.7`.

Branches
--------

- master - Unstable, but buildable, development branch
- gnome-MAJ-MIN - (e.g., gnome-3-15) Stable branch targeting GNOME MAJ.MIN
- wip/FEATURE - Unstable, possibly unbuildable, development branch for working
  on FEATURE

Tags
----

Tags mark releases and contain the version number of the release (e.g., 3.15.2).


Code Conventions
----------------

- Follow PEP8
- Use `make lint`
- Follow __Clean Code: A Handbook of Agile Software Craftmanship__
- Try to follow the style demonstrated in code
- Controll your whitespace
    - Use spaces to indent
    - Don't end a line in whitespace other than the newline
    - Use UNIX-style line endings
- Write good, self-contained, commit message comments
