import requests
import lxml
from bs4 import BeautifulSoup


def get_point_text(point_id):
    """
    Given a point id (for ToS;DR),
    Search that point and return the 
    TOS snippet from there
    Arguments:
    point_id: string or integer
    Returns:
    string: TOS text
    """
    content = requests.get(f"https://edit.tosdr.org/points/{point_id}").content
    soup = BeautifulSoup(content, "lxml")

    if (
        b"Oops! It looks like you're doing many different things in a short period of time. We check for this to prevent abusive requests or other types of vandalism to our site. Please try again in 10 minutes."
        == content
    ):
        raise Exception(b"Please try again in 10 minutes")

    quote = soup.find("blockquote")

    if quote is None:
        quote = soup.select_one("div.container div.row div.col-sm-10")
        if quote is None:
            print(content)
        else:
            return str(quote)

    for tag in quote.findAll(True):
        if tag.name == "footer":
            tag.extract()

    return quote.get_text().strip()


if __name__ == "__main__":
    print(get_point_text("5309"))
