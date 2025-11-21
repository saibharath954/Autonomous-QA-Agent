from bs4 import BeautifulSoup

def parse_html(raw_html: str):
    soup = BeautifulSoup(raw_html, "html.parser")
    # Extract visible text
    text = soup.get_text(separator="\n", strip=True)
    return text
