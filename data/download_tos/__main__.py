import json
import pandas as pd
import re
import time

from point_text import get_point_text
from fulltext import fulltext

with open("../../artifacts/all.json", "r") as file:
    full_dataset = json.load(file)

classes = pd.DataFrame(columns=["class_id", "title", "topic", "effect", "weight"])
num_passed = 0

labeled_excerpts = pd.DataFrame(columns=["class_id", "slug", "excerpt"])

success_excerpts = 0
failed_excerpts = 0


def remove_html_tags(html_str):
    return re.sub(r"\<[^)]*?\>", "", html_str)


def iterate_through_points(points_dict, slug):
    global classes, labeled_excerpts, success_excerpts, failed_excerpts

    points_df = pd.DataFrame()

    for i, point in enumerate(comp_data["points"]):
        title = point["title"]

        # create case if it doesn't exist
        if not any(classes["title"].isin([title])):
            case_data = {
                "class_id": classes.shape[0],
                "title": title,
                "topic": None,
                "effect": point["point"],
                "weight": int(point["score"]),
            }
            classes = classes.append(case_data, ignore_index=True)

        class_id = int(classes.loc[classes["title"] == title, "class_id"])

        try:
            excerpt = remove_html_tags(get_point_text(point["id"]))
            success_excerpts += 1
            if success_excerpts % 100 == 0:
                print(f"success_excerpts: {success_excerpts}")
        except Exception as e:
            if "Please try again in 10 minutes" in str(e):
                print("Wait 10 minutes")
                time.sleep(60 * 10 + 3)
            excerpt = remove_html_tags(get_point_text(point["id"]))
            success_excerpts += 1
            if success_excerpts % 100 == 0:
                print(f"success_excerpts: {success_excerpts}")
        except Exception as e:
            print(
                f"Error receiving excerpt at https://edit.tosdr.org/points/{point['id']}"
            )
            print(e)
            failed_excerpts += 1
            continue

        excerpt = excerpt.replace("\n", " ")
        excerpt_data = {"excerpt": excerpt, "class_id": class_id, "slug": slug}
        labeled_excerpts = labeled_excerpts.append(excerpt_data, ignore_index=True)


# iterate over companies
for comp_name, comp_data in full_dataset.items():
    print("Name:\t", comp_name)

    # filter out metadata
    if comp_name in ("tosdr/api/version", "tosdr/data/version"):
        continue

    # filter out repeat company names
    comp_keys = comp_data.keys()
    if "slug" not in comp_keys:
        continue

    # iterate through points for each company
    if "points" in comp_keys:
        iterate_through_points(comp_data["points"], comp_data["slug"])

    # download company tos information
    if (
        "documents" in comp_keys
        and "points" in comp_keys
        and len(comp_data["documents"]) > 0
    ):
        if len(comp_data["points"]) > 0:

            all_texts = remove_html_tags(
                " ".join(fulltext(comp_data["points"][0]["id"]))
            )

            with open(f"tos/{comp_data['slug']}.txt", "w") as file:
                file.write(all_texts)

    num_passed += 1

print(f"Success Ratio:{success_excerpts}/{success_excerpts+failed_excerpts}")

labeled_excerpts.to_csv("labeled_excerpts.csv", index=False)

classes["frequency"] = labeled_excerpts.groupby("class_id")["excerpt"].count()
classes.to_csv("classes.csv", index=False)
