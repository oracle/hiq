import hiq


driver = hiq.HiQFlaskLatencyOtel(
    endpoints={
        "server_request",
    },
)

app_ = hiq.mod("server_uninstrumented").app
app_.run(port=8082)
