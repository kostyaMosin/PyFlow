PyFlow
---------

A Django PyFlow web app based on python [PyFlow](https://github.com/kostyaMosin/PyFlow).

Django-PyFlow is a community of Python developers.


Setup
-----

````
git clone https://github.com/kostyaMosin/PyFlow.git
cd PyFlow
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
````

First run
---

````
cd PyFlow
python manage.py migrate
python manage.py createsuperuser 
````


Run
---

It will listen on :8000
````
python manage.py runserver
````


Author
------

Kostya Mosin <kostyaMosin93@gmail.com>

References
----------

- First accreditation project at the school of programming [TeachMeSkills](https://teachmeskills.by/)
