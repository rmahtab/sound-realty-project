# sound-realty-project

House price prediction service for Sound Realty

Run the following commands to start running the inference endpoint:

```
$ docker build -t sound-realty-inference .

$ docker run -d -p 8000:8000 sound-realty-inference
```

Once the container is running, run the test script:

```
$ python test_inference.py --n 5 --random_state 42
```

Pass `n` to specify number of samples to test and `random_state` if you'd like to resample same records.

Update the endpoint to try out model v2:

```
$ curl -X POST http://127.0.0.1:8000/reload-model

$ python test_inference.py --n 5 --random_state 42
```

Specifying same `random_state` before and after reloading the model allows you to compare price predictions across model versions.
