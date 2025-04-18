# testing

> [!IMPORTANT]
> Learn about the endpoints [here](endpoints.md)

1. Copy the environment variables // ask from team if you don't want to create them yourself
   ```sh
   cp app/.env.example app/.env # or do it manually
   ```



2. Install [docker](https://docs.docker.com/get-started/get-docker/)
3. Follow this:

# Commands


```sh
make reset  # Cleans existing containers and starts fresh
```
---

```sh
make start  # Starts DB + app with live code reloading
```

```sh
make stop # Stops the containers
```
---

```sh
make clean # Cleans the containers and cleans cache
```

### Testing

```sh
make tests  # Runs pytest suite # too lazy to implement (･ω<)☆
```

## Go to this URL to test the endpoints using Swagger

[http://localhost:8000/docs](http://localhost:8000/docs)
