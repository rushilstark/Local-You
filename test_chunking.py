#!/usr/bin/env python3
"""Test the chunking logic directly without embeddings"""

from pathlib import Path

def test_chunk_text():
    # Read the first diary file
    with open("data/diary/Google Keep Document (1).txt", "r") as f:
        text = f.read()
    
    lines = text.split('\n')
    print(f"Total lines: {len(lines)}\n")
    
    # Helper functions
    def is_metadata_or_author(line: str) -> bool:
        """Lines to skip: author names, dates, thank you lines"""
        stripped = line.strip()
        if not stripped:
            return True
        if stripped in ['Rushil', 'Rushil Reddy', 'Rushil Stark', 'Thank you Algorithm']:
            return True
        # Skip dates
        if any(month in stripped for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
            if len(stripped) < 30 and any(char.isdigit() for char in stripped):
                return True
        return False
    
    def looks_like_header(line: str) -> bool:
        """Check if a line looks like an essay header"""
        stripped = line.strip()
        
        if not stripped or len(stripped) > 80:
            return False
        
        # ALL CAPS headers like "FUCK THIS WORLD"
        if stripped.isupper() and len(stripped) > 2:
            return True
        
        # Title with punctuation like "We Said Yes!!"
        if stripped.endswith(('!!', '!', '?', '...')):
            words = stripped.split()
            if len(words) <= 6 and all(w[0].isupper() or w[0].isdigit() or w[0] in "'\"" for w in words if w):
                return True
        
        # Title-case phrases like "The Curve I Remember"
        if len(stripped) > 3:
            words = stripped.split()
            if 2 <= len(words) <= 6:
                title_words = sum(1 for w in words if w and w[0].isupper())
                if title_words >= len(words) * 0.6 and not (stripped.islower() or stripped[0].islower()):
                    return True
        
        return False
    
    # First pass: Find real essay markers (skip duplicates and subtitles)
    markers = []  # List of (line_index, header_text)
    skip_next = 0
    
    for i in range(len(lines)):
        if skip_next > 0:
            skip_next -= 1
            continue
        
        stripped = lines[i].strip()
        
        if looks_like_header(stripped):
            header = stripped
            
            # Check if next line is a duplicate or subtitle to skip
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or is_metadata_or_author(lines[j])):
                if lines[j].strip() == header or (looks_like_header(lines[j].strip()) and lines[j].strip() != header):
                    # Duplicate header or subtitle found - skip it
                    j += 1
                elif is_metadata_or_author(lines[j]):
                    j += 1
                else:
                    break
            
            markers.append((i, header))
            skip_next = j - i - 1  # Skip the lines we just consumed
    
    print(f"Found {len(markers)} headers:\n")
    for line_num, header in markers[:20]:
        print(f"  Line {line_num+1}: {header}")
    
    print(f"\n{'='*100}")
    print("EXTRACTING SECTIONS:")
    print(f"{'='*100}\n")
    
    # Second pass: Extract content between markers
    chunks = []
    for marker_idx, (marker_line, header_title) in enumerate(markers):
        # Find where content STARTS for this marker
        content_start = marker_line + 1
        
        # Skip all blank lines and metadata after marker
        while content_start < len(lines) and is_metadata_or_author(lines[content_start]):
            content_start += 1
        
        # Find where content ENDS (next marker)
        if marker_idx + 1 < len(markers):
            content_end = markers[marker_idx + 1][0]
        else:
            content_end = len(lines)
        
        # Extract content and clean
        content_lines = lines[content_start:content_end]
        section_content = '\n'.join(content_lines).strip()
        
        if section_content and len(section_content) > 20:
            chunks.append({
                "title": header_title,
                "length": len(section_content),
                "first_line": section_content.split('\n')[0][:60]
            })
    
    print(f"Got {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"{i}. {chunk['title']:35} | {chunk['length']:7} chars")
        print(f"   Start: {chunk['first_line']}...")
    
    return chunks

if __name__ == "__main__":
    test_chunk_text()
