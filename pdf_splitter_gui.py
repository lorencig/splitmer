import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                          QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                          QLabel, QLineEdit, QHBoxLayout, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import logging
import tempfile

class WorkerThread(QThread):
    progress = pyqtSignal(str, int)  # chapter_name, status (0=started, 1=completed)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, pdf_path, chapters_data, output_dir):
        super().__init__()
        self.pdf_path = pdf_path
        self.chapters_data = chapters_data
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = output_dir

    def split_pdf(self):
        try:
            pdf = PdfReader(self.pdf_path)
            for page_num, page in enumerate(pdf.pages, 1):
                pdf_writer = PdfWriter()
                pdf_writer.add_page(page)
                output_filename = os.path.join(self.temp_dir, f'page_{page_num}.pdf')
                with open(output_filename, 'wb') as out:
                    pdf_writer.write(out)
        except Exception as e:
            self.error.emit(f"Error splitting PDF: {str(e)}")
            return False
        return True

    def process_chapter(self, ch_num, ch_title, start_page, end_page):
        try:
            pdf_merger = PdfMerger()
            for i in range(start_page, end_page + 1):
                page_path = os.path.join(self.temp_dir, f'page_{i}.pdf')
                if os.path.exists(page_path):
                    pdf_merger.append(page_path)

            safe_title = ch_title.replace(',', '').replace(';', '').replace(' ', '_')
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, f'Chapter_{ch_num}_{safe_title}.pdf')
            
            with open(output_path, 'wb') as fileobj:
                pdf_merger.write(fileobj)
            return True
        except Exception as e:
            self.error.emit(f"Error processing chapter {ch_num}: {str(e)}")
            return False

    def cleanup(self):
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
        except Exception as e:
            self.error.emit(f"Error during cleanup: {str(e)}")

    def run(self):
        if not self.split_pdf():
            return

        for chapter in self.chapters_data:
            ch_num, ch_title, start_page, end_page = chapter
            chapter_name = f"Chapter {ch_num}: {ch_title}"
            self.progress.emit(chapter_name, 0)  # Started
            
            if self.process_chapter(ch_num, ch_title, int(start_page), int(end_page)):
                self.progress.emit(chapter_name, 1)  # Completed

        self.cleanup()
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Chapter Splitter")
        self.setMinimumSize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_label = QLabel()
        logo_label.setFixedSize(100, 100)
        
        # Create logo file path
        logo_path = "splitter_logo.svg"
        with open(logo_path, 'w') as f:
            f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                <rect width="100" height="100" fill="#f8f9fa"/>
                <path d="M 20 20 L 80 20 L 80 80 L 20 80 Z" fill="none" stroke="#0066cc" stroke-width="4"/>
                <path d="M 35 35 L 65 35 M 35 50 L 65 50 M 35 65 L 65 65" stroke="#0066cc" stroke-width="4"/>
                <path d="M 40 20 L 40 80 M 60 20 L 60 80" stroke="#0066cc" stroke-width="2" stroke-dasharray="4"/>
            </svg>''')
        
        logo_pixmap = QPixmap(logo_path)
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)

        # Title
        title_label = QLabel("PDF Chapter Splitter")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # PDF File selection
        pdf_layout = QHBoxLayout()
        self.pdf_path = QLineEdit()
        self.pdf_path.setPlaceholderText("Select PDF file...")
        pdf_button = QPushButton("Browse PDF")
        pdf_button.clicked.connect(self.browse_pdf)
        pdf_layout.addWidget(self.pdf_path)
        pdf_layout.addWidget(pdf_button)
        layout.addLayout(pdf_layout)

        # Chapter file selection
        ch_layout = QHBoxLayout()
        self.ch_path = QLineEdit()
        self.ch_path.setPlaceholderText("Select chapter file (ch.txt)...")
        ch_button = QPushButton("Browse ch.txt")
        ch_button.clicked.connect(self.browse_ch)
        ch_layout.addWidget(self.ch_path)
        ch_layout.addWidget(ch_button)
        layout.addLayout(ch_layout)

        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output folder...")
        output_button = QPushButton("Browse Output Folder")
        output_button.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        # Progress Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Chapter", "Status"])
        
        # Set column widths (80% and 20%)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, int(self.width() * 0.8))  # 80% for Chapter column
        self.table.setColumnWidth(1, int(self.width() * 0.2))  # 20% for Status column
        
        layout.addWidget(self.table)

        # Overall progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Start button
        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.start_processing)
        layout.addWidget(self.start_button)

        self.chapters_data = []

    def resizeEvent(self, event):
        """Handle window resize to maintain column proportions"""
        super().resizeEvent(event)
        table_width = self.table.width()
        self.table.setColumnWidth(0, int(table_width * 0.8))
        self.table.setColumnWidth(1, int(table_width * 0.2))

    def browse_pdf(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF file", "", "PDF files (*.pdf)")
        if filename:
            self.pdf_path.setText(filename)

    def browse_ch(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select chapter file", "", "Text files (*.txt)")
        if filename:
            self.ch_path.setText(filename)
            self.load_chapters(filename)

    def browse_output(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dirname:
            self.output_path.setText(dirname)

    def load_chapters(self, filename):
        try:
            self.chapters_data = []
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        ch_num = parts[0]
                        start_page = parts[-2]
                        end_page = parts[-1]
                        ch_title = ' '.join(parts[1:-2])
                        self.chapters_data.append((ch_num, ch_title, start_page, end_page))

            # Update table
            self.table.setRowCount(len(self.chapters_data))
            for i, (ch_num, ch_title, _, _) in enumerate(self.chapters_data):
                self.table.setItem(i, 0, QTableWidgetItem(f"Chapter {ch_num}: {ch_title}"))
                self.table.setItem(i, 1, QTableWidgetItem("Pending"))

        except Exception as e:
            self.show_error(f"Error loading chapters file: {str(e)}")

    def start_processing(self):
        if not self.pdf_path.text() or not self.ch_path.text() or not self.output_path.text():
            self.show_error("Please select PDF file, chapter file, and output folder.")
            return

        self.start_button.setEnabled(False)
        self.progress_bar.setMaximum(len(self.chapters_data))
        self.progress_bar.setValue(0)

        self.worker = WorkerThread(self.pdf_path.text(), self.chapters_data, self.output_path.text())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_progress(self, chapter_name, status):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == chapter_name:
                status_text = "Completed" if status == 1 else "Processing..."
                self.table.setItem(row, 1, QTableWidgetItem(status_text))
                if status == 1:
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                break

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.show_error(f"Processing completed! Check '{self.output_path.text()}' for output files.")

    def show_error(self, message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Information", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
