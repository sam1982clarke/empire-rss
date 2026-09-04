from datetime import datetime, timezone
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

    # Locate article containers directly to grab both title, link, and summary text
    articles = soup.find_all(["article", "div"], class_=lambda c: c and ("card" in c or "item" in c or "article" in c))
    
    # Fallback to general links if containers aren't explicitly class-tagged
    if not articles:
        articles = soup.find_all("a", href=True)

    for article in articles:
        # Resolve target link
        link_tag = article if article.name == "a" else article.find("a", href=True)
        if not link_tag or not link_tag.get("href"):
            continue
            
        href = link_tag["href"]
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            # Extract Title
            title_tag = article.find(["h2", "h3", "h4"]) or link_tag.find(["h2", "h3", "h4", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            # Extract Description / Standfirst Text
            desc_tag = article.find(["p", "div"], class_=lambda c: c and ("description" in c or "dek" in c or "summary" in c or "standfirst" in c))
            if not desc_tag:
                desc_tag = article.find("p")
            
            desc_text = desc_tag.get_text(strip=True) if desc_tag else "Read the full review on Empire Online."

            if len(title_text) > 5:
                link = href if href.startswith("http") else f"https://www.empireonline.com{href}"
                
                if link not in seen_links:
                    seen_links.add(link)
                    
                    fe = fg.add_entry()
                    fe.title(title_text)
                    fe.link(href=link)
                    fe.description(desc_text)  # Populates [no content] in Feedly
                    fe.guid(link, permalink=True)
                    fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file("empire_reviews.xml")

if __name__ == "__main__":
    build_rss_feed()
