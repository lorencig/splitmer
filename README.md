Here’s the updated documentation specifically for `pdf_splitter_gui.py`:

---

# PDF Splitter GUI

## Overview

`pdf_splitter_gui.py` is a PyQt6-based graphical application for splitting and merging PDF files into chapters. It provides an intuitive interface for selecting files, configuring chapters, and tracking the progress of the operation.

---

## Features

- **File Selection**: Browse and select a PDF file, chapter configuration file (`ch.txt`), and an output folder.
- **Chapter Splitting**: Splits the selected PDF into individual chapters based on the provided configuration.
- **Interactive Progress Tracking**: Displays the status of each chapter's processing in a table and a progress bar.
- **Error Handling**: Provides clear error messages and logs for debugging.

---

## Installation Guide

### Prerequisites

Ensure the following are installed:
- Python 3.9+
- PyQt6 (for GUI)
- PyPDF2 (for PDF manipulation)

### Steps to Install

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lorencig/splitmer.git
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/Mac
   venv\Scripts\activate      # For Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install PyQt6 PyPDF2
   ```

---

## Usage

### Running the Application

Launch the GUI by running the script:
```bash
python pdf_splitter_gui.py
```

### Steps in the GUI

1. **Select the PDF File**  
   - Use the "Browse PDF" button to select the PDF file you want to split.

2. **Select the Chapter File**  
   - Use the "Browse ch.txt" button to select the chapter configuration file.
   - The chapter file should follow this format:
     ```
     01 Chapter_Title_1 1 10
     02 Chapter_Title_2 11 20
     -
     10 Chapter_Title_10 101 110
     ```
     Columns:
     - Chapter number
     - Chapter title
     - Start page
     - End page

3. **Select the Output Folder**  
   - Use the "Browse Output Folder" button to choose where the output files will be saved.

4. **Start Processing**  
   - Click the "Start Processing" button to begin splitting and merging chapters.
   - The table will update with the processing status of each chapter.
   - A progress bar will display the overall progress.

5. **View Output**  
   - Once processing is complete, the output files will be available in the selected folder.

---

## Notes

- Ensure the chapter file (`ch.txt`) follows the required format for proper functionality.
- The application handles errors gracefully. Any issues encountered during processing will be displayed in a message box.

---

## Example

### Input
- **PDF**: `sample.pdf`
- **Chapter File (`ch.txt`)**:
  ```
  1 Introduction 1 5
  2 Methods 6 15
  3 Results 16 25
  ```

### Output
- `Chapter_1_Introduction.pdf`
- `Chapter_2_Methods.pdf`
- `Chapter_3_Results.pdf`

---

Kudos to https://github.com/qkcire
