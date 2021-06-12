from finetune import SequenceLabeler
import json
import os
from itertools import chain


class Predictor(object):
    """Interface for constructing custom predictors."""

    def __init__(self, model_path):
        self.model = SequenceLabeler.load(model_path)

    def predict(self, tos, **kwargs):
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
        tokens = tokenize(tos)

        predictions = self.model.predict(tokens)
        filtered_preds = filter_confidence(predictions, 0.9)

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
    del prediction["start"]
    del prediction["end"]

    label = prediction["label"]
    desc = mapping[int(label)]

    prediction["conf"] = float(prediction["confidence"][label])
    del prediction["confidence"]

    prediction["description"] = desc["title"]
    prediction["effect"] = desc["effect"]
    prediction["weight"] = desc["weight"]

    return prediction


def filter_confidence(predictions, cutoff=0.5):
    response_preds = list()

    for token_prediction in predictions:
        if len(token_prediction) == 0:
            # Padding detected
            continue
        for prediction in token_prediction:
            label = prediction["label"]
            for class_id, conf in prediction["confidence"].items():
                if conf < 0.1:
                    prediction["confidence"][class_id] = 0.0
            if prediction["confidence"][label] < cutoff:
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
        del pred["weight"]

    if total_weight != 0:
        # Transforms to [-1.0, 1.0] range
        signed_normalized = signed_score / total_weight
    else:
        signed_normalized = 0.0
    return round(signed_normalized * 5 + 5, 1)


if __name__ == "__main__":
    # For debugging purposes only
    p = Predictor("../nlp/checkpoints/model.ckpt")

    instances = [open("../artifacts/tos/wayfair.txt", "r").read()]
    response = [p.predict(instance) for instance in instances]

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/response_ft.json", "w+") as out:
        out.write(json.dumps(response))

    exit(0)
