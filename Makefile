requirements:
	pip install --upgrade pip && pip freeze > requirements.txt

install:
	pip install --no-cache-dir -r requirements.txt

run_api:
	uvicorn app.main:app --port 8080 --host 0.0.0.0  --reload

docker_build:
	docker build -f docker/Dockerfile --tag=mares-api:dev .

docker_run:
	docker run -it -e PORT=8080 -p 8080:8080 mares-api:dev
