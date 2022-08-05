# Management Portal

A management portal to manage licenses, rollout updates to the customer and send heartbeats from customer servers.
It was developed on a university project from October 2020 to January 2021 for a partner company.

## Goal of this project

The goal of this project is a central web portal where you can easily manage heartbeats, licenses and updates.

### Heartbeat

The heartbeat should be send every day by the customer servers which are running the company's software.
The goal of this is to be able to notice early if a server is down. Also the heartbeat can send error messages.
In the web portal you are able to see if any heartbeats are missing or sent with error messages.

### Licenses

Because doing license rollouts manually is very time-consuming you should be able to manage all licenses.
You can read, create, edit and delete all existing licenses in the web portal.
You are also able to see if a license is gonna expire soon.
If the license is extended you can create a future license which will rolls out automatically to the customer software.

### Updates

Same as automatically rolled out licenses also updates should be rolled out automatically.

## Used technologies

- Python 3 / Django
- JQuery, Bootstrap & Font Awesome
- MariaDB

## Installation

You need to have Python 3 installed.
Next you need to have Django and some libaries for it installed.

```bash
pip install django
pip install mysqlclient
pip install djangorestframework
pip install requests
pip install schedule
```

Within the next step you should make sure that your MariaDB connection credentials are correct by looking up at `DATABASES` in `database.py`.
After that you can create a superuser and migrate the database tables.

In Windows:

```bash
python manage.py createsuperuser
python manage.py migrate
```

In Linux and MacOS:

```bash
python3 manage.py createsuperuser
python3 manage.py migrate
```

### Customer scripts

The content of `Kundenscripts` belongs to the customer server. You might have to convert the `.py` file to an `.exe`.
To do this you have to execute:

```bash
pip install pyinstaller
pip install auto-py-to-exe
```

After the helper tool opens you can select the file to convert.

## Usage

To use the management portal you can start the webserver.

In Windows:
`python manage.py runserver`

In Linux and MacOS:
`python3 manage.py runserver`
