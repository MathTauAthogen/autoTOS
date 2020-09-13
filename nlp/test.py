from finetune import SequenceLabeler
from finetune.util.metrics import annotation_report
import json
import sys
from itertools import chain
from train import convert_model_data


def evaluate(tokens):
    model = SequenceLabeler.load("checkpoints/model.ckpt")
    return model.predict(tokens)


def test(test_data):
    tokens, labels = convert_model_data(test_data)

    predictions = evaluate(tokens)
    print(predictions)
    print(annotation_report(labels, predictions))

    return predictions


def tokenize(text):
    return [
        s
        for s in chain(["".join(s.split(". ")) for s in text.split("\n")])
        if len(s) != 0
    ]


def filter_confidence(predictions):
    pass


if __name__ == "__main__":
    tokens = tokenize(open("../data/tos/amazon.txt", "r").read())
    print("\n".join(list(tokens)))
    print(evaluate(tokens))
    exit(0)

    with open(sys.argv[1], "r") as f:
        test_set = json.loads(f.read())

    output = test(test_set)
    with open("outputs/predictions.json", "w+") as out:
        out.write(json.dumps(output))
