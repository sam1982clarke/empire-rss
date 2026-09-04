from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def build_rss_feed():
    # Insert your free ScraperAPI key here
    API_KEY = "48071fd1f9e47992b42d1af6dcc9e7c9"
    target_url = "https://www.empireonline.com/movies/reviews/"
    
    # ScraperAPI routes the request through real residential proxies to bypass Cloudflare
    scraper_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={target_url}&render=true"

    try:
        response = requests.get(scraper_url, timeout=60)
        if response.status_code != 200:
            print(f"ScraperAPI Error: {response.status_code}")
            return
    except Exception as e:
        print(f"Request failed: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=target_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")
    fg.language("en")
    fg.updated(datetime.now(timezone.utc))

    seen_links = set()

    # Parse review links and descriptions
    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]
        
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            title_tag = link_tag.find(["h2", "h3", "h4", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            parent = link_tag.find_parent(["article", "div"])
            desc_tag = parent.find("p") if parent else None
            desc_text = desc_tag.get_text(strip=True) if desc_tag else "Read the full review on Empire Online."

            if len(title_text) > 5 and ("Review" in title_text or len(title_text) > 12):
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

if __name__ == "__main__":
    build_rss_feed()
