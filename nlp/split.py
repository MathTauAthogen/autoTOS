import json
import random
import numpy as np
import sys

TRAIN_PROP = 0.8


def sort_list_dict(freq, desc=False):
    return dict(sorted(freq.items(), key=lambda item: len(item[1]), reverse=desc))


def multi_argmax(arr):
    return [i for i, x in enumerate(arr) if x == np.max(arr)]


def iterative_stratification(tokens, proportions, lookup):
    unlabeled = list()
    remaining = dict()

    # Build the list of tokens per label that have not
    # been allocated to a subset yet
    for token, class_list in dict(tokens).items():
        if len(class_list) == 0:
            unlabeled.append(lookup[token])
            del tokens[token]
            continue
        for c in class_list:
            if c not in remaining.keys():
                remaining[c] = set()
            remaining[c].add(token)

    desired = [dict() for _ in range(len(proportions))]
    subsets = [list() for _ in range(len(proportions))]

    # Compute the desired number of examples for each label,
    # for each subset
    for c, labeled_tokens in remaining.items():
        for i, weight in enumerate(proportions):
            desired[i][c] = round(len(labeled_tokens) * weight)

    while len(tokens.keys()) > 0:
        # Allocate the least frequent label (with at least
        # 1 example remaining) first
        remaining = sort_list_dict(remaining)
        least_freq_label = list(remaining.keys())[0]

        label_tokens = list(remaining[least_freq_label])
        random.shuffle(label_tokens)

        for img in label_tokens:
            # Allocate image to subset that needs the most of that label
            label_counts = [lab[least_freq_label] for lab in desired]
            subset_indexes = multi_argmax(label_counts)

            if len(subset_indexes) > 1:
                # Break ties by subset that needs the most overall examples
                all_label_counts = [sum(desired[i].values()) for i in subset_indexes]

                subset_indexes = [
                    subset_indexes[x] for x in multi_argmax(all_label_counts)
                ]
                if len(subset_indexes) > 1:
                    # Break further ties randomly
                    random.shuffle(subset_indexes)

            # Add image to the chosen subset and remove the image
            idx = subset_indexes[0]
            subset = subsets[idx]
            subset.append(lookup[img])

            for img_set in remaining.values():
                if img in img_set:
                    img_set.remove(img)

            # Decrease the desired number, based on all labels in that example
            for c in tokens[img]:
                desired[idx][c] -= 1

            tokens.pop(img)
        remaining.pop(least_freq_label)

    return subsets, unlabeled


def preprocess_labels(data, filter_with_map=True):
    # This modifies class ids based on the mapping in classes.json,
    # removing all of the ids that aren't part of the predefined set
    id_mapping = dict()
    with open("../config/mapped_classes.json", "r") as mapping:
        mapping_json = json.loads(mapping.read())
    for entry in mapping_json:
        for i in entry["old_ids"]:
            id_mapping[i] = entry["id"]

    for token in data:
        for i, label in enumerate(list(token["labels"])):
            if len(label["text"].strip()) == 0:
                del token["labels"][i]
                continue

            if label["text"] != token["token"][label["start"] : label["end"]]:
                if label["text"] == token["token"][label["start"] : label["end"] + 1]:
                    token["labels"][i]["end"] += 1
                elif len(token["token"]) < label["end"]:
                    len_diff = label["end"] - len(token["token"])
                    add_on_str = label["text"][-len_diff:]
                    token["token"] += add_on_str
                else:
                    text_stream.write(label["text"] + "\n")
                    label_stream.write(
                        token["token"][label["start"] : label["end"]] + "\n"
                    )
                    del token["labels"][i]
                    continue

            if filter_with_map:
                if label["class_id"] not in id_mapping.keys():
                    del token["labels"][i]
                    continue
                else:
                    token["labels"][i]["class_id"] = str(id_mapping[label["class_id"]])

            else:
                token["labels"][i]["class_id"] = str(label["class_id"])
    text_stream.close()
    label_stream.close()


def print_freq_dict(data):
    freq_dict = dict()
    for token in data:
        for label in token["labels"]:
            if label["class_id"] in freq_dict.keys():
                freq_dict[label["class_id"]] += 1
            else:
                freq_dict[label["class_id"]] = 1
    freq_dict = dict(sorted(freq_dict.items(), key=lambda x: x[1]))
    print(freq_dict, sum(freq_dict.values()))


if __name__ == "__main__":
    fname = (
        sys.argv[1] if len(sys.argv) > 1 else "../artifacts/annotated_sentences.json"
    )
    with open(fname, "r") as f:
        data = json.loads(f.read())

    preprocess_labels(data)

    cleaned_data = {d["token"]: [lab["class_id"] for lab in d["labels"]] for d in data}
    lookup = {d["token"]: d for d in data}

    (train_set, test_set), unlabeled = iterative_stratification(
        cleaned_data, [TRAIN_PROP, 1 - TRAIN_PROP], lookup
    )

    print_freq_dict(train_set)
    with open("outputs/train_filter.json", "w+") as out:
        out.write(json.dumps(train_set + unlabeled))
    with open("outputs/test_filter.json", "w+") as out:
        out.write(json.dumps(test_set))
