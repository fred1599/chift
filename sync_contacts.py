import os
import xmlrpc.client
import psycopg2
import time

from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Odoo
url = os.environ["URL_ODOO"]
db = os.environ["DB_ODOO"]
username = os.environ["USERNAME_ODOO"]
api_key = os.environ["API_KEY_ODOO"]

# Configuration PostgreSQL
conn = psycopg2.connect(
    dbname=os.environ["DB_NAME"],
    user=os.environ["USER"],
    password=os.environ["PASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"]
)

cursor = conn.cursor()

# Connexion à Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, api_key, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

def sync_contacts():
    # Récupérer les contacts depuis Odoo
    contact_ids = models.execute_kw(db, uid, api_key, 'res.partner', 'search', [[['is_company', '=', True]]], {'offset': 10, 'limit': 5})
    contacts = models.execute_kw(db, uid, api_key, 'res.partner', 'read', [contact_ids])

    for contact in contacts:
        contact_id = contact['id']
        name = contact['name']
        email = contact.get('email', '')
        phone = contact.get('phone', '')

        # Vérifier si le contact existe déjà
        cursor.execute('SELECT id FROM contacts_contact WHERE odoo_id = %s', (contact_id,))
        result = cursor.fetchone()

        if result:
            # Mettre à jour le contact
            cursor.execute('''
                UPDATE contacts_contact SET name = %s, email = %s, phone = %s WHERE odoo_id = %s
            ''', (name, email, phone, contact_id))
        else:
            # Insérer le contact
            cursor.execute('''
                INSERT INTO contacts_contact (odoo_id, name, email, phone) VALUES (%s, %s, %s, %s)
            ''', (contact_id, name, email, phone))

    conn.commit()

if __name__ == '__main__':
    while True:
        sync_contacts()
        time.sleep(600)  # Exécuter toutes les 10 minutes
