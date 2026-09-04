from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def build_rss_feed():
    API_KEY = "48071fd1f9e47992b42d1af6dcc9e7c9"  # Keep your key inside quotes
    target_url = "https://www.empireonline.com/movies/reviews/"
    
    # render=true forces ScraperAPI to launch a real browser to run Next.js scripts
    # keep_headers=true and premium=true bypass strict Cloudflare/DataDome blocks
    scraper_url = "http://api.scraperapi.com"
    params = {
        "api_key": API_KEY,
        "url": target_url,
        "render": "true",
        "premium": "true"
    }

    try:
        response = requests.get(scraper_url, params=params, timeout=120)
        if response.status_code != 200:
            print(f"ScraperAPI HTTP Error: {response.status_code}")
            return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=target_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")
    fg.language("en")
    fg.updated(datetime.now(timezone.utc))

    seen_links = set()

    # Find rendered anchor tags containing review links
    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]
        
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            # Target heading tags rendered inside the link or parent container
            title_tag = link_tag.find(["h2", "h3", "h4", "p", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            # Target summary text rendered by JavaScript
            parent = link_tag.find_parent(["article", "div", "li"])
            desc_tag = parent.find("p") if parent else None
            desc_text = desc_tag.get_text(strip=True) if desc_tag else "Read the full review on Empire Online."

            if len(title_text) > 6:
                link = href if href.startswith("http") else f"https://www.empireonline.com{href}"
                
                if link not in seen_links:
                    seen_links.add(link)
                    fe = fg.add_entry()
                    fe.title(title_text)
                    fe.link(href=link)
                    fe.description(desc_text)
                    fe.guid(link, permalink=True)
                    fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file("empire_reviews.xml")
    print(f"Successfully processed {len(seen_links)} items.")

if __name__ == "__main__":
    build_rss_feed()
