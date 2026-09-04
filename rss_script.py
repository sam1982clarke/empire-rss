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
        print(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=site_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")

    items_found = False

    # Extract all links containing "/movies/reviews/" in their URL
    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]
        
        # Look for links targeting specific movie reviews
        if "/movies/reviews/" in href and href != "/movies/reviews/":
            # Pull text from inside headings or span tags within the link
            title_tag = link_tag.find(["h2", "h3", "h4", "p", "span"])
            title_text = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            
            # Clean up text and ensure it's not an empty link or navigation label
            if len(title_text) > 8 and "Review" in title_text or len(title_text) > 15:
                link = href if href.startswith("http") else f"https://www.empireonline.com{href}"
                
                fe = fg.add_entry()
                fe.title(title_text)
                fe.link(href=link)
                fe.guid(link)
                items_found = True

    fg.rss_file("empire_reviews.xml")
    print(f"Successfully generated empire_reviews.xml (Found items: {items_found})")

if __name__ == "__main__":
    build_rss_feed()
