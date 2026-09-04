from datetime import datetime, timezone
import json
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def build_rss_feed():
    site_url = "https://www.empireonline.com/movies/reviews/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=site_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")
    fg.language("en")
    fg.updated(datetime.now(timezone.utc))

    seen_links = set()

    # Locate Next.js raw data payload
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    
    if next_data_tag and next_data_tag.string:
        try:
            payload = json.loads(next_data_tag.string)
            # Drill into Next.js prop structure to pull article objects
            props = payload.get("props", {}).get("pageProps", {})
            
            # Find list of content items regardless of key naming
            content_list = []
            for key in ["content", "articles", "items", "latest"]:
                if key in props and isinstance(props[key], list):
                    content_list = props[key]
                    break
            
            # Fallback search if nested under page data
            if not content_list and "data" in props:
                content_data = props["data"]
                if isinstance(content_data, dict):
                    content_list = content_data.get("content", []) or content_data.get("articles", [])

            for item in content_list:
                if not isinstance(item, dict):
                    continue
                    
                title = item.get("title") or item.get("headline") or item.get("name")
                summary = item.get("dek") or item.get("summary") or item.get("description") or item.get("standfirst") or "Read the full review on Empire Online."
                url_path = item.get("canonicalUrl") or item.get("url") or item.get("slug")
                
                if title and url_path:
                    link = url_path if url_path.startswith("http") else f"https://www.empireonline.com{url_path}"
                    
                    if "/movies/reviews/" in link and link not in seen_links:
                        seen_links.add(link)
                        
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=link)
                        fe.description(summary)
                        fe.guid(link, permalink=True)
                        fe.pubDate(datetime.now(timezone.utc))
        except Exception as e:
            print(f"JSON extraction failed: {e}")

    fg.rss_file("empire_reviews.xml")

if __name__ == "__main__":
    build_rss_feed()
