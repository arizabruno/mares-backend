requirements:
	pip install --upgrade pip && pip freeze > requirements.txt

install:
	pip install --no-cache-dir -r requirements.txt

run_api:
	uvicorn app.main:app --port 8080 --host 0.0.0.0  --reload

docker_build:
	docker build --tag=mares-api:dev .

docker_run:
	docker run -it -e PORT=8080 -p 8080:8080 --name mares-api-container mares-api:dev

docker_clean:
	docker rm mares-api-container
	docker rmi mares-api:dev

upload_container_to_registry:
	./upload_to_registry.sh

init_cloud_infra:
	cd terraform && terraform init

apply_cloud_infra:
	cd terraform && terraform apply

destroy_cloud_infra:
	cd terraform && terraform destroy
