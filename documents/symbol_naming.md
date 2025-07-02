# Symbol naming

Symbol naming is described in the table below.
Space must be replaced with underscores.

| Component                   | Naming convention                                                      | Ref |
|-----------------------------|------------------------------------------------------------------------|-----|
| Bipolar junction transistor | bjt npn/pnp type_number package                                        | Q   | 
| Capacitors E-series         | cap capacity voltage tolerance type package                            | C   |
| Connector                   | con type rows x pins pitch straight/right angle th                     | X   |
| Connector DIN41612          | con din41612 plug/receptacle pins rows straight/right angle th/package | X   |
| Connector terminal          | con terminal screw/screwless rows x pins per row pitch th              | X   |
| Crystal                     | crystal frequency tolerance capacity package                           | X   |
| Diode schottky              | dio schottky type_number package                                       | D   |
| Diode TVS                   | dio tvs uni/bi channels voltage package                                | D   |
| Diode zener                 | dio zener voltage power package                                        | D   |
| IC                          | ic function type_number package                                        | U   |
| IC with channels            | ic function channels type_number package                               | U   |
| IC logic gate               | ic logic gate channels gate_type package                               | U   |
| Inductor bead               | ind bead resistance@frequency current dc_resistance package            | L   |
| Inductor common mode        | ind common mode resistance@frequency current dc_resistance package     | L   |
| Mechanical                  | mec type size                                                          | M   |
| MOSFETs                     | mosfet n/p type_number package                                         | Q   |
| Potentiometer               | pot type resistance tolerance power package                            | R   |
| Resistors E-series          | res resistance tolerance power package                                 | R   |
| Switches                    | switch type package                                                    | S   |

The following attributes should be added (if applicable):

* Revision
* Status
* Footprint
* Manufacturer
* Manufacturer_ID
* Lily_ID
* JLCPCB_ID
* JLCPCB_STATUS
