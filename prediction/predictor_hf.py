from transformers import (
    TFRobertaForSequenceClassification,
    RobertaTokenizerFast,
    RobertaConfig,
)
import json
import os
from itertools import chain
import tensorflow as tf
import numpy as np
from tqdm import tqdm

NULL_CLASS = 17


class Predictor(object):
    """Interface for constructing custom predictors."""

    def __init__(self, model_path, filter_conf=0.5):
        self.tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
        self.config = RobertaConfig.from_pretrained(model_path)
        self.model = TFRobertaForSequenceClassification.from_pretrained(
            model_path, config=self.config
        )
        self.filter_conf = filter_conf

    def classify(self, tokens):
        predictions = list()

        for token in tqdm(tokens):
            inputs = self.tokenizer(
                token, truncation=True, padding=True, return_tensors="tf"
            )
            logits = self.model(inputs)[0]

            probs = tf.nn.softmax(logits, axis=1).numpy()[0]
            idx = np.argmax(probs)

            if idx == NULL_CLASS:
                continue

            predictions.append(
                {
                    "label": int(idx),
                    "conf": float(probs[idx]),
                    "raw_conf": float(logits[0][idx]),
                    "text": token,
                }
            )

        return predictions

    def predict(self, instances, **kwargs):
        """Performs custom prediction.

        Instances are the decoded values from the request. They have already
        been deserialized from JSON.

        Args:
            instances: A list of prediction input instances.
            **kwargs: A dictionary of keyword args provided as additional
                fields on the predict request body.

        Returns:
            A list of outputs containing the prediction results. This list must
            be JSON serializable.
        """
        tokens = tokenize(instances[0])

        predictions = self.classify(tokens)
        filtered_preds = filter_confidence(predictions, self.filter_conf)

        with open("../config/mapped_classes.json", "r") as map_file:
            mapping = json.loads(map_file.read())

        output_preds = [map_format_prediction(pred, mapping) for pred in filtered_preds]
        sentiment = calculate_sentiment(output_preds)

        response = {"predictions": output_preds, "sentiment": sentiment}

        return response

    @classmethod
    def from_path(cls, model_dir):
        """Creates an instance of Predictor using the given path.

        Loading of the predictor should be done in this method.

        Args:
            model_dir: The local directory that contains the exported model
                file along with any additional files uploaded when creating the
                version resource.

        Returns:
            An instance implementing this Predictor class.
        """
        return cls(f"{model_dir}/model.ckpt")


def tokenize(text):
    return [
        s
        for s in chain.from_iterable([list(s.split(". ")) for s in text.split("\n")])
        if len(s) != 0
    ]


def map_format_prediction(prediction, mapping):
    """Map a prediction to one of our defined classes, with
    a format following the final API response:

        {
          name: "class name",
          description: "class description",
          effect: "good" | "bad" | "neutral",
          weight: int,
          text: "source text from document"
        }
    """

    label = prediction["label"]
    desc = mapping[label]

    prediction["description"] = desc["title"]
    prediction["effect"] = desc["effect"]
    prediction["weight"] = desc["weight"]

    return prediction


def filter_confidence(predictions, cutoff=0.5):
    response_preds = list()

    for prediction in predictions:
        if prediction["conf"] < cutoff:
            continue

        response_preds.append(prediction)

    return response_preds


def calculate_sentiment(output_preds):
    signed_score = 0.0
    total_weight = 0.0

    for pred in output_preds:
        total_weight += pred["weight"]
        if pred["effect"] == "good":
            signed_score += pred["weight"]
        else:
            signed_score -= pred["weight"]

    if total_weight != 0:
        # Transforms to [-1.0, 1.0] range
        signed_normalized = signed_score / total_weight
    else:
        signed_normalized = 0.0
    return round(signed_normalized * 5 + 5, 1)


if __name__ == "__main__":
    # For debugging purposes only
    p = Predictor("../nlp/checkpoints/autoTOS_hf_model/", 0.9)

    instances = [open("../artifacts/tos/wayfair.txt", "r").read()]
    response = p.predict(instances)

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/response_hf.json", "w+") as out:
        out.write(json.dumps(response))
