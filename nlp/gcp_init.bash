# https://towardsdatascience.com/develop-train-and-deploy-tensorflow-models-using-google-cloud-ai-platform-32b47095878b
export PROJECT_ID='autotos'

gcloud config set project $PROJECT_ID

export SA_NAME='autotos-service-account'

gcloud iam service-accounts create $SA_NAME

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
	--role 'roles/editor'

gcloud iam service-accounts keys create key.json --iam-account \
	$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="key.json"

export BUCKET='autotos-model'

# gsutil mb gs://$BUCKET