read -p 'Website name: ' sitename
apt-get install python3
apt-get install python3-pip
pip install virtualenv
virtualenv env
source env/bin/activate
pip install Boorunaut
boorunaut startproject $sitename
cd $sitename
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver