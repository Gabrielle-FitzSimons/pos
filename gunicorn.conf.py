bind = "0.0.0.0:8080"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
keepalive = 5

keyfile = "privkey.pem"
certfile = "cert.pem"
ca_certs = "chain.pem"
