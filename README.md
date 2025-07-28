# PDF Outline Extractor

## Usage

1. Place your PDF files in `/app/input`.
2. Build the Docker image:
   ```bash
   docker build -t pdf-outline-extractor .
   ```
3. Run the container:
   ```bash
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-outline-extractor
   ```
4. Find JSON outline(s) in `/app/output`.

## Debugging

If you get blank JSON files, run the debug script to analyze your PDF:

```bash
docker run --rm -v $(pwd)/input:/app/input pdf-outline-extractor python debug_pdf.py
```

This will show you:
- Font sizes found in your PDF
- Text content and formatting
- Why headings might not be detected

## Approach

- Uses multiple heuristics (font size, style [bold], indentation, and heading patterns) to infer heading levels H1, H2, H3.
- **Fallback methods**: If strict criteria fail, looks for largest fonts and numbered patterns.
- Avoids single-feature detection for robustness.
- JSON result: list of headings with `title`, `level`, `page_number`, `font_size`, `font_name`, and `indent`.

## Notes

- By default, very short/long capture lines and duplicates are filtered.
- The heading detector is designed for general documents—tune regex heuristics as needed for your PDF set.
- **Common issues**: PDFs with images, scanned documents, or unusual font structures may need manual analysis.
