from typing import List, Dict, Any, Tuple
from disk_visualizer import FileRect


class TreemapLayout:
    def __init__(self, width: int, height: int, padding: int = 0):
        self.width = width
        self.height = height
        self.padding = padding

    def layout_files(self, file_data: List[Dict[str, Any]]) -> List[FileRect]:
        if not file_data:
            return []

        total_size = sum(f.get('size_bytes', 0) for f in file_data if f.get('size_bytes', 0) > 0)
        if total_size == 0:
            return []

        total_area = self.width * self.height
        scale_factor = total_area / total_size

        rectangles = []
        for f in file_data:
            size = f.get('size_bytes', 0)
            if size > 0:
                area = max(10, int(size * scale_factor))
                rectangles.append((f, area))

        rectangles.sort(key=lambda x: x[1], reverse=True)

        return self._layout_rectangles(rectangles, 0, 0, self.width, self.height)

    def _layout_rectangles(self, rectangles: List[Tuple[Dict[str, Any], float]],
                           x: int, y: int, width: int, height: int) -> List[FileRect]:
        if not rectangles:
            return []

        if len(rectangles) == 1:
            file_data, _ = rectangles[0]
            # No padding here since gap handled between rectangles
            return [FileRect(file_data, x, y, width, height)]

        total_area = sum(area for _, area in rectangles)
        best_split = 1
        best_ratio = float('inf')

        for split in range(1, len(rectangles)):
            group1_area = sum(area for _, area in rectangles[:split])
            group2_area = total_area - group1_area

            if width > height:
                width1 = int(width * group1_area / total_area)
                width2 = width - width1
                if height > 0 and width1 > 0 and width2 > 0:
                    ratio = max(width1 / height, height / width1, width2 / height, height / width2)
                else:
                    ratio = float('inf')
            else:
                height1 = int(height * group1_area / total_area)
                height2 = height - height1
                if width > 0 and height1 > 0 and height2 > 0:
                    ratio = max(width / height1, height1 / width, width / height2, height2 / width)
                else:
                    ratio = float('inf')

            if ratio < best_ratio:
                best_ratio = ratio
                best_split = split

        group1 = rectangles[:best_split]
        group2 = rectangles[best_split:]

        group1_area = sum(area for _, area in group1)
        gap = 1  # 1 pixel gap between rectangles

        result = []
        if width > height:
            width1 = max(1, int(width * group1_area / total_area))
            width2 = max(1, width - width1 - gap)  # subtract gap here

            result.extend(self._layout_rectangles(group1, x, y, width1, height))
            result.extend(self._layout_rectangles(group2, x + width1 + gap, y, width2, height))
        else:
            height1 = max(1, int(height * group1_area / total_area))
            height2 = max(1, height - height1 - gap)  # subtract gap here

            result.extend(self._layout_rectangles(group1, x, y, width, height1))
            result.extend(self._layout_rectangles(group2, x, y + height1 + gap, width, height2))

        return result
