# mail sender

## local

1) provide env vars in .env
2) run locally
```
functions-framework-python --target send_mail
```

## deploy

1) provide env vars in .env.yaml
2) deploy
```
gcloud functions deploy send_mail --region=europe-central2 --runtime=python312 --trigger-http --source=./ --env-vars-file .env.yaml
```

## auth token

gcloud auth print-identity-token
