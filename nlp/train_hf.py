import sys
import json
import pickle
import tensorflow as tf
from transformers import (
    RobertaTokenizerFast,
    RobertaConfig,
    TFRobertaForSequenceClassification,
    TFTrainer,
    TFTrainingArguments
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


def train(train_set):
    """
    This works
    """
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    tokens, labels = convert_model_data(train_set)

    train_encodings = tokenizer(
        tokens, truncation=False, padding=True
    )

    train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), labels))

    config = RobertaConfig.from_pretrained("roberta-base")
    config.num_labels = len(set(labels)) # number of classes in classes.json

    model = TFRobertaForSequenceClassification.from_pretrained("roberta-base", config=config)

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
        callbacks=[cp_callback]
    )

def builtin_train(train_set, test_set):
    """
    This does not work
    """
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")

    train_tokens, train_labels = convert_model_data(train_set)
    test_tokens, test_labels = convert_model_data(test_set)

    train_encodings = tokenizer(
        train_tokens, truncation=False, padding=True,
        return_tensors="tf"
    )
    test_encodings = tokenizer(
        test_tokens, truncation=False, padding=True,
        return_tensors="tf"
    )

    train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), train_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((dict(test_encodings), test_labels))

    model = TFRobertaForSequenceClassification.from_pretrained("roberta-base")

    args = TFTrainingArguments(
        output_dir="./checkpoints",
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs'
    )

    trainer = TFTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset.shuffle(1000).batch(16).repeat(2),
        eval_dataset=test_dataset
    )

    trainer.train()



if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        train_set = json.loads(f.read())
    
    train(train_set)
