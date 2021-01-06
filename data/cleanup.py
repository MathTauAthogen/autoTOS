# Cleans up the data! See the Google Doc (https://docs.google.com/document/d/1Vjsw9VIRL8PDP4b7krbxwE0MRT4YMP06uGuQVYCLXdo/edit)
# Puts it in the "Model Data" format
#
#
# TODO list:
# 1. Loop over all sites

import pandas as pd
import json
import string

# Function removerange
# Inputs: first_index, the first index of the substring;
#   last_index, the last index of the substring;
#   lens, an array of the current indices of the tokens;
#   labels, a current list of all of the info about the tokens.
# Output: A new lens and labels list,
#   where lens has the combined token size
#   and labels has all of the data about the token.
def removerange(first_index, last_index, lens, labels, substitute):
    sub, sub2 = substitute
    c = []
    inb = True
    for i in range(len(lens)):
        if inb and lens[i] > first_index:
            inb = False
            c += [i]
        if (not inb) and lens[i] > last_index:
            c += [i]
            break
    assert c[0] >= 1
    return [
        lens[: c[0]] + lens[c[1] :],
        labels[: c[0] - 1] + [(sub, sub2, first_index, last_index)] + labels[c[1] :],
    ]


###############################################################################################################

# Initialize the Labelled Excerpts Data Table

df = pd.read_csv("../artifacts/labeled_excerpts.csv")

c = []

borked = []

sluglist = list(df.slug.unique())
with open("../artifacts/exclude.txt") as f:
    for a in f.read().splitlines():
        for i, v in enumerate(sluglist):
            if a == v:
                sluglist.pop(i)

###############################################################################################################
for b in sluglist:
    borkedq = False
    sitedf = df[df["slug"] == b]
    full = ""  # The full text of the TOS of the site

    with open("../artifacts/tos/" + b + ".txt", "r") as g:
        full = g.read()  # Get the full text
        printable = set(string.printable)
        full = "".join(filter(lambda x: x in printable, full))
        tokenlistb = full.splitlines()  # Get a list of sentences
        tokenlistb = [i.strip(" ").strip(".") for i in tokenlistb]
        lens = [
            sum(map(len, tokenlistb[:i])) + i for i in range(len(tokenlistb) + 2)
        ]  # Find the starting index of each sentences

        full = " ".join(tokenlistb)  # Put the full text on only one line.

    labels = [
        ("", "", "", "") for i in range(len(tokenlistb))
    ]  # Initialize something containing inner tuples that can be indexed to the same amount as the other values
    print(tokenlistb)

    # sub = label, iterate over all
    # sub2 = its class_id

    badlines = []

    for i, row in sitedf.iterrows():
        sub = (
            " ".join(" ".join(str(row["excerpt"]).split("\n")).split(". "))
            .strip(" ")
            .strip(".")
        )
        printable = set(string.printable)
        sub = "".join(filter(lambda x: x in printable, sub))
        sub2 = row["class_id"]
        try:
            ind = full.index(sub)
            lens, labels = removerange(ind, ind + len(sub), lens, labels, (sub, sub2))
        except:
            badlines += [(sub, sub2)]

    if borkedq:
        continue

    # And finish it off
    dff = [
        {
            "token": full[lens[i] : lens[i + 1] - 1],
            "labels": [
                {
                    "text": labels[i][0],
                    "start": labels[i][2] - lens[i],
                    "end": labels[i][3] - lens[i],
                    "class_id": labels[i][1],
                }
                for j in range(i, i + 1)
                if labels[j] != ("", "", "", "")
            ],
        }
        for i in range(len(labels))
    ]
    dfb = [
        {
            "token": badlines[i][0],
            "labels": [
                {
                    "text": badlines[i][0],
                    "start": 0,
                    "end": len(badlines[i][0]),
                    "class_id": badlines[i][1],
                }
            ],
        }
        for i in range(len(badlines))
    ]
    c += dfb
    c += dff
    # print(json.dumps(dff))
print("Finale:")
with open("../artifacts/annotated_sentences.json", "w") as fp:
    json.dump(c, fp)
print("Borked:")
print(borked)
