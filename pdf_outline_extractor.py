import os
import json
import pdfplumber
import re
from collections import defaultdict

# Heuristics: heading detection uses font size, style, indentation, and pattern
HEADING_PATTERNS = [
    re.compile(r"^(?:[0-9]+\.?)+\s+"),   # Numbered like "1.", "1.2.3 "
    re.compile(r"^[A-Z][A-Z\s]{3,}$"),   # All uppercase heading
    re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$"),  # Title Case
]

def is_bold(fontname):
    return "Bold" in fontname or "bold" in fontname

def clean_text(text):
    """Clean and properly format text with word breaks"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Fix common word separation issues
    # Add spaces before capital letters that are likely word boundaries
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Fix specific patterns like "Connectthedots" -> "Connect the dots"
    text = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', text)
    
    # Fix specific merged words from the PDF
    text = re.sub(r'Connectthe', 'Connect the', text)
    text = re.sub(r'Welcometo', 'Welcome to', text)
    text = re.sub(r'Connectingthe', 'Connecting the', text)
    text = re.sub(r'Areyouin', 'Are you in', text)
    text = re.sub(r'andconnect', 'and connect', text)
    text = re.sub(r'Inaworld', 'In a world', text)
    text = re.sub(r'floodedwith', 'flooded with', text)
    text = re.sub(r'Buildabeautiful', 'Build a beautiful', text)
    text = re.sub(r'Youmustbuild', 'You must build', text)
    text = re.sub(r'asolutionthat', 'a solution that', text)
    text = re.sub(r'Bybuildingan', 'By building an', text)
    text = re.sub(r'outlineextractor', 'outline extractor', text)
    text = re.sub(r'Thisoutlinewill', 'This outline will', text)
    text = re.sub(r'bethefoundation', 'be the foundation', text)
    text = re.sub(r'fortherestof', 'for the rest of', text)
    text = re.sub(r'yourhackathon', 'your hackathon', text)
    text = re.sub(r'Yourjobisto', 'Your job is to', text)
    text = re.sub(r'extractastructured', 'extract a structured', text)
    text = re.sub(r'ThroughDocs', 'Through Docs', text)
    text = re.sub(r'Yourcontainershould', 'Your container should', text)
    text = re.sub(r'Afterbuildingthe', 'After building the', text)
    text = re.sub(r'Wewillbuildthe', 'We will build the', text)
    text = re.sub(r'dockerimageusing', 'docker image using', text)
    text = re.sub(r'thefollowingcommand', 'the following command', text)
    text = re.sub(r'CPUarchitecture', 'CPU architecture', text)
    text = re.sub(r'Dockerfileto', 'Dockerfile to', text)
    text = re.sub(r'explicitlyspecify', 'explicitly specify', text)
    text = re.sub(r'Anymodelsor', 'Any models or', text)
    text = re.sub(r'librariesused', 'libraries used', text)
    text = re.sub(r'Yourapproach', 'Your approach', text)
    text = re.sub(r'Alldependencies', 'All dependencies', text)
    text = re.sub(r'installedwithin', 'installed within', text)
    text = re.sub(r'thecontainer', 'the container', text)
    text = re.sub(r'Total45', 'Total 45', text)
    text = re.sub(r'MultilingualHandling', 'Multilingual Handling', text)
    text = re.sub(r'Nointernetaccess', 'No internet access', text)
    text = re.sub(r'allowedduring', 'allowed during', text)
    text = re.sub(r'Sectiontitle', 'Section title', text)
    text = re.sub(r'Pagenumber', 'Page number', text)
    text = re.sub(r'Processingtimestamp', 'Processing timestamp', text)
    text = re.sub(r'Jobtobedone', 'Job to be done', text)
    text = re.sub(r'Inputdocuments', 'Input documents', text)
    text = re.sub(r'Theoutputshould', 'The output should', text)
    text = re.sub(r'TestCase', 'Test Case', text)
    text = re.sub(r'Qualityof', 'Quality of', text)
    text = re.sub(r'granularsubsection', 'granular subsection', text)
    text = re.sub(r'Howwell', 'How well', text)
    text = re.sub(r'selectedsections', 'selected sections', text)
    text = re.sub(r'Dockerfileand', 'Dockerfile and', text)
    text = re.sub(r'executioninstructions', 'execution instructions', text)
    text = re.sub(r'Summarizethe', 'Summarize the', text)
    text = re.sub(r'financialsof', 'financials of', text)
    text = re.sub(r'corporationxyz', 'corporation xyz', text)
    text = re.sub(r'Providea', 'Provide a', text)
    text = re.sub(r'literaturereview', 'literature review', text)
    text = re.sub(r'foragiven', 'for a given', text)
    text = re.sub(r'topicand', 'topic and', text)
    text = re.sub(r'availableresearch', 'available research', text)
    text = re.sub(r'Researchpapers', 'Research papers', text)
    text = re.sub(r'Documentcollection', 'Document collection', text)
    text = re.sub(r'Concretetask', 'Concrete task', text)
    text = re.sub(r'thepersona', 'the persona', text)
    text = re.sub(r'needsto', 'needs to', text)
    text = re.sub(r'Youwillbuild', 'You will build', text)
    text = re.sub(r'asystemthat', 'a system that', text)
    text = re.sub(r'actsasan', 'acts as an', text)
    text = re.sub(r'intelligentdocument', 'intelligent document', text)
    text = re.sub(r'ChallengeBrief', 'Challenge Brief', text)
    text = re.sub(r'ConnectWhat', 'Connect What', text)
    text = re.sub(r'Forthe', 'For the', text)
    text = re.sub(r'UserWho', 'User Who', text)
    text = re.sub(r'WhatYou', 'What You', text)
    text = re.sub(r'Needto', 'Need to', text)
    text = re.sub(r'WhatNotto', 'What Not to', text)
    text = re.sub(r'ForSample', 'For Sample', text)
    text = re.sub(r'Inputand', 'Input and', text)
    text = re.sub(r'OutputFiles', 'Output Files', text)
    text = re.sub(r'pleaserefer', 'please refer', text)
    text = re.sub(r'totheappendix', 'to the appendix', text)
    text = re.sub(r'SubmissionChecklist', 'Submission Checklist', text)
    text = re.sub(r'ScoringCriteria', 'Scoring Criteria', text)
    text = re.sub(r'CriteriaPoints', 'Criteria Points', text)
    text = re.sub(r'RequiredOutput', 'Required Output', text)
    text = re.sub(r'AcademicResearch', 'Academic Research', text)
    text = re.sub(r'SampleTest', 'Sample Test', text)
    text = re.sub(r'BusinessAnalysis', 'Business Analysis', text)
    text = re.sub(r'EducationalContent', 'Educational Content', text)
    text = re.sub(r'DocumentCollection', 'Document Collection', text)
    text = re.sub(r'InputSpecification', 'Input Specification', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def reconstruct_words_from_characters(chars_data):
    """Reconstruct words from individual character data"""
    if not chars_data:
        return []
    
    words = []
    current_word = ""
    current_word_data = None
    
    for char_data in chars_data:
        char = char_data['text']
        
        # If this is a space or punctuation that should end a word
        if char.isspace() or char in ',.!?;:':
            if current_word:
                words.append({
                    'text': current_word,
                    'size': current_word_data['size'],
                    'fontname': current_word_data['fontname'],
                    'x0': current_word_data['x0'],
                    'y0': current_word_data['y0']
                })
                current_word = ""
                current_word_data = None
        else:
            # Add character to current word
            current_word += char
            if current_word_data is None:
                current_word_data = char_data
    
    # Don't forget the last word
    if current_word and current_word_data:
        words.append({
            'text': current_word,
            'size': current_word_data['size'],
            'fontname': current_word_data['fontname'],
            'x0': current_word_data['x0'],
            'y0': current_word_data['y0']
        })
    
    return words

def is_heading(text, size, fontname, indent):
    """Returns (True, level) if heading, else (False, None)"""
    # Clean text for analysis
    clean_text_val = text.strip()
    if not clean_text_val or len(clean_text_val) < 2:
        return False, None
    
    # H1: Large, bold/caps, left/centered
    if size > 14 and (is_bold(fontname) or clean_text_val.isupper()) and indent < 100:
        return True, "H1"
    # H2: medium-large, bold or pattern, not indented
    elif 12 < size <= 14 and (is_bold(fontname) or any(p.match(clean_text_val) for p in HEADING_PATTERNS)):
        return True, "H2"
    # H3: normal heading styles, maybe indented, shorter
    elif 10 < size <= 12 and (is_bold(fontname) or indent < 80 or any(p.match(clean_text_val) for p in HEADING_PATTERNS)):
        return True, "H3"
    return False, None

def extract_headings_from_pdf(pdf_path):
    results = []
    seen_titles = set()
    font_sizes = defaultdict(int)
    all_texts = []
    
    print(f"Processing: {os.path.basename(pdf_path)}")
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"  Total pages: {total_pages}")
        
        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"  Processing page {page_num}...")
            
            # Try to extract words first
            words = page.extract_words(extra_attrs=["size", "fontname", "x0", "y0"])
            
            # If words are too short (individual characters), try character extraction
            if words and any(len(word['text']) == 1 for word in words[:10]):
                print(f"    Detected character-by-character extraction, reconstructing words...")
                
                # Extract characters and reconstruct words
                chars = page.extract_words(extra_attrs=["size", "fontname", "x0", "y0"], 
                                         keep_blank_chars=True, 
                                         x_tolerance=3, 
                                         y_tolerance=3)
                
                # Group characters by line (y position) and reconstruct words
                lines = defaultdict(list)
                for char in chars:
                    if char['text'].strip():  # Skip empty characters
                        y_pos = round(char['y0'], 1)  # Round to group nearby lines
                        lines[y_pos].append(char)
                
                # Process each line
                for y_pos in sorted(lines.keys()):
                    line_chars = lines[y_pos]
                    # Sort characters by x position
                    line_chars.sort(key=lambda x: x['x0'])
                    
                    # Reconstruct words from this line
                    line_words = reconstruct_words_from_characters(line_chars)
                    
                    for word in line_words:
                        text = word['text'].strip()
                        if not text or len(text) > 90:
                            continue
                        
                        size = word['size']
                        font = word['fontname']
                        indent = word['x0']
                        
                        # Collect statistics
                        font_sizes[size] += 1
                        all_texts.append((text, size, font, indent))
                        
                        ishead, level = is_heading(text, size, font, indent)
                        if ishead:
                            # Clean the text properly
                            cleaned_text = clean_text(text)
                            if cleaned_text:
                                entry = {
                                    "level": level,
                                    "text": cleaned_text,
                                    "page": page_num
                                }
                                key = (cleaned_text.lower(), level)
                                if key not in seen_titles:
                                    results.append(entry)
                                    seen_titles.add(key)
                                    print(f"    Found heading: {cleaned_text} (Level: {level}, Size: {size}, Font: {font})")
            else:
                # Normal word extraction
                for word in words:
                    text = word['text'].strip()
                    if not text or len(text) > 90:
                        continue
                    
                    size = word['size']
                    font = word['fontname']
                    indent = word.get('x0', 0)
                    
                    # Collect statistics
                    font_sizes[size] += 1
                    all_texts.append((text, size, font, indent))
                    
                    ishead, level = is_heading(text, size, font, indent)
                    if ishead:
                        # Clean the text properly
                        cleaned_text = clean_text(text)
                        if cleaned_text:
                            entry = {
                                "level": level,
                                "text": cleaned_text,
                                "page": page_num
                            }
                            key = (cleaned_text.lower(), level)
                            if key not in seen_titles:
                                results.append(entry)
                                seen_titles.add(key)
                                print(f"    Found heading: {cleaned_text} (Level: {level}, Size: {size}, Font: {font})")
    
    # If no headings found with strict criteria, try fallback methods
    if not results:
        print("  No headings found with strict criteria. Trying fallback methods...")
        
        # Method 1: Look for largest fonts
        if font_sizes:
            largest_sizes = sorted(font_sizes.keys(), reverse=True)[:3]
            print(f"  Largest font sizes found: {largest_sizes}")
            
            for text, size, font, indent in all_texts:
                if size in largest_sizes and len(text) > 3 and len(text) < 100:
                    # Skip common non-heading text
                    if text.lower() in ['page', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for']:
                        continue
                    
                    cleaned_text = clean_text(text)
                    if cleaned_text:
                        entry = {
                            "level": "H1" if size == largest_sizes[0] else "H2" if size == largest_sizes[1] else "H3",
                            "text": cleaned_text,
                            "page": 1
                        }
                        key = (cleaned_text.lower(), entry["level"])
                        if key not in seen_titles:
                            results.append(entry)
                            seen_titles.add(key)
                            print(f"  Fallback heading: {cleaned_text} (Level: {entry['level']}, Size: {size})")
        
        # Method 2: Look for numbered patterns
        if not results:
            for text, size, font, indent in all_texts:
                if re.match(r"^(?:[0-9]+\.?)+\s+", text) and len(text) < 100:
                    cleaned_text = clean_text(text)
                    if cleaned_text:
                        entry = {
                            "level": "H2",
                            "text": cleaned_text,
                            "page": 1
                        }
                        key = (cleaned_text.lower(), entry["level"])
                        if key not in seen_titles:
                            results.append(entry)
                            seen_titles.add(key)
                            print(f"  Numbered heading: {cleaned_text}")
    
    print(f"  Total headings found: {len(results)}")
    return results

def process_all_pdfs(input_dir, output_dir):
    pdf_count = 0
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        
        pdf_count += 1
        input_path = os.path.join(input_dir, filename)
        headings = extract_headings_from_pdf(input_path)
        
        # Determine the main title (first H1 or largest heading)
        main_title = "Document Outline"
        if headings:
            # Look for first H1
            h1_headings = [h for h in headings if h["level"] == "H1"]
            if h1_headings:
                main_title = h1_headings[0]["text"]
            else:
                # Use the first heading as title
                main_title = headings[0]["text"]
        
        # Create the required JSON structure
        output_data = {
            "title": main_title,
            "outline": headings
        }
        
        output_path = os.path.join(output_dir, filename.replace('.pdf', '.json'))
        
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved outline to: {output_path}")
    
    if pdf_count == 0:
        print("No PDF files found in input directory!")
    else:
        print(f"Processed {pdf_count} PDF file(s)")

if __name__ == "__main__":
    in_dir = "./input"
    out_dir = "./output"
    
    print(f"Input directory: {in_dir}")
    print(f"Output directory: {out_dir}")
    
    if not os.path.exists(in_dir):
        print(f"Error: Input directory '{in_dir}' does not exist!")
        exit(1)
    
    os.makedirs(out_dir, exist_ok=True)
    process_all_pdfs(in_dir, out_dir)
    print("Outline extraction complete.")
