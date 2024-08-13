# Rock-Particle-Analyzer (RPA)

RPA automates: particle contour detection, measurements and data collection. Users dynamically adjust contour detection parameter to ensure accurate results. 

Created to address the needs of a university research project. 

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Contributing](#contributing)
- [Known Issues](#known-issues)
- [Donations](#donations)

## Introduction



## Features

- Real-time Adjustable Contour Detection: 
     - Modify contour detection parameters on the fly for precise measurements.
     - Press `q` when the image processing window is focused to stop processing.
     - Press `e` when the image processing window is focused to display gathered data from Excel.
- Particle Characteristics Calculation:
     - Minimum Feret Diameter
     - Maximum Feret Diameter
     - Roundness
- Excel Export: 
     - Particle data is automatically saved to an Excel file upon contour click.

## Dependencies

Ensure you have [Python 3.6](https://www.python.org/downloads/) or higher installed.

To install the necessary dependencies, run the following command in your terminal from the project's root directory:
```bash
pip install -r requirements.txt
```

## Usage

1. Configuration:
     - Run the script initially without adjusting the scrollbar.

     - Use the coordinate system provided by the script to measure the scale bar's pixel width.
     ![scale-bar](screenshots/ScaleBar.png)

     - Update the `config.json` file with the measurement to ensure accurate data extraction.
     
     ![configuring](screenshots/config.png)
     

2. Running the script:

     - Execute the following command from the project's root directory:

     ```bash
     python3 main.py
     ```
     - Use the scrollbar to zoom in and adjust contour detection in real-time, ensuring proper contour alignment.
     ![AdjustRealTime](screenshots/AdjustingScrollbarExample.png)

     - Once the contour is properly aligned, click on it. The data will be appeneded to Excel file and displayed in the console.
     ![ClickAndDone](screenshots/ClickAndDone.gif)

## Contributing

If you have any ideas, suggestions, or bug reports, please open an issue, submit a pull request or contact me directly.

## Known Issues

## Donations

Monero
```
884Pjeq7L7n7cCciVnjZuS9dbXj86GqkCKKes4REg9RK2cvhjRNZVUXHsr7WWS3cCtWag48N9ASJe5QzRoyWJM4VJEG7Gje
```
