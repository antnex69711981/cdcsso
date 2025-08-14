APP_NAME=sso-validator
DOCKER_IMAGE=$(APP_NAME):latest
TAR_FILE = $(APP_NAME).tar
PORT=8000

.PHONY: build run stop logs shell

save:
	docker build -t $(DOCKER_IMAGE) .
	docker save -o $(TAR_FILE) $(DOCKER_IMAGE)
	@echo "📦 已將映像檔儲存為 $(TAR_FILE)"

build:
	docker build -t $(DOCKER_IMAGE) .

run:
	docker run --rm -it -p $(PORT):8000 $(DOCKER_IMAGE)

stop:
	docker stop $$(docker ps -q --filter ancestor=$(DOCKER_IMAGE)) || true

logs:
	docker logs -f $$(docker ps -q --filter ancestor=$(DOCKER_IMAGE))

shell:
	docker exec -it $$(docker ps -q --filter ancestor=$(DOCKER_IMAGE)) /bin/bash