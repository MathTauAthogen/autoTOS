import sys
import json
import pickle
import tensorflow as tf
import transformers # huggingface
from transformers import RobertaConfig, RobertaModel, 
    RobertaTokenizerFast, TFRobertaForSequenceClassification


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
    tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base')
    config = RobertaConfig()
    model = TFRobertaForSequenceClassification(config)
    tokens, labels = convert_model_data(train_set)

    tokenized_input = [tokenizer(t) for t in tokens]
    
    items = tokenizer(tokens, labels)

    with open("checkpoints/hf_orig_model.p", "wb") as file:
        pickle.dump(model, file)

    model.fit(items)
    model.save("checkpoints/hf_model.ckpt")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        train_set = json.loads(f.read())

    train(train_set)
