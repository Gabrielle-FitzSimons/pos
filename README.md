To get started, make sure python 3.9 is installed

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

or

```
./init_dev.sh
```

TODO: Add middleware for logging access
TODO: Add more customisation to big transaction query.
TODO: Add superuser properly!
