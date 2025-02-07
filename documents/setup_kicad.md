# Setup KiCad

This document describes how to set up KiCad with these libraries as global libraries (for every project).

Steps for adding the libraries:

* Launch KiCad.
* In the main view open: Preferences - Manage Symbol Libraries.
* Click the 'Add existing library to the table' button (folder icon).
* Select the 'lily_symbols.kicad_sym' file from this repo.
* Rename the library to 'LilyTronics'.
* Click the OK button
* In the main view open: Preferences - Manage Footprint Libraries.
* Click the 'Add existing library to the table' button (folder icon).
* Select the 'lily_footprints.pretty' folder from this repo.
* Rename the library to 'LilyTronics'.
* Click the OK button

If you also want to use the templates:
* In the main view open: Preferences - Configure Paths.
* Change the folder of the 'KICAD_USER_TEMPLATE_DIR'.
* Select the 'templates' folder from this repo.
* Click the OK button
