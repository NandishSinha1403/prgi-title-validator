import re
import json
import os

def extract_titles_from_xls(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read().decode('latin-1', errors='ignore')
        
        # Log basic info
        print(f"File: {os.path.basename(filepath)}, size: {len(data)}")
        
        # Use split on <tr> in case </tr> is missing (common in some exports)
        # or use findall with re.IGNORECASE
        rows = re.split(r'<(?:tr|TR).*?>', data, flags=re.DOTALL)
        
        print(f"Found {len(rows)} split segments in {os.path.basename(filepath)}")
        
        titles = []
        for row in rows[1:]: # Skip headers if they are in the first tr
            cells = re.findall(r'<(?:td|TD).*?>(.*?)</(?:td|TD)>', row, re.DOTALL)
            if len(cells) >= 2:
                # Group 1 is the second cell (index 1) which usually contains the title
                title = re.sub(r'<.*?>', '', cells[1]).strip()
                if title and len(title) > 2:
                    titles.append(title.upper())
        
        print(f"Extracted {len(titles)} titles from {os.path.basename(filepath)}")
        return titles
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []

def main():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    files = [
        "TestExcel.xls", "TestExcel(1).xls", "TestExcel(2).xls",
        "TestExcel(3).xls", "TestExcel(4).xls", "TestExcel(5).xls"
    ]
    
    all_titles = set()
    for filename in files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}...")
            titles = extract_titles_from_xls(filepath)
            all_titles.update(titles)
        else:
            print(f"File not found: {filename}")
            
    output_path = os.path.join(data_dir, 'titles_database.json')
    titles_list = sorted(list(all_titles))
    
    with open(output_path, 'w') as f:
        json.dump(titles_list, f, indent=2)
        
    print(f"Total unique titles extracted: {len(titles_list)}")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()