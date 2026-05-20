from hashlib import md5

username = "admin"
remote_addr = "127.0.0.1"
print(md5((username + remote_addr).encode()).hexdigest())