from finetune import SequenceLabeler
from finetune.util.metrics import annotation_report
import json
import sys


def test(test_data):
    tokens = list()
    labels = list()
    for token in test_set:
        tokens.append(token["token"])
        labels.append(token["labels"])

    model = SequenceLabeler.load("checkpoints")

    predictions = model.predict_proba(tokens)
    print(predictions)
    print(annotation_report(labels, predictions))

    return predictions


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        test_set = json.loads(f.read())

    output = test(test_set)
    with open("output/predictions.txt", "w+") as out:
        out.write(output)
