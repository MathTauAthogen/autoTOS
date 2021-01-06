# retrieve full TOS texts from a point ID
#
# usage example:
#   texts = fulltext('6723')
#   for text in texts:
#     print(texts)
#
# `texts` should now be an array containing all of the document texts
# from 1Password (which has a point with ID 6723)
#
# the script requires some authentication information in order to access
# the tosdr annotation page---this is provided in the `cookies.config`
# file, where:
#   1. the first line is the value of the _phoenix_session cookie
#   2. the second line is the value of the remember_user_token cookie
# you can find these cookie values by looking them up in your browser
# after logging in

from bs4 import BeautifulSoup
import requests
import re

# we will pre-compile some regexes and authentication data to speed up
# the process
match_service_id = re.compile(r"/services/(\d+)")
match_doc_id = re.compile(r"doc_\d+")
with open("../config/cookies.config", "r") as auth_data:
    session, user = map(lambda s: s.strip(), auth_data.readlines())
    cookies = {"_phoenix_session": session, "remember_user_token": user}

# get service ID from a point ID by scraping the discussion document
def get_service_id(point_id):
    discussion_url = "https://edit.tosdr.org/points/%s" % point_id
    discussion_doc = requests.get(discussion_url)
    soup = BeautifulSoup(discussion_doc.text, "lxml")
    for link in soup.find_all("a"):
        href = link.get("href")
        if "services" in href:
            return match_service_id.search(href).group(1)


# get the text from a 'document' div on a service annotation page
def get_document_text(document_div):
    return document_div.find(class_="documentContent").get("data-content")


# get full text from a point ID
def fulltext(point_id):

    service_id = get_service_id(point_id)

    url = "https://edit.tosdr.org/services/%s/annotate" % service_id
    doc = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(doc.text, "lxml")
    divs = soup.find_all(id=match_doc_id)
    return list(map(get_document_text, divs))
