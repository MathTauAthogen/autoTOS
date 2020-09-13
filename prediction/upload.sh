gcloud ai-platform models create autotos \
  --regions us-east1


gcloud beta ai-platform versions create 1.0 \
  --model autotos \
  --runtime-version 1.15 \
  --python-version 3.7 \
  --origin gs://autotos-model/checkpoints/model.ckpt \
  --package-uris gs://your-bucket/path-to-staging-dir/my_custom_code-0.1.tar.gz \
  --prediction-class predictor.Predictor

