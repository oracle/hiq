# HiQ UI

HiQ provide an integrated UI if you use popular Python web framework like FastAPI, Flask etc.

Take FastAPI as an example, where can find it at [here](https://github.com/oracle-samples/hiq/tree/main/hiq/examples/fastapi).


`webapp.py` is the original web server code to serve an `AlexNet` onnx model with FastAPI.

To trace the latency, we can run `python webapp_driver.py`:

```
> python webapp_driver.py
INFO:     Started server process [16618]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

Open the link `http://localhost:8080/hiq` in your browser, and you will see something like this page:

![](https://raw.githubusercontent.com/oracle-samples/hiq/main/hiq/docs/source/img/hiq-ui-1.png)


Click the `API` link under HIQ, and you can see the swagger UI for the web server. You can try out the `/predict` endpoint to send some requests.

In the response header part, you can see something like:

```
 access-control-expose-headers: X-Request-ID
 content-length: 23
 content-type: application/json
 date: Mon,06 Feb 2023 19:55:44 GMT
 server: uvicorn
 x-latency: 0.15682927519083023
 x-request-id: fe0a322299874deeb811b0cdb9ac55a5
```


By default, HiQ will generate a unique `x-request-id` for each request. It will put the endpoint latency in `x-latency` field.


Then you can go back to the HiQ page(`http://localhost:8080/hiq`), and click the `req ID` in the Latency table. You would see something like:

![](https://raw.githubusercontent.com/oracle-samples/hiq/main/hiq/docs/source/img/hiq-ui-2.png)


This gives you the text graph of the HiQ tree.



## Disable HiQ

In case you want to disable HiQ, just send a GET request to `http://localhost:8080/hiq_disable`, or just access the URL in the browser.


## Enable HiQ

To aenale HiQ, you just need to send a GET request to `http://localhost:8080/hiq_enable`, or just access the URL in the browser.


