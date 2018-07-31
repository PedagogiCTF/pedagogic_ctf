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
	for dir in dockerfiles/* ; do \
		echo " [*] Entering $$dir" ; \
		cd $$dir ; \
		image=$$(echo $$dir | sed "s/.*\///") ; \
		echo " [*] Building $$image Docker image" ; \
		docker build . -t $$image ; \
		echo ; \
		cd - ; \
	done

api: challenges.json go docker-util-images
	docker build -t pedagogictf-api -f Dockerfile.api .

frontend: node
	docker volume ls | grep frontend-ssl || (docker volume create frontend-ssl && echo "Add your ssl certificates to the docker volume! See ssl.sh")
	docker build -t pedagogictf-frontend -f Dockerfile.front .

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
	docker exec db createuser -U postgres ctf || echo "User already exists"; \
	docker exec db echo $${password} ; \
	docker exec db psql -U postgres -c "ALTER USER ctf WITH PASSWORD 'md5$$(echo -n $${password}ctf | md5sum | cut -d ' ' -f 1)'"
	# Create db if not exists
	docker exec db createdb -U postgres pedagogic_ctf  || echo "DB already exists";
	# Grant access to user to the DB
	docker exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE pedagogic_ctf TO ctf"

api-run: frontend api trusted-network launch-db
	rm -rf /tmp/guest && mkdir /tmp/guest && chmod -R 750 /tmp/guest
	docker run -d --restart=unless-stopped \
		--network=trusted \
		--name=api \
		--env-file $(ENV_FILE) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v /tmp/guest:/tmp \
		pedagogictf-api
	docker run -d --restart=unless-stopped \
		--network=trusted \
		--name=front \
		-p 80:80 \
		-p 443:443 \
		-v frontend-ssl:/etc/nginx/ssl/ \
		pedagogictf-frontend

clean:
	rm main
