import sys
import json
from finetune import SequenceLabeler
from finetune.base_models import RoBERTa

# NOTE: You will also need to run python3 -m spacy download en


def convert_model_data(model_data):
    tokens = list()
    labels = list()
    for token in model_data:
        tokens.append(token["token"])

        for label in token["labels"]:
            label["label"] = label.pop("class_id")
        labels.append(token["labels"])

    return tokens, labels


def train(train_set):
    tokens, labels = convert_model_data(train_set)
    model = SequenceLabeler(
        base_model=RoBERTa,
        n_epochs=5,
        chunk_long_sequences=True,
        eval_acc=True,
        oversample=True,
        subtoken_predictions=False,
        # max_empty_chunk_ratio=1.0,
    )

    model.fit(tokens, labels)
    model.save("checkpoints/model-all.ckpt")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        train_set = json.loads(f.read())

    train(train_set)
