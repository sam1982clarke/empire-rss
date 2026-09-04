import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def build_rss_feed():
    site_url = "https://www.empireonline.com/movies/reviews/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    fg = FeedGenerator()
    fg.title("Empire Online - Movie Reviews")
    fg.link(href=site_url, rel="alternate")
    fg.description("Latest movie reviews from Empire Online")

    for article in soup.find_all("article")[:15]:
        title_tag = article.find(["h2", "h3", "h4"])
        link_tag = article.find("a", href=True)

        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag["href"]
            if not link.startswith("http"):
                link = f"https://www.empireonline.com{link}"

            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.guid(link)

    fg.rss_file("empire_reviews.xml")
    print("Successfully generated empire_reviews.xml")

if __name__ == "__main__":
    build_rss_feed()
