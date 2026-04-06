import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

# arXiv API URL for cs.AI, quant-ph, and general cs
# Sorting by submittedDate, descending. Grabbing top 20.
URL = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:quant-ph+OR+cat:cs.*&sortBy=submittedDate&sortOrder=desc&max_results=20'

def fetch_papers():
    params = {
        "search_query": "cat:cs.AI OR cat:cs.LG", 
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 10
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
            
            # Parse the XML
            root = ET.fromstring(data)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            parsed_papers = []
            
            # Extract title, link, author, and date for each paper
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
                link = entry.find('atom:id', namespace).text
                
                # --- NEW: Extract Authors ---
                # A paper can have multiple authors, so we find all of them and join with commas
                authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
                author_string = ", ".join(authors) if authors else "Unknown"
                
                # --- NEW: Extract Date ---
                # arXiv returns dates like "2026-04-05T18:00:00Z". The [:10] slices it to just "2026-04-05"
                date_string = entry.find('atom:published', namespace).text[:10]
                
                # Now we pass all four pieces of data to your HTML generator!
                parsed_papers.append({
                    'title': title, 
                    'link': link,
                    'author': author_string,
                    'date': date_string
                })
                
            return parsed_papers
            
    except urllib.error.HTTPError as e:
        print(f"Crash details: HTTP {e.code} - {e.reason}")
        print(f"arXiv Server says: {e.read().decode('utf-8')}")
        raise
def generate_html(papers):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily arXiv: AI, CS & Quantum</title>
        <style>
            body {{ font-family: system-ui, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
            .paper {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
            h2 {{ margin-bottom: 5px; color: #1a0dab; }}
            a {{ text-decoration: none; color: inherit; }}
            a:hover {{ text-decoration: underline; }}
            .meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
            .summary {{ background: #f9f9f9; padding: 15px; border-left: 4px solid #ccc; }}
        </style>
    </head>
    <body>
        <h1>Latest arXiv Updates</h1>
        <p><em>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</em></p>
    """
    
    for p in papers:
        html_content += f"""
        <div class="paper">
            <h2><a href="{p['link']}" target="_blank">{p['title']}</a></h2>
            <div class="meta">By {p['author']} • Published: {p['date']}</div>
            <div class="summary">{p['summary'][:300]}... <a href="{p['link']}" target="_blank" style="color:#1a0dab;">Read more</a></div>
        </div>
        """
        
    html_content += "</body></html>"
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    papers = fetch_papers()
    generate_html(papers)
    print("Successfully generated index.html")
