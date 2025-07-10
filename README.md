# VisualDisk

VisualDisk is a Python-based application designed to analyze and visualize disk usage in a given directory in real-time. It generates an interactive treemap visualization, allowing users to quickly identify large files and directories.

Features
Real-time Scanning: Scans directories and updates the visualization as files are discovered.

Interactive Treemap: Displays disk usage as a treemap where the size of each rectangle corresponds to the file or directory size.

File Information on Hover: Hover over any rectangle to see detailed information about the file or directory (path, size, type, depth).

File Visualization: The treemap adapts to the window size, and the info panel provides relevant details.


![VisualDisk](https://github.com/user-attachments/assets/ca6e0b05-a6fc-4116-b31d-b349764f9eb6)


Requirements
Python 3.x
matplotlib
tkinter (usually comes with Python, used for screen size detection)



Installation
Clone the repository:

git clone https://github.com/l-system/VisualDisk.git
cd VisualDisk



Install dependencies:
It's recommended to use a virtual environment.

python3 -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`
pip install matplotlib




Usage
Run the main.py script from your terminal. You can specify a directory to scan or let it prompt you.

python3 main.py [directory_to_scan] [options]




Available Options:

directory: (Optional) The path to the directory to scan. If omitted, it will prompt for input.

--max-depth <int>: Maximum depth to scan (default: 8, 0 is current directory only).

--max-files <int>: Maximum number of files to process (default: 100000).






License
This project is open-source and available under the MIT License.
