from sklearn.metrics import classification_report

from transformers import (
    RobertaTokenizerFast,
    RobertaConfig,
    TFRobertaForSequenceClassification,
    TFTrainer,
    TFPreTrainedModel,
    TFTrainingArguments,
)

import json
import sys
from train_hf import convert_model_data


def evaluate(tokens):
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")

    inputs = tokenizer(tokens, truncation=True, padding=True, return_tensors="tf")

    config = RobertaConfig.from_pretrained("roberta-base")
#    config.num_labels = len(set(labels))  # number of classes in classes.json

    model = TFPreTrainedModel.from_pretrained(
        "checkpoints/hf_model.ckpt.index", config=config, from_tf=True
    )
    mode.eval()
    #model.load_weights("checkpoints/hf_model.ckpt")

    return model(inputs)


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
