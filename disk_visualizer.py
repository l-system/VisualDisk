import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import tkinter as tk  # For screen size detection

from visualization_config import VisualizationConfig, FileRect
from treemap_layout import TreemapLayout

logger = logging.getLogger(__name__)


class DiskVisualization:
    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()

        # Determine screen size for 80% window dimensions
        root = tk.Tk()
        root.withdraw()  # Hide main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()

        dpi = 100  # Typical matplotlib DPI
        fig_width = (screen_width * 0.8) / dpi
        fig_height = (screen_height * 0.8) / dpi

        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        self.fig.patch.set_facecolor(self.config.background_color)

        # Remove matplotlib toolbar by pack_forget if available
        try:
            if hasattr(self.fig.canvas.manager, "toolbar") and self.fig.canvas.manager.toolbar is not None:
                self.fig.canvas.manager.toolbar.pack_forget()
        except Exception as e:
            logger.warning(f"Could not remove toolbar: {e}")

        # Setup subplots: main plot and info panel
        import matplotlib.gridspec as gridspec
        gs = gridspec.GridSpec(1, 5, figure=self.fig)
        self.ax_main = self.fig.add_subplot(gs[0, :4])
        self.ax_info = self.fig.add_subplot(gs[0, 4])

        self.ax_main.set_facecolor(self.config.background_color)
        self.ax_main.set_aspect('equal')
        self.ax_main.axis('off')

        self.ax_info.set_facecolor('#282832')
        self.ax_info.axis('off')

        self.file_rects: List[FileRect] = []
        self.hovered_rect: Optional[FileRect] = None
        self.update_lock = threading.RLock()
        self.pending_update = False
        self.current_files: List[Dict[str, Any]] = []
        self.target_directory = ""

        self._start_update_timer()

    def _start_update_timer(self):
        def timer_callback():
            updated = self._check_and_perform_update()
            if updated:
                self.redraw()

        # Create the timer once
        self.timer = self.fig.canvas.new_timer(interval=500)
        self.timer.add_callback(timer_callback)
        self.timer.start()

    def load_initial_data(self, root_directory: str) -> bool:
        try:
            self.target_directory = root_directory
            plot_width = 1000
            plot_height = 800
            self.ax_main.set_xlim(0, plot_width)
            self.ax_main.set_ylim(0, plot_height)

            with self.update_lock:
                self.current_files = []
                self.file_rects = []

            logger.info("Initialized for real-time visualization")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    def normalize_file_data(self, file_data: List[Any]) -> List[Dict[str, Any]]:
        normalized = []
        for file_info in file_data:
            if hasattr(file_info, 'path'):
                size_bytes = getattr(file_info, 'size_bytes', getattr(file_info, 'size', 0))
                is_dir = getattr(file_info, 'is_directory', getattr(file_info, 'is_dir', False))
                depth = getattr(file_info, 'depth', 0)
                file_dict = {
                    'path': getattr(file_info, 'path', ''),
                    'size_bytes': size_bytes,
                    'size_human': self._format_size(size_bytes),
                    'file_type': Path(getattr(file_info, 'path', '')).suffix.lower(),
                    'depth': depth,
                    'is_directory': is_dir
                }
            elif isinstance(file_info, dict):
                file_dict = file_info.copy()
                if 'size_human' not in file_dict:
                    file_dict['size_human'] = self._format_size(file_dict.get('size_bytes', 0))
                if 'file_type' not in file_dict:
                    file_dict['file_type'] = Path(file_dict.get('path', '')).suffix.lower()
                if 'depth' not in file_dict:
                    file_dict['depth'] = 0
                if 'is_directory' not in file_dict:
                    file_dict['is_directory'] = False
            else:
                continue

            if file_dict.get('size_bytes', 0) > 0 and not file_dict.get('is_directory', False):
                normalized.append(file_dict)

        return normalized

    def create_visualization(self, file_data: List[Dict[str, Any]], target_dir: str) -> bool:
        try:
            self.target_directory = target_dir
            if not file_data:
                logger.warning("No files to visualize")
                return False
            with self.update_lock:
                self.current_files = file_data
                self._update_layout()
            self.show()
            return True
        except Exception as e:
            logger.error(f"Failed to create visualization: {e}")
            return False

    def _update_layout(self):
        plot_width = 1000
        plot_height = 800
        layout = TreemapLayout(plot_width, plot_height, self.config.padding)
        self.file_rects = layout.layout_files(self.current_files)
        self.ax_main.set_xlim(0, plot_width)
        self.ax_main.set_ylim(0, plot_height)
        logger.info(f"_update_layout: laid out {len(self.file_rects)} rectangles from {len(self.current_files)} files")

    def update_data_realtime(self, new_file_data: List[Dict[str, Any]]) -> None:
        try:
            with self.update_lock:
                self.current_files = new_file_data
                self.pending_update = True

            if hasattr(self.fig, 'canvas') and self.fig.canvas:
                self.fig.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error in real-time update: {e}")

    def _check_and_perform_update(self) -> bool:
        try:
            with self.update_lock:
                if self.pending_update:
                    self._update_layout()
                    self.pending_update = False
                    return True
            return False
        except Exception as e:
            logger.error(f"Error in update check: {e}")
            return False

    def update_info_panel(self) -> None:
        self.ax_info.clear()
        self.ax_info.set_facecolor('#282832')
        self.ax_info.axis('off')

        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)

        self.ax_info.text(0.05, 0.95, "File Information",
                          fontsize=14, fontweight='bold',
                          color=self.config.text_color,
                          transform=self.ax_info.transAxes,
                          wrap=True)

        with self.update_lock:
            file_count = len(self.current_files)

        self.ax_info.text(0.05, 0.88, f"Files: {file_count:,}",
                          fontsize=10, color='#c8c8c8',
                          transform=self.ax_info.transAxes,
                          wrap=True)

        if self.hovered_rect:
            file_data = self.hovered_rect.file_data
            y_pos = 0.82

            # Name label (bold, right aligned)
            name_label = "Name:"
            name_text = file_data['path']
            wrapped_name_lines = self._wrap_text(name_text, 50)

            # Label x and data x positions
            label_x = 0.05
            data_x = 0.12

            # Draw label on first line only
            if wrapped_name_lines:
                self.ax_info.text(label_x, y_pos, name_label,
                                  fontsize=10, fontweight='bold',
                                  color=self.config.text_color,
                                  transform=self.ax_info.transAxes,
                                  wrap=True,
                                  verticalalignment='top',
                                  horizontalalignment='right')

                # Print first line of wrapped text next to label, with x offset
                self.ax_info.text(data_x, y_pos, wrapped_name_lines[0],
                                  fontsize=9, fontweight='normal',
                                  color=self.config.text_color,
                                  transform=self.ax_info.transAxes,
                                  wrap=True,
                                  verticalalignment='top',
                                  horizontalalignment='left')

                y_pos -= 0.06

                # Remaining wrapped lines (if any) below with indent (aligned with data_x)
                for line in wrapped_name_lines[1:]:
                    self.ax_info.text(data_x, y_pos, line,
                                      fontsize=9, fontweight='normal',
                                      color=self.config.text_color,
                                      transform=self.ax_info.transAxes,
                                      wrap=True,
                                      verticalalignment='top',
                                      horizontalalignment='left')
                    y_pos -= 0.06
            else:
                # No wrapping needed, print full line with label and data on same line
                self.ax_info.text(label_x, y_pos, name_label,
                                  fontsize=10, fontweight='bold',
                                  color=self.config.text_color,
                                  transform=self.ax_info.transAxes,
                                  wrap=True,
                                  verticalalignment='top',
                                  horizontalalignment='right')
                self.ax_info.text(data_x, y_pos, name_text,
                                  fontsize=9, fontweight='normal',
                                  color=self.config.text_color,
                                  transform=self.ax_info.transAxes,
                                  wrap=True,
                                  verticalalignment='top',
                                  horizontalalignment='left')
                y_pos -= 0.06

            # Size label and value
            size_human = file_data.get('size_human', self._format_size(file_data.get('size_bytes', 0)))
            self.ax_info.text(label_x, y_pos, "Size:",
                              fontsize=10, fontweight='bold',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='right')
            self.ax_info.text(data_x, y_pos, size_human,
                              fontsize=9, fontweight='normal',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='left')
            y_pos -= 0.06

            # Type label and value
            file_type = file_data.get('file_type', 'unknown')
            self.ax_info.text(label_x, y_pos, "Type:",
                              fontsize=10, fontweight='bold',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='right')
            self.ax_info.text(data_x, y_pos, file_type,
                              fontsize=9, fontweight='normal',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='left')
            y_pos -= 0.06

            # Depth label and value
            depth = file_data.get('depth', 'unknown')
            self.ax_info.text(label_x, y_pos, "Depth:",
                              fontsize=10, fontweight='bold',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='right')
            self.ax_info.text(data_x, y_pos, str(depth),
                              fontsize=9, fontweight='normal',
                              color=self.config.text_color,
                              transform=self.ax_info.transAxes,
                              wrap=True,
                              verticalalignment='top',
                              horizontalalignment='left')
            y_pos -= 0.08

        else:
            instructions = [
                "Hover over rectangles",
                "to see file details",
                "",
                "Real-time scanning...",
                "Close window to exit"
            ]

            y_pos = 0.7
            for instruction in instructions:
                self.ax_info.text(0.05, y_pos, instruction,
                                  fontsize=10, color='#b4b4b4',
                                  transform=self.ax_info.transAxes,
                                  wrap=True)
                y_pos -= 0.06

    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        if len(text) <= max_chars:
            return [text]

        lines = []
        remaining_text = text
        while remaining_text:
            if len(remaining_text) <= max_chars:
                lines.append(remaining_text)
                break
            else:
                break_point = max_chars
                # Find a good break point at space or slash to avoid breaking words/paths
                for i in range(max_chars - 1, max_chars // 2, -1):
                    if remaining_text[i] in [' ', '/', '\\']:
                        break_point = i + 1
                        break

                # If no good break point found, break at max_chars anyway
                lines.append(remaining_text[:break_point].rstrip())
                remaining_text = remaining_text[break_point:].lstrip()

        return lines

    def _format_size(self, size_bytes: int) -> str:
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

    def on_mouse_move(self, event: Any) -> None:
        if not hasattr(event, 'inaxes') or not hasattr(event, 'xdata') or not hasattr(event, 'ydata'):
            return

        if event.inaxes != self.ax_main or event.xdata is None or event.ydata is None:
            if self.hovered_rect:
                self.hovered_rect.hovered = False
                self.hovered_rect = None
                self.redraw()
            return

        new_hovered = None
        with self.update_lock:
            for rect in self.file_rects:
                if rect.contains_point(event.xdata, event.ydata):
                    new_hovered = rect
                    break

        if new_hovered != self.hovered_rect:
            if self.hovered_rect:
                self.hovered_rect.hovered = False
            self.hovered_rect = new_hovered
            if self.hovered_rect:
                self.hovered_rect.hovered = True
            self.redraw()

    def redraw(self) -> None:
        try:
            self._check_and_perform_update()
            self.ax_main.clear()
            self.ax_main.set_facecolor(self.config.background_color)
            self.ax_main.axis('off')

            # Reset axis limits after clearing:
            self.ax_main.set_xlim(0, 1000)
            self.ax_main.set_ylim(0, 800)

            for rect in self.file_rects:
                patch = rect.create_patch()
                self.ax_main.add_patch(patch)

            self.update_info_panel()
            self.fig.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error during redraw: {e}")

    def show(self) -> None:
        if self.config.interactive:
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            plt.show()

    def run(self) -> None:
        self.show()
