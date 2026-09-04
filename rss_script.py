from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def build_rss_feed():
    site_url = "https://www.empireonline.com/movies/reviews/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=site_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")

    # Add feed-level language and updated date for RSS compliance
    fg.language("en")
    fg.updated(datetime.now(timezone.utc))

    seen_links = set()

    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]
        
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            title_tag = link_tag.find(["h2", "h3", "h4", "p", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            if len(title_text) > 8 and ("Review" in title_text or len(title_text) > 15):
                link = href if href.startswith("http") else f"https://www.empireonline.com{href}"
                
                # Prevent duplicate entries
                if link not in seen_links:
                    seen_links.add(link)
                    
                    fe = fg.add_entry()
                    fe.title(title_text)
                    fe.link(href=link)
                    # Unique permalink identifier required by Feedly
                    fe.guid(link, permalink=True)
                    # Feed date
                    fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file("empire_reviews.xml")

if __name__ == "__main__":
    build_rss_feed()
