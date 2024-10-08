# ECG Analysis Tool

This project is an ECG (Electrocardiogram) analysis tool developed in Python, using PyQt5 for the user interface. The tool allows users to download ECG data from the PhysioNet MIT-BIH Arrhythmia Database, preprocess the data, and select specific heartbeats for analysis. The program consists of three main functionalities: downloading ECG data, preprocessing the data, and selecting/visualizing specific heartbeats.

## Features
- **Download ECG Data**: Users can download ECG records from PhysioNet (MIT-BIH Arrhythmia Database) using the `wfdb` library. The number of records to download can be specified.
- **Preprocessing**: The program applies a bandpass filter (1Hz to 40Hz) to clean the ECG signal, and users can customize additional options such as normalization, re-sampling or zero-padding, and selecting the final size of each heartbeat.
- **Selection and Visualization**: After preprocessing, users can select how many heartbeats of each class to keep and visualize the selected heartbeats in graphical form.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/VictorCercasin/EasyBeat
    ```

2. **Install dependencies:**
    Make sure you have Python 3.x installed. You can install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

    Example `requirements.txt`:
    ```
    PyQt5
    wfdb
    numpy
    pandas
    matplotlib
    scipy
    tensorflow
    ```

3. **Run the application:**
    Execute the following command to start the application:
    ```bash
    python main.py
    ```

## How It Works

### User Interface Overview
The program is divided into three main screens:

1. **Download Screen**:
   - Allows the user to select how many files (ECG records) to download from the MIT-BIH Arrhythmia Database on PhysioNet.
   - The downloaded files are stored in the `./mitdb` directory.

2. **Preprocessing Screen**:
   - The user can customize the preprocessing options, including:
     - Low and high cutoff frequencies for the bandpass filter.
     - Option to normalize the ECG signal.
     - Option to either re-sample the ECG data to a specific length or apply zero-padding.
   - The preprocessed heartbeats are saved in the `./beat_data` directory.

3. **Selection and Visualization Screen**:
   - The user can select how many heartbeats of each class to keep, with options to specify quantities for individual heartbeat types.
   - Visualize the selected heartbeats in a plot.
   - The selected heartbeats are saved in the `./selected_beat_data` directory.

### Folder Structure
- `./mitdb`: Contains the raw ECG files downloaded from PhysioNet.
- `./beat_data`: Stores the preprocessed individual heartbeats after bandpass filtering, normalization, and segmentation.
- `./selected_beat_data`: Contains the heartbeats selected by the user after preprocessing, ready for analysis.

## Example Workflow

1. **Download Data**:
   - Select the number of records to download from PhysioNet. The program automatically downloads the `.dat`, `.hea`, and `.atr` files for the specified records.

2. **Preprocess Data**:
   - Customize the bandpass filter settings (low/high cutoff frequencies), and choose whether to normalize the data and resample or apply zero-padding.
   - Process the ECG data to extract individual heartbeats and save them in the `./beat_data` directory.

3. **Select and Visualize Heartbeats**:
   - Select how many heartbeats of each type you wish to analyze. The program then allows you to visualize some of the selected heartbeats.
   - The selected heartbeats are saved in the `./selected_beat_data` directory for further analysis.



## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

