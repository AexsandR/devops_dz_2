docker network create net
docker run --rm  --name bd --network net -e POSTGRES_USER=qwe -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=users -v "$PWD/init_db.sql:/docker-entrypoint-initdb.d/init.sql"  -d  postgres 
sleep 10
docker build -t app .
docker run --rm --network net --env-file .env -p 5000:8000 -v $(pwd)/logs:/app/logs -d app
