import requests
import lxml
from bs4 import BeautifulSoup

def get_point_text(point_id):

	content = requests.get(f"https://edit.tosdr.org/points/{point_id}").content
	soup = BeautifulSoup(content, "lxml")
	
	quote = soup.find("blockquote")
	
	for tag in quote.findAll(True):
		if tag.name == "footer":
			tag.extract()

	return quote.get_text().strip()

if __name__ == "__main__":
	get_point_text("5309")