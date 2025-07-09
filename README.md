# VisualDisk

VisualDisk is a Python-based application designed to analyze and visualize disk usage in a given directory in real-time. It generates an interactive treemap visualization, allowing users to quickly identify large files and directories.

Features
Real-time Scanning: Scans directories and updates the visualization as files are discovered.

Interactive Treemap: Displays disk usage as a treemap where the size of each rectangle corresponds to the file or directory size.

File Information on Hover: Hover over any rectangle to see detailed information about the file or directory (path, size, type, depth).

Customizable Scan Parameters: Adjust maximum depth, file limits, and scan timeouts.

Responsive Visualization: The treemap adapts to the window size, and the info panel provides relevant details.


![VisualDisk](https://github.com/user-attachments/assets/ca6e0b05-a6fc-4116-b31d-b349764f9eb6)


Requirements
Python 3.x

matplotlib

tkinter (usually comes with Python, used for screen size detection)

Installation
Clone the repository:

git clone https://github.com/l-system/VisualDisk.git
cd VisualDisk

(Note: Replace YOUR_USERNAME with your actual GitHub username.)

Install dependencies:
It's recommended to use a virtual environment.

python3 -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`
pip install matplotlib

Usage
Run the main.py script from your terminal. You can specify a directory to scan or let it prompt you.

python3 main.py [directory_to_scan] [options]

Examples:

Scan the current directory (interactive):

python3 main.py

(It will prompt you to enter a directory, or press Enter for current.)

Scan a specific directory:

python3 main.py /path/to/your/folder

Scan with a maximum depth of 5 and no visualization (for analysis only):

python3 main.py /path/to/your/folder --max-depth 5 --no-visualization

Scan without interactivity (e.g., for screenshots or non-GUI environments):

python3 main.py /path/to/your/folder --non-interactive

Available Options:

directory: (Optional) The path to the directory to scan. If omitted, it will prompt for input.

--max-depth <int>: Maximum depth to scan (default: 8).

--max-files <int>: Maximum number of files to process (default: 100000).

--timeout <int>: Timeout for the scan in seconds (default: 300).

--follow-symlinks: (Flag) Follow symbolic links. By default, symbolic links are not followed.

--width <int>: Width of the visualization window in pixels (default: 1200).

--height <int>: Height of the visualization window in pixels (default: 800).

--no-visualization: (Flag) Run only the disk analysis without launching the graphical visualization.

--non-interactive: (Flag) Run the visualization in non-interactive mode (no mouse hover effects).

--update-interval <float>: Interval in seconds for real-time visualization updates (default: 0.5).

Project Structure
main.py: The main entry point of the application. Handles argument parsing, initializes the disk analyzer and visualizer, and manages the data flow.

disk_analyzer.py: Contains the DiskAnalyzer class for recursively scanning directories and the RealTimeDataStreamer for sending file information in batches.

disk_visualizer.py: Manages the Matplotlib-based visualization. Handles rendering the treemap, displaying file information on hover, and updating the display in real-time.

treemap_layouter.py: Implements the treemap layout algorithm, calculating the positions and dimensions of rectangles based on file sizes.

file_rect.py: Defines the FileRect class, representing a single rectangle in the treemap, including its data, position, and color calculation logic.

visualization_config.py: A dataclass for holding configuration parameters related to the visualization's appearance and behavior.

License
This project is open-source and available under the MIT License.
