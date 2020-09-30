import sys
import json
import pickle
import tensorflow as tf
from transformers import (
    RobertaTokenizerFast,
    TFRobertaForSequenceClassification,
)


def convert_model_data(model_data):
    tokens = list()
    labels = list()
    for token in model_data:
        for label in token["labels"]:
            tokens.append(label["text"])
            labels.append(label["class_id"])

    return tokens, labels


def train(train_set):
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    tokens, labels = convert_model_data(train_set)

    train_encodings = tokenizer(tokens, truncation=False, padding=True)

    train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), labels))

    model = TFRobertaForSequenceClassification.from_pretrained("roberta-base")

    optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
    model.compile(
        optimizer=optimizer, loss=model.compute_loss
    )  # can also use any keras loss fn

    cp_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath="checkpoints/hf_model.ckpt", save_weights_only=True, verbose=1
    )
    model.fit(
        train_dataset.shuffle(1000).batch(16),
        epochs=5,
        batch_size=16,
        callbacks=[cp_callback],
    )


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        train_set = json.loads(f.read())

    train(train_set)
