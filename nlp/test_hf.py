from sklearn.metrics import classification_report

from transformers import TFRobertaForSequenceClassification
import json
import sys
from train_hf import convert_model_data


def evaluate(tokens):
    model = TFRobertaForSequenceClassification.load(
        "checkpoints/model.ckpt", from_tf=True
    )
    return model.predict(tokens)


def test(test_data):
    tokens, labels = convert_model_data(test_data)

    predictions = evaluate(tokens)
    print(predictions)
    print(classification_report(labels, predictions))

    return predictions


if __name__ == "__main__":

    with open(sys.argv[1], "r") as f:
        test_set = json.loads(f.read())

    output = test(test_set)
    with open("outputs/predictions.json", "w+") as out:
        out.write(json.dumps(output))
