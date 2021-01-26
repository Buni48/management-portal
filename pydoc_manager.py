import django, pydoc, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management_portal.settings')
django.setup()
pydoc.cli()
