HelloWorld Storm Service
========================

Running the service
-------------------

```
python hellostormsvc.py hello00 --auth-passwd secret --telepath tcp://127.0.0.1:9999/ --https 9443
```

Connecting your cortex
----------------------

```
cli> storm service.add tcp://root:secret@127.0.0.1:9999/
```

