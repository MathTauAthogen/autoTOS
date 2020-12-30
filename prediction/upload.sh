gcloud ai-platform models create autotos \
  --regions us-central1 \
  --enable-logging


gcloud beta ai-platform versions create autotos1 \
  --model autotos \
  --runtime-version 1.15 \
  --python-version 3.7 \
  --origin gs://autotos-model/model.ckpt \
  --package-uris gs://autotos-model/auto_tos_summarizer-0.1.tar.gz \
  --prediction-class predictor.Predictor \
  --machine-type n1-standard-2

