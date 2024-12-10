# CellPyAbility

The objective of CellPyAbility is to offer an open-access cell viability analysis tool that seamlessly integrates with our provided [protocols](path/to/protocol).

## Requirements

While we try to make CellPyAbility widely applicable, there are several technical limitations:

- Cells must be adherent or able to adhere to a 96-well plate prior to imaging.
- Only the inner 60 wells of the 96-well plate should contain cells. The outer wells can be filled with PBS or another solution to help buffer evaporation.
- A fluorescence imager capable of exciting ~360 nm is required (DAPI/Hoechst channel, GFP channel likely okay). Although tuned for 20x magnification, the [CellProfiler pipeline](CellPyAbility/CellPyAbility.cppipe) is easily modulable.
- CellProfiler must be saved in the default location for a given operating system: 
  - Microsoft Windows: Program Files or Program Files(x86)
  - MacOS: Applications
  - Linux: 'cellprofiler'

## Getting Started

Download the [CellPyAbility directory](CellPyAbility). This is the working directory for our program and contains three Python scripts with unique outputs:
- **CellPyAbility_GDA**: dose-response analysis of two cell lines/cell conditions with a drug gradient.
- **CellPyAbility_synergy**: dose-response and synergy (Bliss) analysis of one cell line/cell condition with simultaneous horizontal and vertical drug gradients.
- **CellPyAbility_simple**: raw nuclei count matrix recapitulating the 96-well format.

We provide example image sets in the [test directory](test) with the expected outputs, along with a drug concentration gradient calculation sheet. We recommend running these test sets to ensure the scripts are working properly prior to running one's own data. Please note that the test directory includes 240 images of 2.8 MB each; therefore, downloading it will decrease your available storage for cat videos and increase your carbon footprint substantially.