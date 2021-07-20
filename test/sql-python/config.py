import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://ksups111.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'Sl0kc0sQtFkHx6prt6QJD6hxQuILLDXe4ESYjFMOXu6FK261JHFkDRHI2vWTHTPpbUmnQXIOEalNRYCnoBQGwQ=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'ToDoList'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Items'),
}