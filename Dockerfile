FROM python:3.9
COPY . .
RUN pip install -r requirments.txt && apt update && apt install libzbar-dev -y
CMD ["python", "__main__.py"]
