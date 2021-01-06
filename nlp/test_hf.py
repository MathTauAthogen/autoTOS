import tensorflow as tf
from tqdm import tqdm
from sklearn.metrics import classification_report

from transformers import (
    RobertaTokenizer,
    RobertaConfig,
    TFRobertaForSequenceClassification,
)

import json
import sys
import numpy as np
from train_hf import convert_model_data


def evaluate(tokens):
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    config = RobertaConfig.from_pretrained("checkpoints/autoTOS_hf_model/")

    model = TFRobertaForSequenceClassification.from_pretrained(
        "checkpoints/autoTOS_hf_model/", config=config
    )

    predictions = list()

    for token in tqdm(tokens):
        inputs = tokenizer(token, truncation=True, padding=True, return_tensors="tf")
        logits = model(inputs)[0]
        probs = tf.nn.softmax(logits, axis=1).numpy()[0]
        idx = np.argmax(probs)

        predictions.append(
            {"class_id": int(idx), "conf": float(probs[idx]), "text": token}
        )

    return predictions


def test(test_data):
    tokens, labels = convert_model_data(test_data)

    predictions = evaluate(tokens)

    predicted_labels = [prediction["class_id"] for prediction in predictions]

    print(classification_report(labels, predicted_labels))

    return predictions


if __name__ == "__main__":

    with open(sys.argv[1], "r") as f:
        test_set = json.loads(f.read())

    output = test(test_set)
    with open("outputs/predictions.json", "w+") as out:
        out.write(json.dumps(output))
