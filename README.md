# traxee
Important folder is traxee-simple where the main django project exists

Use the package manager [pip](https://pip.pypa.io/en/stable/) to setup the environment.
```bash
pip install requirements.txt
```
Before running the server change the path of firebase key(good to set as environment variable) json file in views.py file in flipkart app.

To run Django server run command
```bash
python manage.py runserver
```
As dependency for schedular tasks like fetching price of products every day it currently uses celery beats. And it needs redis to act as message broker.
So install redis before running celery server
Visit [here](https://www.codingforentrepreneurs.com/blog/hello-linux-install-redis) for more on Celery + Redis + Django.
```bash
brew install redis
brew services start redis
```

If redis-server command shows error that port is currently busy use
```bash
sudo services redis-server stop
```
and start the server again using command
```bash
redis-server
```
**New price fetched in every 24hrs updated at 11:20pm everyday**
**currently the mailing functionality only works by sending udated price on every morning 7am**
