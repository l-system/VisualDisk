import hashlib
import math
from pathlib import Path
from typing import Any, Dict, Optional
import matplotlib.patches as patches
import logging


logger = logging.getLogger(__name__)


class FileRect:
    def __init__(self, file_data: Dict[str, Any], x: int, y: int, width: int, height: int):
        self.file_data = file_data
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = self._calculate_color()
        self.hovered = False
        self.patch: Optional[patches.Rectangle] = None


    def _calculate_color(self) -> str:
        file_path = self.file_data.get('path', '')
        size_bytes = self.file_data.get('size_bytes', 0)
        file_ext = Path(file_path).suffix.lower()

        type_colors = {
            '.txt': '#c8c8ff',
            '.py': '#64c896',
            '.js': '#ffc864',
            '.html': '#ff9664',
            '.css': '#9696ff',
            '.jpg': '#ff6496',
            '.jpeg': '#ff6496',
            '.png': '#ff6496',
            '.gif': '#ff6496',
            '.mp4': '#96ff64',
            '.mp3': '#64ff96',
            '.wav': '#64ff96',
            '.pdf': '#ff6464',
            '.doc': '#6496ff',
            '.docx': '#6496ff',
            '.zip': '#c864ff',
            '.tar': '#c864ff',
            '.gz': '#c864ff',
            '': '#969696',  # No extension
        }

        base_color = type_colors.get(file_ext)
        if base_color is None:
            # Generate deterministic random color based on file_ext string
            if file_ext == '':
                base_color = '#969696'  # fallback for no extension
            else:
                # Hash extension to get a reproducible seed
                h = hashlib.md5(file_ext.encode('utf-8')).hexdigest()
                # Use first 6 hex digits as RGB
                base_color = '#' + h[:6]

        # Brightness adjustment as before
        if size_bytes > 0:
            log_size = math.log10(max(size_bytes, 1))
            brightness_factor = min(1.5, 0.5 + (log_size / 10))
            hex_color = base_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            brightened_rgb = tuple(min(255, int(c * brightness_factor)) for c in rgb)
            color = f'#{brightened_rgb[0]:02x}{brightened_rgb[1]:02x}{brightened_rgb[2]:02x}'
        else:
            color = base_color

        return color

    def contains_point(self, x: float, y: float) -> bool:
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def create_patch(self) -> patches.Rectangle:
        color = self.color
        if self.hovered:
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            brightened_rgb = tuple(min(255, c + 50) for c in rgb)
            color = f'#{brightened_rgb[0]:02x}{brightened_rgb[1]:02x}{brightened_rgb[2]:02x}'

        # No visible border because spacing gives visual separation
        patch = patches.Rectangle(
            (self.x, self.y), self.width, self.height,
            facecolor=color,
            edgecolor=(0, 0, 0, 0),  # fully transparent edge
            linewidth=0
        )

        logger.debug(f"create_patch: ({self.x},{self.y}) {self.width}x{self.height}, color={color}")

        self.patch = patch
        return patch

