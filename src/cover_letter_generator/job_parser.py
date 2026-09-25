from trafilatura import fetch_url, extract
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool: #:str indicates the argument passed should be a string and bool indicates this func returns boolean
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extractUrl(url):
    if not is_valid_url(url):
        return "Please enter a valid URL."
    pageContent = fetch_url(url)
    return extract(pageContent, output_format="json", with_metadata=True)

print(extractUrl("https://ornate-torte-03c391.netlify.app/"))