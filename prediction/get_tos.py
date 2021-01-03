import requests
from bs4 import BeautifulSoup, NavigableString
import re

INVALID_TAGS = ["script", "noscript", "img", "audio", "video"]

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
	soup = BeautifulSoup(content, 'lxml')
	# html_body = soup.find("body")

	# # remove unnecessary tags
	# html_tagless = strip_tags(str(html_body))

	# return html_tagless.prettify()
	raw_text = soup.get_text()
	cleaner_text = re.sub(r"\n+\s+", "\n", raw_text)
	
	return cleaner_text

# adapted from https://stackoverflow.com/a/3225671/12940893
def strip_tags(html_str):
    global INVALID_TAGS

    soup = BeautifulSoup(html_str, 'lxml')
    found_tags = set()

    for tag in soup.findAll(True):
        if tag.name in INVALID_TAGS:
        	tag.replaceWith("\n")
        	print("removed tag")
        else:
            innerhtml = ""
            found_tags.add(tag.name)

            for subtag in tag.contents:
                if not isinstance(subtag, NavigableString):
                	print("new subtag")
                	print(subtag.get_text()[:100])
                	raise IndexError
                	subtag = strip_tags(subtag.decode_contents())
                innerhtml += str(subtag)

            tag.replaceWith(innerhtml)

    print("Tags found:", *found_tags, sep="\n")
    return soup

if __name__ == "__main__":
    slug_to_url = {
        "twitter": [
            "https://twitter.com/en/tos",
            "https://twitter.com/en/privacy"
        ],
        "duckduckgo": [
            "https://duckduckgo.com/privacy"
        ]
    }

    for slug, urls in slug_to_url.items():
        try:
            agreements = ""
            for url in urls:
                agreements += tos_from_url(url)
            with open(f"../artifacts/tos/fromsite/{slug}.txt", 'w') as file_out:
                file_out.write(agreements)
        except Exception as e:
            print(e)
            continue