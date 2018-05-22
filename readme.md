Lapfinder scrapes NYC recreation center websites and helps you find the lap hours at the rec center closest to you!


#how to run
```
docker build -t lapfinder

docker run --rm -p 5000:5000 lapfinder

``` 


#getting started in heroku
```

wget -qO- https://cli-assets.heroku.com/install-ubuntu.sh | sh
heroku container:login
heroku create {project-name}
heroku container:push web
heroku open --app lapfinder

```

App link http://lapfinder.herokuapp.com/