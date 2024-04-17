# Lily KiCad Library

This is a free to use KiCad library.

Compatible KiCad version: 8

Addintional information:

* [Symbol naming convention](documents/symbol_naming.md)
* [Part list](documents/part_list.md)

## Setup

The library is set up as follows:

```
lily_kicad_lib/
  |- 3d_models
  |- footprints
  |- lib_test
  |- symbols
```

### 3D models

The 3D models are taken from three sources:

* KiCad 3D models
* Manufacturer 3D models
* Self created 3D models

### footprints

Footprints are created using the specifications of the manufacturers.
All footprints have a 3D model attached.

### Symbols

All symbols are self created to ensure consistensy. All symbols have the following extra attributes:

* Extra values for voltage/current/power/tolerance etc.
* Part ID field for the ERP system used in LilyTronics.
* Part ID field for the part ID used by JLCPCB.

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

