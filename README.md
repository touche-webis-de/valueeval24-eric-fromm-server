# valueeval24-eric-fromm-server
Reimplementation of the approach of Mishra and Morren. [[paper](https://touche.webis.de/publications.html#mishra_2024)]

## Single Run

```bash
# run
tira-run \
  --input-directory "$PWD/valueeval24/test" \
  --output-directory "$PWD/output" \
  --allow-network True \
  --image webis/valueeval24-eric-fromm-server:1.0.0

# or
docker run --rm \
  -v "$PWD/valueeval24/test:/dataset" -v "$PWD/output:/output" \
  webis/valueeval24-eric-fromm-server:1.0.0

# view results
cat output/run.tsv
```

## Inference Server
A local inference server can be started from the same Docker-Image using:

```bash
PORT=8001

docker run --rm -it --init \
  -v "$PWD/logs:/logs" \
  -p $PORT:$PORT \
  --entrypoint tira-run-inference-server \
  webis/valueeval24-eric-fromm-server:1.0.0 \
  --script /requester.py --port $PORT
```
Exemplary request for a server running on localhost:8001 are

```bash
# POST (JSON list as payload)
curl -X POST -H "application/json" \
  -d "[\"element 1\",\"element 2\"]" \
  localhost:8001
```
and
```bash
# GET (JSON object string(s) passed to the 'payload' parameter)
curl "localhost:8001?payload=\"element+1\"&payload=\"element+2\""
```

## Building

```bash
docker build -f Dockerfile -t webis/valueeval24-eric-fromm-server:1.0.0 .
```
