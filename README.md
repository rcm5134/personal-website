
gcloud builds submit --tag gcr.io/cse477-fall-2024/exam
gcloud run deploy --image gcr.io/cse477-fall-2024/exam --platform managed
