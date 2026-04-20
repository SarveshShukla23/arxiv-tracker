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
    # CSS UI Variables and Google Fonts for a modern, professional look
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arXiv Research Tracker</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #f8fafc;
                --card-bg: #ffffff;
                --text-main: #1e293b;
                --text-muted: #64748b;
                --accent-primary: #2563eb;
                --accent-hover: #1d4ed8;
                --border-color: #e2e8f0;
            }}
            body {{ 
                font-family: 'Inter', -apple-system, sans-serif; 
                background-color: var(--bg-color); 
                color: var(--text-main); 
                line-height: 1.6; 
                margin: 0; 
                padding: 0; 
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 60px 20px; 
            }}
            header {{
                text-align: center;
                margin-bottom: 60px;
            }}
            header h1 {{
                font-size: 2.5em;
                color: #0f172a;
                margin-bottom: 12px;
                letter-spacing: -0.02em;
            }}
            .timestamp {{ 
                color: var(--text-muted); 
                font-size: 0.95em; 
                background: #f1f5f9;
                display: inline-block;
                padding: 6px 16px;
                border-radius: 20px;
                border: 1px solid var(--border-color);
            }}
            .category-section {{
                margin-bottom: 70px;
            }}
            h1.category-title {{ 
                color: #0f172a; 
                border-bottom: 2px solid var(--border-color); 
                padding-bottom: 12px; 
                margin-top: 0; 
                font-size: 2em; 
            }}
            h2.section-title {{ 
                color: var(--accent-primary); 
                margin-top: 40px; 
                margin-bottom: 24px;
                font-size: 1.2em; 
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 700;
            }}
            .paper-card {{ 
                background-color: var(--card-bg); 
                border: 1px solid var(--border-color);
                border-radius: 12px; 
                padding: 28px; 
                margin-bottom: 24px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease; 
            }}
            .paper-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
                border-color: #cbd5e1;
            }}
            .paper-title {{ 
                margin: 0 0 12px 0; 
                font-size: 1.4em; 
                line-height: 1.3;
            }}
            .paper-title a {{ 
                color: #0f172a; 
                text-decoration: none; 
            }}
            .paper-title a:hover {{ 
                color: var(--accent-primary); 
            }}
            .meta-info {{ 
                color: var(--text-muted); 
                font-size: 0.9em; 
                margin-bottom: 18px; 
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }}
            .meta-item {{
                display: flex;
                align-items: center;
            }}
            .summary {{ 
                color: #334155; 
                font-size: 1em; 
                margin-bottom: 20px;
            }}
            .read-more-btn {{
                display: inline-block;
                padding: 8px 16px;
                background-color: #eff6ff;
                color: var(--accent-primary);
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9em;
                border-radius: 6px;
                transition: background-color 0.2s ease, color 0.2s ease;
            }}
            .read-more-btn:hover {{
                background-color: var(--accent-primary);
                color: #ffffff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>arXiv Research Tracker</h1>
                <div class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </header>
    """

    # Loop through Categories (e.g., Artificial Intelligence, Computer Science)
    for category_name, sections in all_data.items():
        html_content += f"""
            <div class="category-section">
                <h1 class="category-title">{category_name}</h1>
        """
        
        # Loop through Sections (e.g., Latest Updates, Key Foundational Papers)
        for section_name, papers in sections.items():
            html_content += f'<h2 class="section-title">{section_name}</h2>'
            
            # Loop through individual papers to create the cards
            for p in papers:
                html_content += f"""
                <div class="paper-card">
                    <h3 class="paper-title"><a href="{p['link']}" target="_blank">{p['title']}</a></h3>
                    <div class="meta-info">
                        <span class="meta-item"><strong>Author(s):</strong>&nbsp;{p['author']}</span>
                        <span class="meta-item"><strong>Published:</strong>&nbsp;{p['date']}</span>
                    </div>
                    <div class="summary">{p['summary'][:350]}...</div>
                    <a href="{p['link']}" target="_blank" class="read-more-btn">Read Full Paper →</a>
                </div>
                """
        
        html_content += "</div>" # Close category-section div

    # Close HTML document
    html_content += """
        </div>
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
            "Key Foundational Papers": fetch_papers("cat:cs.AI", sort_by="relevance", max_results=10),
            "Papers from Top Authors": fetch_papers('cat:cs.AI AND (au:Bengio OR au:LeCun OR au:Hinton OR au:"Andrew Ng" OR au:"Sutskever" OR au:"Fei-Fei Li")', sort_by="submittedDate", max_results=10)
        },
        "Computer Science (General)": {
            "Latest Updates": fetch_papers("cat:cs.CR OR cat:cs.SE OR cat:cs.DS", sort_by="submittedDate", max_results=5),
            "Key Foundational Papers": fetch_papers("cat:cs.CR OR cat:cs.SE OR cat:cs.DS", sort_by="relevance", max_results=10)
        },
        "Quantum Physics": {
            "Latest Updates": fetch_papers("cat:quant-ph", sort_by="submittedDate", max_results=5),
            "Key Foundational Papers": fetch_papers("cat:quant-ph", sort_by="relevance", max_results=10),
            "Papers from Top Authors": fetch_papers('cat:quant-ph AND (au:Preskill OR au:Aaronson OR au:Shor, au: "M. Cerezo" AND "Barren Plateaus", au: "Hsin-Yuan Huang" AND "Learning")', sort_by="submittedDate", max_results=10)
        }
    }
    
    # 2. Pass all that data to the HTML generator
    print("Generating HTML...")
    generate_html(tracker_data)
    print("Done! index.html created successfully.")
