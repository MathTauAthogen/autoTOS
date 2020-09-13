import tensorflow_cloud as tfc
import os

print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
bucket = "autotos-service-account"
labels = {"phase": "hello", "owner": "world"}

tfc.run(
    requirements_txt="../requirements.txt",
    distribution_strategy="auto",
    chief_config="auto",
    docker_image_bucket_name=bucket,
    job_labels=labels,
)
