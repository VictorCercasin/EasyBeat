from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QComboBox, QPushButton, QButtonGroup, QRadioButton, QStackedWidget
import sys
import wfdb
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, resample
from tensorflow.keras.preprocessing.sequence import pad_sequences

class ECGAnalysisApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ECGAnalysisApp, self).__init__()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Set up individual pages
        self.download_page = QtWidgets.QWidget()
        self.preprocess_page = QtWidgets.QWidget()
        self.analysis_page = QtWidgets.QWidget()

        self.setup_download_ui()
        self.setup_preprocess_ui()
        self.setup_analysis_ui()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.download_page)
        self.stacked_widget.addWidget(self.preprocess_page)
        self.stacked_widget.addWidget(self.analysis_page)

        # Show the download page initially
        self.stacked_widget.setCurrentWidget(self.download_page)

    def setup_download_ui(self):
        self.download_page.setWindowTitle("ECG Analysis Tool - Download Data")
        self.download_page.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(self.download_page)

        self.downloadButton = QtWidgets.QPushButton("Download Data")
        layout.addWidget(self.downloadButton)

        self.numFiles = QtWidgets.QSpinBox()
        self.numFiles.setRange(1, 1000)
        self.numFiles.setPrefix("Number of Files: ")
        layout.addWidget(self.numFiles)

        self.downloadButton.clicked.connect(self.download_data)

        # Check if data already exists
        if os.path.exists('mitdb'):
            self.skipDownloadButton = QtWidgets.QPushButton("Skip to Preprocess")
            layout.addWidget(self.skipDownloadButton)
            self.skipDownloadButton.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.preprocess_page))

    def setup_preprocess_ui(self):
        self.preprocess_page.setWindowTitle("ECG Analysis Tool - Preprocess Data")
        self.preprocess_page.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(self.preprocess_page)

        self.low_cutoff = QtWidgets.QSpinBox()
        self.low_cutoff.setRange(0, 100)
        self.low_cutoff.setValue(1)
        self.low_cutoff.setPrefix("Low Cutoff: ")
        layout.addWidget(self.low_cutoff)

        self.high_cutoff = QtWidgets.QSpinBox()
        self.high_cutoff.setRange(0, 100)
        self.high_cutoff.setValue(40)
        self.high_cutoff.setPrefix("High Cutoff: ")
        layout.addWidget(self.high_cutoff)

        self.normalizeCheckbox = QtWidgets.QCheckBox("Normalize Data")
        layout.addWidget(self.normalizeCheckbox)

        self.resampleRadio = QRadioButton("Resample")
        self.resampleRadio.setChecked(True)
        self.paddingRadio = QRadioButton("Zero Padding")
        self.paddingGroup = QButtonGroup()
        self.paddingGroup.addButton(self.resampleRadio)
        self.paddingGroup.addButton(self.paddingRadio)
        layout.addWidget(self.resampleRadio)
        layout.addWidget(self.paddingRadio)

        self.paddingSize = QtWidgets.QSpinBox()
        self.paddingSize.setRange(0, 1000)
        self.paddingSize.setValue(300)
        self.paddingSize.setPrefix("Padding Size: ")
        layout.addWidget(self.paddingSize)

        self.preprocessButton = QtWidgets.QPushButton("Preprocess Data")
        layout.addWidget(self.preprocessButton)

        self.preprocessButton.clicked.connect(self.preprocess_data)

        # Check if preprocessed data already exists
        if os.path.exists('beat_data/preprocessed_data.csv') and os.path.exists('beat_data/annotations_train.csv'):
            self.skipPreprocessButton = QtWidgets.QPushButton("Skip to Analysis")
            layout.addWidget(self.skipPreprocessButton)
            self.skipPreprocessButton.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.analysis_page))

    def setup_analysis_ui(self):
        self.analysis_page.setWindowTitle("ECG Analysis Tool - Analyze Data")
        self.analysis_page.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(self.analysis_page)

        
        self.numBeats = QtWidgets.QSpinBox()
        self.numBeats.setRange(1, 1000)
        self.numBeats.setPrefix("Number of Beats: ")
        
        self.beatSelectionLayout = QtWidgets.QVBoxLayout()
        self.beatTypeCheckboxes = {}
        self.numBeatsSpinboxes = {}

        # Load beat types from file if available
        if os.path.exists('beat_data/annotations_train.csv'):
            annotations = pd.read_csv('beat_data/annotations_train.csv')
            unique_beat_types = annotations['beat_type'].unique()
            for beat_type in unique_beat_types:
                checkbox = QtWidgets.QCheckBox(f"{beat_type}")
                spinbox = QtWidgets.QSpinBox()
                spinbox.setRange(1, 1000)
                spinbox.setPrefix(f"Number of Beats for {beat_type}: ")
                spinbox.setEnabled(False)

                checkbox.stateChanged.connect(lambda state, spinbox=spinbox: spinbox.setEnabled(state == 2))

                self.beatTypeCheckboxes[beat_type] = checkbox
                self.numBeatsSpinboxes[beat_type] = spinbox

                self.beatSelectionLayout.addWidget(checkbox)
                self.beatSelectionLayout.addWidget(spinbox)

        layout.addLayout(self.beatSelectionLayout)

        self.selectBeatsButton = QtWidgets.QPushButton("Select Beats")
        layout.addWidget(self.selectBeatsButton)

        self.visualizeButton = QtWidgets.QPushButton("Visualize Data")
        layout.addWidget(self.visualizeButton)

        self.summarizeButton = QPushButton("Summarize Beat Amounts")
        layout.addWidget(self.summarizeButton)

        self.selectBeatsButton.clicked.connect(self.select_beat_data)
        self.visualizeButton.clicked.connect(self.visualize_data)
        self.summarizeButton.clicked.connect(self.summarize_beats)

    def download_data(self):
        # Clean old data
        if os.path.exists('mitdb'):
            for root, dirs, files in os.walk('mitdb', topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir('mitdb')
        # Get the number of files to download
        num_files = self.numFiles.value()
        file_list = [f"100.atr", f"100.dat", f"100.hea"]
        for i in range(101, 100 + num_files):
            file_list.append(f"{i}.atr")
            file_list.append(f"{i}.dat")
            file_list.append(f"{i}.hea")

        try:
            wfdb.dl_files('mitdb', f'{os.getcwd()}/mitdb', file_list, keep_subdirs=False)
            QMessageBox.information(self, 'Success', 'Files downloaded successfully!')
            # Switch to preprocess page
            self.stacked_widget.setCurrentWidget(self.preprocess_page)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to download files: {str(e)}')

    def preprocess_data(self):
        # Clean old preprocessed data
        if os.path.exists('beat_data'):
            for root, dirs, files in os.walk('beat_data', topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir('beat_data')
        try:
            # Bandpass filter settings
            lowcut = self.low_cutoff.value()
            highcut = self.high_cutoff.value()
            normalize = self.normalizeCheckbox.isChecked()
            zero_padding = self.paddingRadio.isChecked()
            target_length = self.paddingSize.value()

            # Load data and preprocess
            data_dir = 'mitdb'
            if not os.path.exists(data_dir):
                raise FileNotFoundError(f"Data directory '{data_dir}' not found. Please download the data first.")

            records = []
            annotations = []
            window_size = target_length // 2  # Half window before and after the beat

            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.dat'):
                        record_path = os.path.join(root, file[:-4])
                        record = wfdb.rdrecord(record_path)
                        annotation = wfdb.rdann(record_path, 'atr')

                        # Use only the first channel if there are multiple channels
                        signal = record.p_signal[:, 0] if record.p_signal.ndim > 1 else record.p_signal.flatten()

                        for i in range(len(annotation.sample)):
                            beat_sample = annotation.sample[i]
                            start = max(0, beat_sample - window_size)
                            end = min(len(signal), beat_sample + window_size)

                            beat_segment = signal[start:end]
                            if len(beat_segment) < target_length:
                                beat_segment = np.pad(beat_segment, (0, target_length - len(beat_segment)), 'constant')

                            records.append(beat_segment)
                            annotations.append(annotation.symbol[i])

            
            # Convert annotations to DataFrame
            annotations = pd.DataFrame(annotations, columns=['beat_type'])
            records = pd.DataFrame(records)
            
            unique_beat_types = annotations['beat_type'].unique()

            if normalize:
                records = records.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)

            # Apply zero padding or resampling
            if not zero_padding:
                records = [resample(beat, target_length) for beat in records.values]
                records = np.array(records)

            # Save preprocessed data
            os.makedirs('beat_data', exist_ok=True)
            pd.DataFrame(records).to_csv('beat_data/preprocessed_data.csv', index=False)
            annotations.to_csv('beat_data/annotations_train.csv', index=False)

            # Update beat type checkboxes
            self.beatSelectionLayout = QtWidgets.QVBoxLayout()
            self.beatTypeCheckboxes = {}
            self.numBeatsSpinboxes = {}
            for beat_type in unique_beat_types:
                checkbox = QtWidgets.QCheckBox(f"{beat_type}")
                spinbox = QtWidgets.QSpinBox()
                spinbox.setRange(1, 1000)
                spinbox.setPrefix(f"Number of Beats for {beat_type}: ")
                spinbox.setEnabled(False)

                checkbox.stateChanged.connect(lambda state, spinbox=spinbox: spinbox.setEnabled(state == 2))

                self.beatTypeCheckboxes[beat_type] = checkbox
                self.numBeatsSpinboxes[beat_type] = spinbox

                self.beatSelectionLayout.addWidget(checkbox)
                self.beatSelectionLayout.addWidget(spinbox)
            analysis_layout = self.analysis_page.layout()
            analysis_layout.addLayout(self.beatSelectionLayout)
            self.stacked_widget.setCurrentWidget(self.analysis_page)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to preprocess data: {str(e)}')

    def select_beat_data(self):
        # Clean old selected beats
        if os.path.exists('selected_beat_data'):
            for root, dirs, files in os.walk('selected_beat_data', topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir('selected_beat_data')
        try:
            # Load annotations and preprocessed data
            annotations = pd.read_csv('beat_data/annotations_train.csv')
            records = pd.read_csv('beat_data/preprocessed_data.csv')

            selected_beat_data = []
            for beat_type, checkbox in self.beatTypeCheckboxes.items():
                if checkbox.isChecked():
                    num_beats = self.numBeatsSpinboxes[beat_type].value()
                    filtered_annotations = annotations[annotations['beat_type'] == beat_type]

                    if len(filtered_annotations) < num_beats:
                        raise ValueError(f"Not enough beats of type {beat_type} available. Only {len(filtered_annotations)} found.")

                    selected_indices = filtered_annotations.sample(n=num_beats).index
                    selected_beat_data.append(records.iloc[selected_indices])

            if not selected_beat_data:
                raise ValueError("No beat types selected.")

            selected_beat_data = pd.concat(selected_beat_data)

            # Create directory for selected beats
            selected_beat_data_dir = 'selected_beat_data'
            os.makedirs(selected_beat_data_dir, exist_ok=True)

            # Save each selected beat in the 'selected_beat_data' folder
            selected_beat_data.to_csv(f'{selected_beat_data_dir}/selected_beat_data.csv', index=False)

            QMessageBox.information(self, 'Success', 'Selected beats have been saved successfully!')

                        
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to select beat data: {str(e)}')

    def visualize_data(self):
        try:
            # Load selected beats and annotations
            beats = pd.read_csv('selected_beat_data/selected_beat_data.csv')
            annotations = pd.read_csv('beat_data/annotations_train.csv')

            # Plot the beats
            plt.figure(figsize=(15, 10))
            for i in range(min(10, len(beats))):
                plt.subplot(5, 2, i + 1)
                plt.plot(beats.iloc[i].dropna().values)
                plt.title(f'Beat {i + 1}')
                plt.xlabel(f'Beat Type: {annotations.iloc[i]["beat_type"]}')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to visualize data: {str(e)}')

    def summarize_beats(self):
        try:
            # Load annotations
            annotations = pd.read_csv('beat_data/annotations_train.csv')
            beat_counts = annotations['beat_type'].value_counts()
            summary = "\n".join([f"{beat_type}: {count}" for beat_type, count in beat_counts.items()])
            QMessageBox.information(self, 'Beat Summary', summary)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to summarize beat data: {str(e)}')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = ECGAnalysisApp()
    main_window.show()
    sys.exit(app.exec_())