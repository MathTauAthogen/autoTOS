import sys
import json
import pickle
import tensorflow as tf
from transformers import (
    RobertaTokenizer,
    RobertaConfig,
    TFRobertaForSequenceClassification,
    TFTrainer,
    TFTrainingArguments,
)


def convert_model_data(model_data):
    tokens = list()
    labels = list()
    for token in model_data:
        for label in token["labels"]:
            if len(label["text"].split(" ")) > 512:
                # token too long for processing
                continue
            tokens.append(label["text"])
            labels.append(int(label["class_id"]))

    return tokens, labels


def get_tf_dataset(labeled_set):
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    tokens, labels = convert_model_data(labeled_set)
    print(tokens, labels)
    encodings = tokenizer(tokens, truncation=True, padding=True, return_tensors="tf")

    return tf.data.Dataset.from_tensor_slices((dict(encodings), labels))


def train(train_set):
    train_dataset = get_tf_dataset(train_set)
    config = RobertaConfig.from_pretrained("roberta-base")

    model = TFRobertaForSequenceClassification.from_pretrained(
        "roberta-base", config=config
    )

    optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
    model.compile(
        optimizer=optimizer, loss=model.compute_loss
    )  # can also use any keras loss fn

    model.fit(
        train_dataset.shuffle(1000).batch(4),
        epochs=5,
        batch_size=4,
    )
    model.save_pretrained("checkpoints/autoTOS_hf_model2")


if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else "outputs/train_filter.json"
    with open(fname, "r") as f:
        train_set = json.loads(f.read())

    train(train_set)
