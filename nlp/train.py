import sys
import json
from finetune import SequenceLabeler
from finetune.base_models import RoBERTa


def train(train_set):
    tokens = list()
    labels = list()
    for token in train_set:
        tokens.append(token["token"])
        labels.append(token["labels"])

    model = SequenceLabeler(
        base_model=RoBERTa,
        n_epochs=3,
        chunk_long_sequences=True,
        eval_acc=True,
        oversample=True,
        subtoken_predictions=True,
        max_empty_chunk_ratio=1.0,
    )

    model.fit(tokens, labels)
    model.save("checkpoints")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        train_set = json.loads(f.read())

    train(train_set)
