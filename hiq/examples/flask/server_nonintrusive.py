import hiq


driver = hiq.HiQFlaskLatencyOtel(
    hiq_id_func=hiq.hiq_utils.FlaskReqIdGenerator(),
    endpoints={
        "server_request",
    },
)

app_ = hiq.mod("server_uninstrumented").app
app_.run(port=8082)

driver.show()
