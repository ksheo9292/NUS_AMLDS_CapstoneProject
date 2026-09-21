# Deployment

Start the API from the main project folder:

```bash
uvicorn deployment.app:app --reload
```

Open `http://127.0.0.1:8000/docs`, choose `POST /predict`, click **Try it out**, paste the contents of `sample_request.json`, and click **Execute**.

