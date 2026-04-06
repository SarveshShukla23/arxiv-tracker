# arxiv-tracker
arxiv-tracker

An automated data pipeline that fetches, parses, and curates research papers from the [arXiv API](https://arxiv.org/), generating a static HTML dashboard of the latest academic developments. 

This project is built to run entirely without external dependencies and is fully automated via GitHub Actions.

## 🚀 Features
* **Automated Data Pipeline:** Runs on a scheduled GitHub Actions workflow to fetch the most up-to-date research without manual intervention.
* **Multi-Disciplinary Tracking:** Currently configured to track categories such as Artificial Intelligence, General Computer Science, and Quantum Physics.
* **Smart Curation:** For each category, the tracker extracts:
  * **Latest Updates:** The 5 most recently submitted papers.
  * **Key Foundational Papers:** The top 20 papers sorted by historical relevance to the field.
* **Zero-Dependency Python:** Built exclusively using Python's standard library (`urllib`, `xml.etree.ElementTree`) to ensure a lightweight, secure, and easily maintainable codebase.
* **Static Site Generation:** Dynamically builds an `index.html` file that neatly formats titles, authors, publication dates, and summaries with direct links to the original papers.

## 🛠️ How it Works
1. `build.py` constructs safely encoded API requests and queries the arXiv Atom feed.
2. The raw XML response is parsed to extract key metadata (Title, Author(s), Date, Summary, Link).
3. The extracted data is injected into a responsive HTML template.
4. GitHub Actions automatically commits the new `index.html` and deploys the updated dashboard.
