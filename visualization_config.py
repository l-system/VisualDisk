from dataclasses import dataclass
from typing import Optional

@dataclass
class VisualizationConfig:
    figure_width: float = 16
    figure_height: float = 10
    min_rect_size: int = 2
    max_rect_size: int = 200
    padding: int = 2
    background_color: str = '#0a283c'
    text_color: str = 'white'
    highlight_color: str = '#ffff00'
    border_color: str = '#646464'
    save_format: str = 'png'
    save_path: Optional[str] = None
    interactive: bool = True
