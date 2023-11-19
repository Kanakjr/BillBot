docker system prune -f
docker build -f "Dockerfile" -t aitools:latest "."
docker ps -q --filter "name=aitools" | xargs -I {} docker stop {}
sleep 5
docker run --rm -d -p 8503:8503/tcp --name aitools aitools