# CellPyAbility

The objective of CellPyAbility is to offer an open-access cell viability analysis tool that seamlessly integrates with our provided [protocols](path/to/protocol).

## Requirements

While we try to make CellPyAbility widely applicable, there are several technical limitations:

- Cells must be adherent or able to adhere to a 96-well plate prior to imaging
- A fluorescence imager capable of exciting around 360 nm is required (DAPI/Hoechst channel, GFP channel likely okay). Although tuned for 20x, the [CellProfiler pipeline](CellPyAbility.cppipe) is easily modulable.
- CellProfiler must be downloaded and saved in the default location for a given operating system (e.g. Windows OS saved in Program Files or Program Files (x86), etc.)