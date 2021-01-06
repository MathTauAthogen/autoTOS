import requests
from bs4 import BeautifulSoup
import re

def urls_from_text(text):
    """
    Return a list of URLs from a piece of text using RegEx
    """
    # https://stackoverflow.com/a/48769624/12940893 for regex
    url_regex = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"
    return re.findall(url_regex, text)

def tos_from_url(url):
    """
    Return a string of HTML from a URL for
    a Terms of Service agreement. Removes unnecessary tags.

    Arguments:
    url: a string to a valid TOS page

    Returns:
    string: the TOS content.
    """
    content = requests.get(url).content
    soup = BeautifulSoup(content, "lxml")

    # clean up text in the HTML
    raw_text = soup.get_text()
    cleaner_text = re.sub(r"\n+\s+", "\n", raw_text)

    return cleaner_text

def all_tos_from_text_input(text):
    """
    Take a text input (as a list of URLs)
    and return the agreements found on those links
    
    """
    urls = urls_from_text(text)
    agreements = ""

    for url in urls:
        try:
            agreements += tos_from_url(url)
        except Exception as e:
            print(e)
            continue

    return agreements

if __name__ == "__main__":
    slug_to_url = {
        "twitter": ["https://twitter.com/en/tos", "https://twitter.com/en/privacy"],
        "duckduckgo": ["https://duckduckgo.com/privacy"],
    }

    for slug, urls in slug_to_url.items():
        try:
            agreements = ""
            for url in urls:
                agreements += tos_from_url(url)
            with open(f"../artifacts/tos/fromsite/{slug}.txt", "w") as file_out:
                file_out.write(agreements)
        except Exception as e:
            print(e)
            continue
