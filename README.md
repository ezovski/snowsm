# snowsm

## Local Setup

Please use a Mac. Too lazy to genericize this right now.

Install system requirements using homebrew:

```
brew install python
brew install postgresql
brew install postgis
brew install redis
```

Make sure you have `pip` and `virtualenv`. Brew should have added them, but who knows.

```
which pip virtualenv
```

Create and activate a virtualenv for this project. From the top of this project:

```
virtualenv venv
source venv/bin/activate
```

Install python dependencies:

```
pip install -r requirements.txt
```

Initialize the database:

```
./dbinit.sh
# Specify an empty password when prompted.
```

Perform the initial db migration (you may have to do it in steps... not sure why):

```
python web.py db upgrade
```

You should be good to go!

## Local operation

Most important commands are run through the `web.py` script. Some of the important ones:

* To run an import of a region from OpenStreetMap: `python web.py build_db [region_number]`

  * The regions are specified near the top of `process_trails.py`.

* To start the web server on port 5000: `python web.py run`

* To generate a new migration (perhaps after making model changes, perhaps not): `python web.py db migrate`

* To apply any migrations that have not yet been applied to the db: `python web.py db upgrade`

To start a worker process, make sure Redis is running on port 6379, then run `python worker.py` in the virtualenv. Event queues can be monitored at `/rq`. 

I recommend using PyCharm (https://www.jetbrains.com/pycharm/) to run this. The server should run properly in PyCharm just by specifying `web.py` as your script, `run` as your script parameters, and the top of this directory as your working directory.

## Dev Notes

To make an async function call:

```
import queues
queues.q.enqueue(function, param1, param2)
```

## Heroku Notes

snowsm is dependent on pip, npm, and bower for its installs. To support this, both the Node.js and Python buildpacks are needed.

```
heroku buildpacks:set https://github.com/heroku/heroku-buildpack-python
heroku buildpacks:add --index 1 https://github.com/cyberdelia/heroku-geo-buildpack
```

Also, the `IS_HEROKU` environment configuration variable must be set.
