# ThreatDigest Hub

ThreatDigest Hub is a scalable, AI-enhanced cyber threat intelligence aggregator. It collects, enriches, and classifies global cybersecurity incidents from curated RSS feeds, scraping article content and tagging each entry with structured threat metadata.

## Features
- Aggregates global and regional cyber news feeds
- Scrapes and parses full article content
- Classifies incidents using GPT (threat type, CVEs, geo, actor, etc.)
- Outputs enhanced RSS feeds and Markdown summaries

## Setup

```bash
git clone https://github.com/YOUR_ORG/threatdigest-hub
cd threatdigest-hub
pip install -r requirements.txt
cp .env.example .env
python app/threatdigest_main.py
```
