import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# arXiv API URL for cs.AI, quant-ph, and general cs
# Sorting by submittedDate, descending. Grabbing top 20.
URL = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:quant-ph+OR+cat:cs.*&sortBy=submittedDate&sortOrder=desc&max_results=20'

def fetch_papers():
    response = urllib.request.urlopen(URL).read()
    root = ET.fromstring(response)
    
    # arXiv XML uses namespaces
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.replace('\n', ' ')
        link = entry.find('atom:id', ns).text
        published = entry.find('atom:published', ns).text[:10]
        
        # Grab primary author
        author = entry.find('atom:author/atom:name', ns).text
        
        papers.append({
            'title': title, 'author': author, 'summary': summary, 
            'link': link, 'date': published
        })
    return papers

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
