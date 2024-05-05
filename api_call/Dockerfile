FROM python:3.10
COPY . .
RUN pip install -r requirements.txt
ARG API_KEY=NYT_API_KEY
ENV API_KEY=$(API_KEY)
CMD ["python", "state_api_responses.py"]
