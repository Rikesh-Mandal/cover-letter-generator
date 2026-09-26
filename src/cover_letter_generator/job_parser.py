from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def is_valid_url(url: str) -> bool: #:str indicates the argument type is string and bool indicates this func returns boolean
    try:
        result = urlparse(url)
        return (result.scheme in {"http", "https"} and bool(result.netloc))
    except ValueError:
        return False


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    if not is_valid_url(url):
        return ("Invalid URL!")
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if not soup.body:
        text = ""
    else:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    return title + "\n\n" + text


def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    if not is_valid_url(url):
        return ("Invalid URL!")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]
