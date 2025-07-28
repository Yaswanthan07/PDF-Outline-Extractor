#!/usr/bin/env python3
"""
Debug script to analyze PDF structure and understand why headings aren't being detected.
"""

import os
import pdfplumber
from collections import defaultdict

def analyze_pdf(pdf_path):
    """Analyze PDF structure to understand text extraction"""
    print(f"\n=== Analyzing PDF: {os.path.basename(pdf_path)} ===\n")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Analyze first few pages in detail
        for page_num in range(min(3, len(pdf.pages))):
            page = pdf.pages[page_num]
            print(f"\n--- Page {page_num + 1} ---")
            
            # Extract words with attributes
            words = page.extract_words(extra_attrs=["size", "fontname", "x0", "y0"])
            
            if not words:
                print("  No words found on this page!")
                continue
            
            # Group by font size
            font_sizes = defaultdict(list)
            for word in words:
                text = word['text'].strip()
                if text and len(text) > 1:
                    size = word['size']
                    font_sizes[size].append({
                        'text': text,
                        'font': word['fontname'],
                        'x0': word.get('x0', 0),
                        'y0': word.get('y0', 0)
                    })
            
            # Show font size distribution
            print(f"  Font sizes found: {sorted(font_sizes.keys())}")
            
            # Show largest fonts (potential headings)
            largest_sizes = sorted(font_sizes.keys(), reverse=True)[:5]
            for size in largest_sizes:
                texts = font_sizes[size]
                print(f"  Font size {size}: {len(texts)} words")
                for item in texts[:5]:  # Show first 5
                    print(f"    '{item['text']}' (font: {item['font']}, x: {item['x0']:.1f})")
                if len(texts) > 5:
                    print(f"    ... and {len(texts) - 5} more")
            
            # Show all text on page (first 20 words)
            print(f"  First 20 words on page:")
            for i, word in enumerate(words[:20]):
                print(f"    {i+1:2d}. '{word['text']}' (size: {word['size']}, font: {word['fontname']})")

def main():
    input_dir = "./input"
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory!")
        return
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        try:
            analyze_pdf(pdf_path)
        except Exception as e:
            print(f"Error analyzing {pdf_file}: {e}")

if __name__ == "__main__":
    main() 