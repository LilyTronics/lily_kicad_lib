# Lily KiCad Library

This is a free to use KiCad library.

Compatible KiCad version: 8

## Latest revisions

* 20240421: Revision 1
  * Standard resistor E24 0805 series, 1R0 up to 9M1, 1%, 125mW

Additional information:

* [Overview of all symbols](https://htmlpreview.github.io/?https://github.com/LilyTronics/lily-kicad-lib/blob/main/documents/symbols_report.html)
* [Symbol naming convention](documents/symbol_naming.md)

## Setup

The library is set up as follows:

```
lily_kicad_lib/
  |- 3d_models
  |- documents
  |- lib_test
  |- lily_footprints.pretty
  |- scripts
  |- symbols
```

### 3D models

The 3D models are taken from three sources:

* KiCad 3D models
* Manufacturer 3D models
* Self created 3D models

### Footprints

Footprints are created using the specifications of the manufacturers.
All footprints have a 3D model attached.

### Symbols

All symbols are self created to ensure consistency.
All symbols have the following extra attributes:

* Revision: numeric value for the revision of the symbol.
* Status: Active, End of life, Obsolete
* Manufacturer (original, alternatives are not added)
* Manufacturer part ID (original, alternatives are not added)
* Part ID field for the ERP system used in LilyTronics.
* Part ID field for the part ID used by JLCPCB.
* JLCPCB part status: Basic, Extended preferred, Extended

### Lib test

KiCad project for evaluating new symbols, footprints and 3D symbols.

## Usage

There are two ways you can use the KiCad libraries:

* As a project specific library
* As a global library

Which one you choose is depending on your preferred way of working. See the KiCad documentation on how to add libraries.
If your KiCad project is also in a git repository, you can clone this library as a sub module in your poject.
See the Git documentatoion on how to add sub modules to your projects.

## Disclamer

It is provided as is, without any support.
We do not take any liability for damages when using this library.

(c) LilyTronics (https://lilytronics.nl)
