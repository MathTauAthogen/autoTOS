import os
import json
import glob

from predictor import Predictor
from get_tos import tos_from_url

def parse_tos_from_urls():
	with open("tos_urls.json", "r") as infile:
		tos_urls = json.load(infile)

	predictor = Predictor("../nlp/checkpoints/model.ckpt")

	for slug, urls in tos_urls.items():
		print(f"Parsing {slug} TOS")
		if os.path.isfile(f"../artifacts/eval/fromsite/{slug}.json"):
			print("skipped (file exists)")
			continue

		try:
			# capture text for agreements
			agreements = ""
			for url in urls:
				agreements += tos_from_url(url)
			with open(f"../artifacts/tos/fromsite/{slug}.txt", "w") as outfile:
				outfile.write(agreements)

			# get TOS prediction
			tos_eval = predictor.predict(agreements)

			with open(f"../artifacts/eval/fromsite/{slug}.json", "w") as outfile:
				json.dump(tos_eval, outfile, indent=4)

		except Exception as e:
			print(e)
			continue

def parse_tos_from_text():
	predictor = Predictor("../nlp/checkpoints/model.ckpt")

	for textfile in glob.glob("../artifacts/tos/*.txt"):
		try:
			slug = os.path.basename(textfile)[:-4]
			print(f"Parsing {slug} TOS")
			
			with open(textfile, "r") as infile:
				tos_text = infile.read()
			if not tos_text:
				continue
			
			tos_eval = predictor.predict(tos_text)

			if not tos_eval["predictions"]:
				print("No predictions")
				continue

			with open(f"../artifacts/eval/fromtext/{slug}.json", "w") as outfile:
				json.dump(tos_eval, outfile, indent=4)

		except Exception as e:
			print(e)
			continue

if __name__ == "__main__":
	pass
	# parse_tos_from_text()