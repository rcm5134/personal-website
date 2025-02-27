Riley Moorman's Personal Webpage built partially from elements in Prof. MM Ghassemi's <ghassem3@msu.edu> CSE 477 course.

Uploading website to gcloud:

gcloud builds submit --tag gcr.io/personal-webpage-449418/personal-page
gcloud run deploy --image gcr.io/personal-webpage-449418/personal-page --platform managed
