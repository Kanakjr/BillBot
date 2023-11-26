docker system prune -f
docker build -f "Dockerfile" -t billbot:latest "."
docker ps -q --filter "name=billbot" | xargs -I {} docker stop {}
sleep 5
docker run --rm -d -p 8504:8504/tcp --name billbot billbot