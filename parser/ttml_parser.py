import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LyricWord:
    begin_ms: int
    end_ms: int
    text: str

@dataclass
class LyricLine:
    begin_ms: int
    end_ms: int
    text: str
    words: List[LyricWord] = field(default_factory=list)

def parse_time_to_ms(time_str: str) -> int:
    """
    Parses TTML timestamp format to milliseconds.
    Supported formats:
    - hh:mm:ss.mss (e.g. 00:00:10.000)
    - mm:ss.mss (e.g. 00:10.000)
    - ss.mss (e.g. 10.000)
    - seconds (e.g. 10)
    """
    time_str = time_str.strip()
    if not time_str:
        return 0
    
    # Check if format is metric (e.g. "10s", "100ms" - less common in basic TTML but good to handle)
    if time_str.endswith("ms"):
        return int(float(time_str[:-2]))
    elif time_str.endswith("s"):
        return int(float(time_str[:-1]) * 1000)
        
    parts = time_str.split(":")
    if len(parts) == 3:
        # hh:mm:ss.mss
        h = int(parts[0])
        m = int(parts[1])
        s_parts = parts[2].split(".")
        s = int(s_parts[0])
        ms = int(s_parts[1].ljust(3, '0')[:3]) if len(s_parts) > 1 else 0
        return (h * 3600 + m * 60 + s) * 1000 + ms
    elif len(parts) == 2:
        # mm:ss.mss
        m = int(parts[0])
        s_parts = parts[1].split(".")
        s = int(s_parts[0])
        ms = int(s_parts[1].ljust(3, '0')[:3]) if len(s_parts) > 1 else 0
        return (m * 60 + s) * 1000 + ms
    elif len(parts) == 1:
        # ss.mss or raw seconds
        s_parts = parts[0].split(".")
        s = int(s_parts[0])
        ms = int(s_parts[1].ljust(3, '0')[:3]) if len(s_parts) > 1 else 0
        return s * 1000 + ms
    return 0

def parse_ttml(file_path: str) -> List[LyricLine]:
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error reading or parsing XML: {e}")
        return []

    # Namespace handling
    namespaces = {
        'tt': 'http://www.w3.org/ns/ttml',
        'ttm': 'http://www.w3.org/ns/ttml#metadata',
        'tts': 'http://www.w3.org/ns/ttml#styling'
    }

    # Find all paragraph elements
    p_elements = []
    p_elements.extend(root.findall(".//tt:p", namespaces))
    
    if not p_elements:
        for elem in root.iter():
            tag = elem.tag
            if tag.endswith('}p') or tag == 'p':
                p_elements.append(elem)

    lyrics: List[LyricLine] = []
    for p in p_elements:
        begin = p.get('begin') or p.get('{http://www.w3.org/ns/ttml}begin')
        end = p.get('end') or p.get('{http://www.w3.org/ns/ttml}end')
        
        # Get all text nodes within paragraph
        text = "".join(p.itertext()).strip()
        
        if begin and text:
            begin_ms = parse_time_to_ms(begin)
            end_ms = parse_time_to_ms(end) if end else begin_ms + 4000
            
            # Parse spans for word-by-word timing
            words = []
            spans = p.findall(".//tt:span", namespaces)
            if not spans:
                for child in p:
                    tag = child.tag
                    if tag.endswith('}span') or tag == 'span':
                        spans.append(child)
            
            for span in spans:
                w_begin = span.get('begin') or span.get('{http://www.w3.org/ns/ttml}begin')
                w_end = span.get('end') or span.get('{http://www.w3.org/ns/ttml}end')
                w_text = "".join(span.itertext()).strip()
                if w_begin and w_text:
                    words.append(LyricWord(
                        begin_ms=parse_time_to_ms(w_begin),
                        end_ms=parse_time_to_ms(w_end) if w_end else parse_time_to_ms(w_begin) + 500,
                        text=w_text
                    ))
            
            # Fallback if no spans found
            if not words:
                words.append(LyricWord(begin_ms=begin_ms, end_ms=end_ms, text=text))
                
            lyrics.append(LyricLine(begin_ms=begin_ms, end_ms=end_ms, text=text, words=words))
            
    # Sort lyrics by begin time
    lyrics.sort(key=lambda x: x.begin_ms)
    return lyrics
