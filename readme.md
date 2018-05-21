#how to run
```
docker build -t pool

docker run --rm -p 5000:5000 pool

``` 


#getting started in heroku
```

wget -qO- https://cli-assets.heroku.com/install-ubuntu.sh | sh
heroku container:login
heroku create {project-name}
heroku container:push web
heroku open

```