# Lily KiCad Library

This is a free to use KiCad library.

Compatible KiCad version: 9 (and higher)

* More than 400 symbols and 95 footprints.
* Datasheet for each part (if applicable)
* 3D models for each footprint (if applicable)
* Lily KiCad toolbox:
  * Check library for consistency
  * Generate part IDs for the Lily ERP system
  * Generate manufacturing data for a design
    * PDF files for documentation (schematics and component placement)
    * Import for the Lily ERP
    * Bill of materials (BOM) for Excell
    * BOM for JLCPCB (with specific JLCPCB part IDs)
    * Gerbers and drill files
    * Position file for JLCPCB (can also be used for other manufacturers)
    * ODB+ output
    * 3D model of PCB
    * Archive design after generating output for traceability

Additional information:

* [Overview of all symbols and footprints](https://lilytronics.github.io/lily_kicad_lib/library_report.html)
* [Setup KiCad using this repo](docs/setup_kicad.md)

Do you have a request for a component? Submit a request using the [issue tracker](https://github.com/LilyTronics/lily_kicad_lib/issues).
Please specify a specific manufacturer, manufacturer part ID if possible.

[![Generate report](https://github.com/LilyTronics/lily_kicad_lib/actions/workflows/generate_report.yml/badge.svg)](https://github.com/LilyTronics/lily_kicad_lib/actions/workflows/generate_report.yml)
[![pages-build-deployment](https://github.com/LilyTronics/lily_kicad_lib/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/LilyTronics/lily_kicad_lib/actions/workflows/pages/pages-build-deployment)


## Setup

The repo is set up as follows:

```
lily_kicad_lib/
  |- 3d_models                  # 3D models for the footprints
  |- docs                       # sources for the GitHub pages
  |- documents                  # documentation
  |- lily_footprints.pretty     # footprint library
  |- projects                   # example and test projects
  |- scripts                    # various scripts
  |- symbols                    # symbols library
  |- templates                  # design templates, sheet templates, etc
  |- toolbox                    # sources of the Lily KiCad toolbox, with build script for build an executable
```

### 3D models

The 3D models are taken from three sources:

* KiCad 3D models
* Manufacturer 3D models
* Self created 3D models (design is included in the repo)

### Footprints

Footprints are created using the specifications of the manufacturers.
All footprints have a 3D model attached if applicable.
All footprints have the following extra attributes:

* Revision: numeric value for the revision of the footprint.

### Symbols

All symbols have the following extra attributes:

* Revision: numeric value for the revision of the symbol.
* Status: Active or Obsolete
* Manufacturer: manufacturer name (original, alternatives are not added)
* Manufacturer_ID: manufacturer part ID (original, alternatives are not added)
* Lily_ID: part ID for the ERP system used in LilyTronics.
* JLCPCB_ID: part ID used by JLCPCB.

## Usage

There are two ways you can use the KiCad libraries:

* As a project specific library
* As a global library

Which one you choose is depending on your preferred way of working. See the KiCad documentation on how to add libraries.
If your KiCad project is also in a git repository, you can clone this library as a sub module in your git poject.
See the Git documentation on how to add sub modules to your projects.

## Disclamer

This library is provided as is, without any support.
We do not take any liability for damages when using this library.

(c) LilyTronics (https://lilytronics.nl)
