# Disk Analyzer

A straightforward disk usage analyzer that turns your file system into pretty charts. Because sometimes you need to know *exactly* which folder is hoarding all your disk space (spoiler: it's probably your Downloads folder).

## Usage

```bash
# Scan current directory
python main.py

# Scan a specific directory  
python main.py /path/to/suspicious/folder

# Custom limits for the impatient
python main.py --max-depth 5 --timeout 120 --no-visualization
```

## What It Does

- Scans directories with real-time updates
- Creates visualizations (falls back gracefully if dependencies are missing)
- Human-readable file sizes and sensible defaults

Key options: `--max-depth` (default: 8), `--max-files` (100k), `--timeout` (5 min), `--follow-symlinks`, `--no-visualization`

---
*This entire program was created with LLM assistance - it's just for reference and could definitely be written much better*



![image](https://github.com/user-attachments/assets/d05b8c22-b7b9-4719-a52f-76110cc9e597)
