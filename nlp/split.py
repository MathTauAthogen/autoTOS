import json
import random
import numpy as np
import sys


def sort_list_dict(freq, desc=False):
    return dict(sorted(freq.items(), key=lambda item: len(item[1]), reverse=desc))


def multi_argmax(arr):
    return [i for i, x in enumerate(arr) if x == np.max(arr)]


def iterative_stratification(tokens, proportions):
    unlabeled_tokens = list()
    remaining = dict()

    # Build the list of tokens per label that have not
    # been allocated to a subset yet
    for token in list(tokens):
        # Add label to account for padding
        if len(token["labels"]) == 0:
            unlabeled_tokens.append(token)
            tokens.remove(token)
            continue

        for label in token["labels"]:
            if label["class_id"] not in remaining.keys():
                remaining[label["class_id"]] = set()
            remaining[label["class_id"]].add(token)

    desired = [dict() for _ in range(len(proportions))]
    subsets = [list() for _ in range(len(proportions))]

    # Compute the desired number of examples for each label,
    # for each subset
    for c, labeled_token in remaining.items():
        for i, weight in enumerate(proportions):
            desired[i][c] = round(len(labeled_token) * weight)

    while len(tokens) > 0:
        # Allocate the least frequent label (with at least
        # 1 example remaining) first
        remaining = sort_list_dict(remaining)
        least_freq_label = list(remaining.keys())[0]

        label_tokens = list(remaining[least_freq_label])
        random.shuffle(label_tokens)

        for token in label_tokens:
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
            subset.append(token)

            for token_set in remaining.values():
                if token in token_set:
                    token_set.remove(token)

            # Decrease the desired number, based on all labels in that example
            for label in token["labels"]:
                desired[idx][label["class_id"]] -= 1

            tokens.remove(token)
        remaining.pop(least_freq_label)

    return subsets, unlabeled_tokens


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        data = json.loads(f)
    (train_set, test_set), unlabeled = iterative_stratification(data, [0.8, 0.2])

    with open("outputs/train.json", "w+") as out:
        out.write(json.dumps(train_set + unlabeled))
    with open("outputs/test.json", "w+") as out:
        out.write(json.dumps(test_set))
