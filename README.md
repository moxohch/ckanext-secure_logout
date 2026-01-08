# ckanext-secure_logout

CKAN extension that enables secure logout by invalidating the server-side session. This extension replaces CKAN's default logout mechanism with a secure implementation that removes the session from the Redis server.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.11            | yes           |
| 2.10 and earlier | not tested    |

## Installation

### Docker Installation

1. Add the following line in your Dockerfile:

    RUN pip3 install --no-cache-dir -e git+https://github.com/moxohch/ckanext-secure_logout.git@main#egg=ckanext-secure_logout

2. Add `secure_logout` to the `CKAN__PLUGINS` variable in your `.env` file:

    CKAN__PLUGINS=secure_logout

3. Configure the Redis URL in your `.env` file:

    CKAN__REDIS__URL=redis://redis:6379/1

4. Rebuild and restart your Docker container.

### Installation without Docker

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/moxohch/ckanext-secure_logout.git
    cd ckanext-secure_logout
    pip install -e .
    pip install -r requirements.txt

3. Add `secure_logout` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Configure the Redis URL in your CKAN config file (e.g. `ckan.ini`):

    ckan.redis.url = redis://localhost:6379/1

5. Restart CKAN. 

## Config settings

### ckan.redis.url

Redis connection URL used to store Flask sessions. This configuration is required for the extension to work properly.

- **Type:** string
- **Default:** `redis://localhost:6379/1`
- **Example:** `redis://redis:6379/1` (for Docker)

This variable can be configured either in the CKAN config file (`ckan.ini`) or via an environment variable (`CKAN__REDIS__URL` in Docker).
