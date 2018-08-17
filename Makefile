GOPATH=$(shell pwd)
ENV_FILE=src/ctf/config/config.env

challenges.json:
	python3 generate_challenges.json.py

node:
	cd frontend-angular && bower install

go:
	GOPATH=$(GOPATH) go get -v -d ./src/ctf/...
	GOPATH=$(GOPATH) go build src/ctf/main/main.go

docker-util-images:
	for image in correction exploitation sandbox selenium ; do \
		cd dockerfiles/$$image ; \
		docker build . -t pedagogictf/$$image ; \
		@echo ; \
		cd - ; \
	done

api: challenges.json go docker-util-images
	docker build -t pedagogictf/api -f Dockerfile.api .

frontend-ssl:
	docker volume ls | grep frontend-ssl || (docker volume create frontend-ssl && echo -e "\n\e[41mAdd your ssl certificates to the docker volume! See ssl.sh\e[49m\n" && exit 2)

frontend: frontend-ssl node
	docker build -t pedagogictf/frontend -f Dockerfile.front .

trusted-network:
	docker network ls | grep trusted || docker network create trusted

launch-db: trusted-network
	docker volume ls | grep db || docker volume create db
	password=$$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1); \
	sed -i -e"s/^DB_HOST=.*/DB_HOST=db/" $(ENV_FILE); \
	sed -i -e"s/^DB_USER=.*/DB_USER=ctf/" $(ENV_FILE); \
	sed -i -e"s/^DB_PASS=.*/DB_PASS=$$password/" $(ENV_FILE); \
	docker run -d --restart=unless-stopped \
		--network=trusted \
		--name=db \
		-e POSTGRES_DB=pedagogic_ctf \
		-v db:/var/lib/postgresql/data \
		postgres:10.4; \
	echo "DB is launching." && sleep 2; \
	echo "DB is launching.." && sleep 2; \
	echo "DB is launching..." && sleep 2; \
	docker exec db createuser -U postgres ctf || echo "User already exists"; \
	docker exec db psql -U postgres -c "ALTER USER ctf WITH PASSWORD 'md5$$(echo -n $${password}ctf | md5sum | cut -d ' ' -f 1)'"
	# Create db if not exists
	docker exec db createdb -U postgres pedagogic_ctf  || echo "DB already exists";
	# Grant access to user to the DB
	docker exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE pedagogic_ctf TO ctf"

docker-push:
	docker push pedagogictf/api
	docker push pedagogictf/frontend
	docker push pedagogictf/selenium
	docker push pedagogictf/sandbox
	docker push pedagogictf/exploitation
	docker push pedagogictf/correction

docker-pull:
	docker pull pedagogictf/api
	docker pull pedagogictf/frontend
	docker pull pedagogictf/selenium
	docker pull pedagogictf/sandbox
	docker pull pedagogictf/exploitation
	docker pull pedagogictf/correction

launch:
	sudo rm -rf /tmp/guest && mkdir /tmp/guest && chmod -R 750 /tmp/guest
	docker run -d --restart=unless-stopped \
		--network=trusted \
		--name=api \
		--env-file $(ENV_FILE) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v /tmp/guest:/tmp \
		pedagogictf/api
	docker run -d --restart=unless-stopped \
		--network=trusted \
		--name=front \
		-p 80:80 \
		-p 443:443 \
		-v frontend-ssl:/etc/nginx/ssl/ \
		pedagogictf/frontend

run-dev: frontend api trusted-network launch-db launch
	echo "API launched with images built from local sources"

run-prod: docker-pull frontend-ssl trusted-network launch-db launch
	echo "API launched from remote docker images"
