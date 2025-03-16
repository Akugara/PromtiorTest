<img width="831" alt="promptiordiagram" src="https://github.com/user-attachments/assets/8c3a5e70-0760-427e-8c6c-99cf2d478f82" /># RAG Application

A Retrieval-Augmented Generation (RAG) application built with Streamlit and OpenAI.

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
```
Then edit `.env` and add your actual API keys and credentials.

4. Run the application
```bash
streamlit run app.py
```

## Docker Setup

1. Build the image:
```bash
docker build -t rag-app .
```

2. Run the container:
```bash
docker run -d \
  --name rag-app \
  -p 8501:8501 \
  --env-file .env \
  --restart unless-stopped \
  rag-app
```

## Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key

Optional variables for AWS deployment:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)

## Security Notes

- Never commit the `.env` file
- Keep your API keys secure
- Use appropriate security groups in AWS
- Follow the principle of least privilege for API keys 
