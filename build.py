import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

# Helper function to fetch a specific list of papers
def fetch_papers(query, sort_by="submittedDate", max_results=5):
    params = {
        "search_query": query, 
        "sortBy": sort_by,
        "sortOrder": "descending",
        "max_results": max_results
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"http://export.arxiv.org/api/query?{query_string}"
    
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read() 
            root = ET.fromstring(data)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            parsed_papers = []
            
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
                link = entry.find('atom:id', namespace).text
                
                authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
                author_string = ", ".join(authors) if authors else "Unknown"
                
                date_string = entry.find('atom:published', namespace).text[:10]
                summary = entry.find('atom:summary', namespace).text.replace('\n', ' ').strip()
                
                parsed_papers.append({
                    'title': title, 
                    'link': link,
                    'author': author_string,
                    'date': date_string,
                    'summary': summary
                })
                
            return parsed_papers
            
    except urllib.error.HTTPError as e:
        print(f"Crash details: HTTP {e.code} - {e.reason}")
        print(f"arXiv Server says: {e.read().decode('utf-8')}")
        raise 

# Function to build the HTML page
def generate_html(all_data):
    # Start the HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arXiv Tracker</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
            h1 {{ color: #222; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-top: 40px; }}
            h2 {{ color: #444; margin-top: 30px; }}
            .paper {{ margin-bottom: 25px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
            .paper h3 {{ margin: 0 0 10px 0; }}
            .paper a {{ color: #1a0dab; text-decoration: none; }}
            .paper a:hover {{ text-decoration: underline; }}
            .meta {{ color: #555; font-size: 0.9em; margin-bottom: 10px; }}
            .summary {{ font-size: 0.95em; line-height: 1.5; }}
            .timestamp {{ color: #666; font-style: italic; }}
        </style>
    </head>
    <body>
        <p class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    # Loop through Categories (CS, AI, Quantum)
    for category_name, sections in all_data.items():
        html_content += f"<h1>{category_name}</h1>"
        
        # Loop through Sections (Latest, Key Papers)
        for section_name, papers in sections.items():
            html_content += f"<h2>{section_name}</h2>"
            
            # Loop through individual papers
            for p in papers:
                html_content += f"""
                <div class="paper">
                    <h3><a href="{p['link']}" target="_blank">{p['title']}</a></h3>
                    <div class="meta">By {p['author']} • Published: {p['date']}</div>
                    <div class="summary">{p['summary'][:300]}... <a href="{p['link']}" target="_blank">Read more</a></div>
                </div>
                """

    # Close HTML document
    html_content += """
    </body>
    </html>
    """

    # Save to file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# --- MAIN SCRIPT EXECUTION ---
if __name__ == "__main__":
    
    # 1. Define the categories and fetch the data
    # We store everything in a nested dictionary
    print("Fetching papers...")
    
    tracker_data = {
        "Artificial Intelligence": {
            "Latest Updates": fetch_papers("cat:cs.AI", sort_by="submittedDate", max_results=5),
            "Key Foundational Papers": fetch_papers("cat:cs.AI", sort_by="relevance", max_results=20),
            "Papers from Top Authors": fetch_papers('cat:cs.AI AND (au:Bengio OR au:LeCun OR au:Hinton OR au:"Andrew Ng" OR au:"Sutskever" OR au:"Fei-Fei Li")', sort_by="submittedDate", max_results=10)
        },
        "Computer Science (General)": {
            "Latest Updates": fetch_papers("cat:cs.CR OR cat:cs.SE OR cat:cs.DS", sort_by="submittedDate", max_results=5),
            "Key Foundational Papers": fetch_papers("cat:cs.CR OR cat:cs.SE OR cat:cs.DS", sort_by="relevance", max_results=20)
        },
        "Quantum Physics": {
            "Latest Updates": fetch_papers("cat:quant-ph", sort_by="submittedDate", max_results=5),
            "Key Foundational Papers": fetch_papers("cat:quant-ph", sort_by="relevance", max_results=20),
            "Papers from Top Authors": fetch_papers('cat:quant-ph AND (au:Preskill OR au:Aaronson OR au:Shor, au: "M. Cerezo" AND "Barren Plateaus",
au: "Hsin-Yuan Huang" AND "Learning")', sort_by="submittedDate", max_results=10)
        }
    }
    
    # 2. Pass all that data to the HTML generator
    print("Generating HTML...")
    generate_html(tracker_data)
    print("Done! index.html created successfully.")
