from datetime import datetime, timezone
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from playwright.sync_api import sync_playwright

def build_rss_feed():
    site_url = "https://www.empireonline.com/movies/reviews/"
    
    # Launch a headless Chrome instance to pass Cloudflare and render Next.js
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            page.goto(site_url, wait_until="networkidle", timeout=30000)
            html_content = page.content()
        except Exception as e:
            print(f"Error fetching page: {e}")
            browser.close()
            return
        browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=site_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")
    fg.language("en")
    fg.updated(datetime.now(timezone.utc))

    seen_links = set()

    # Locate review links dynamically rendered by JavaScript
    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]
        
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            title_tag = link_tag.find(["h2", "h3", "h4", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            # Find parent article/div wrapper to pull summary text
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
