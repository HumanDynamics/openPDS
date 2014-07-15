[uwsgi]
socket = 127.0.0.1:{{ uwsgi_port }}
threads = 40
master = 1
env = DJANGO_SETTINGS_MODULE=settings
module = django.core.handlers.wsgi:WSGIHandler()
# XXX - in the future, when we create our fabric_common library,
# we'll then see this as instance_root/repo_name/app_name
# we'll want to add a chunk in documentation about this..
chdir = {{ instance_root }}/{{ repo_name }}/pds
