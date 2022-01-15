```
$ python
>>> import cloud_run
>>> cloud_run.create_vm("debian-bullseye", "foo", "bar", "512M", "5G")
```

In another terminal:

```
$ ssh -p 2222 -o StrictHostKeyChecking=off localhost
$ sudo shutdown -h now
```
