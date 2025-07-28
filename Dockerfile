FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_outline_extractor.py debug_pdf.py .
RUN mkdir -p /app/input /app/output

# Default command runs the main extractor
CMD ["python", "pdf_outline_extractor.py"]
