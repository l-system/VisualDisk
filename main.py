#!/usr/bin/env python3

import sys
import argparse
import logging
from pathlib import Path
from disk_analyzer import DiskAnalyzer, RealTimeDataStreamer

# Handle visualization imports with explicit error messages
try:
    from disk_visualizer import DiskVisualization, VisualizationConfig

    HAS_VISUALIZER = True
except ImportError as e:
    HAS_VISUALIZER = False
    missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"

    print(f"ERROR: Missing required dependency: {missing_module}", file=sys.stderr)
    print("\nThis program requires the following packages to be installed:", file=sys.stderr)
    print("  • matplotlib (for plotting and visualization)", file=sys.stderr)
    print("  • tkinter (usually included with Python, but may need separate install on some systems)", file=sys.stderr)
    print("\nTo install the required dependencies, run:", file=sys.stderr)
    print("  pip install matplotlib", file=sys.stderr)
    print("\nFor tkinter on Ubuntu/Debian systems:", file=sys.stderr)
    print("  sudo apt-get install python3-tk", file=sys.stderr)
    print("\nFor tkinter on other systems, it's usually included with Python.", file=sys.stderr)
    print("\nPlease install the missing dependencies and try again.", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def select_directory(cli_path=None):
    if cli_path:
        path = Path(cli_path).resolve()
        if path.exists() and path.is_dir():
            return path
        else:
            raise ValueError(f"Invalid directory: {cli_path}")
    else:
        # Prompt user for directory path
        while True:
            user_input = input("Enter directory to scan (leave blank for current directory): ").strip()
            if not user_input:
                return Path.cwd().resolve()
            path = Path(user_input).resolve()
            if path.exists() and path.is_dir():
                return path
            else:
                print(f"Invalid directory: {user_input}. Please try again.")


def normalize_fileinfo_list(files):
    """Convert list of FileInfo into dicts for visualization"""
    normalized = []
    for f in files:
        if not f.is_dir and f.size > 0:
            normalized.append({
                'path': f.path,
                'size_bytes': f.size,
                'size_human': format_size(f.size),
                'file_type': Path(f.path).suffix.lower(),
                'depth': f.depth,
                'is_directory': f.is_dir
            })

    logger.info(f"normalize_fileinfo_list: normalized {len(normalized)} files out of {len(files)} total")
    if normalized:
        logger.info(f"Sample normalized entry: {normalized[0]}")

    return normalized


def format_size(size_bytes: int) -> str:
    """Format file size human-readable"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    elif size_bytes < 1024 ** 4:
        return f"{size_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_bytes / 1024 ** 4:.1f} TB"


def run_analysis(args):
    directory = select_directory(args.directory)
    logger.info(f"Analyzing directory: {directory}")

    def on_update(fileinfo_list):
        logger.info(f"on_update called with {len(fileinfo_list)} files")
        normalized_data = normalize_fileinfo_list(fileinfo_list)
        if not args.no_visualization:
            logger.info(f"Updating visualizer with {len(normalized_data)} entries")
            viz.update_data_realtime(normalized_data)

    streamer = RealTimeDataStreamer(callback_function=on_update, update_interval=args.update_interval)

    analyzer = DiskAnalyzer(
        max_depth=args.max_depth,
        max_files=args.max_files,
        timeout_seconds=args.timeout,
        follow_symlinks=args.follow_symlinks,
        data_streamer=streamer
    )

    if not args.no_visualization:
        config = VisualizationConfig(
            figure_width=args.width / 100,
            figure_height=args.height / 100,
            interactive=not args.non_interactive
        )
        global viz
        viz = DiskVisualization(config)
        viz.load_initial_data(str(directory))

    analyzer.scan_directory(str(directory))
    streamer.flush()

    if not args.no_visualization:
        logger.info("Calling viz.show() to launch visualizer")
        viz.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Disk Usage Visualizer")
    parser.add_argument('directory', nargs='?', help='Directory to scan')
    parser.add_argument('--max-depth', type=int, default=8)
    parser.add_argument('--max-files', type=int, default=100000)
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--follow-symlinks', action='store_true')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=800)
    parser.add_argument('--no-visualization', action='store_true')
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--update-interval', type=float, default=0.5)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        run_analysis(args)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()