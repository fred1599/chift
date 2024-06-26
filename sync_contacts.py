import os
import xmlrpc.client
import psycopg2
import dj_database_url
from dotenv import load_dotenv
import logging

# Configurer la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration Odoo
url = os.environ["URL_ODOO"]
db = os.environ["DB_ODOO"]
username = os.environ["USERNAME_ODOO"]
api_key = os.environ["API_KEY_ODOO"]

# Configuration PostgreSQL
database_url = os.environ["URL_DATABASE"]
logger.info("URL_DATABASE: %s", database_url)

try:
    db_config = dj_database_url.config(default=database_url)
    conn = psycopg2.connect(
        dbname=db_config["NAME"],
        user=db_config["USER"],
        password=db_config["PASSWORD"],
        host=db_config["HOST"],
        port=db_config["PORT"],
        sslmode="require",
    )
    cursor = conn.cursor()
    logger.info("Successfully connected to the database")
except Exception as e:
    logger.error("Failed to connect to the database: %s", e)
    raise

# Connexion à Odoo
try:
    common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
    uid = common.authenticate(db, username, api_key, {})
    models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))
    logger.info("Successfully connected to Odoo")
except Exception as e:
    logger.error("Failed to connect to Odoo: %s", e)
    raise


def sync_contacts():
    try:
        # Récupérer les contacts depuis Odoo
        contact_ids = models.execute_kw(
            db,
            uid,
            api_key,
            "res.partner",
            "search",
            [[["is_company", "=", True]]],
            {"offset": 0, "limit": 10},
        )
        contacts = models.execute_kw(
            db, uid, api_key, "res.partner", "read", [contact_ids]
        )
        logger.info("Retrieved contacts from Odoo")

        for contact in contacts:
            contact_id = contact["id"]
            name = contact["name"]
            email = contact.get("email", "")
            phone = contact.get("phone", "")

            # Vérifier si le contact existe déjà
            cursor.execute(
                "SELECT id FROM contacts_contact WHERE odoo_id = %s", (contact_id,)
            )
            result = cursor.fetchone()

            if result:
                # Mettre à jour le contact
                cursor.execute(
                    """
                    UPDATE contacts_contact SET name = %s, email = %s, phone = %s WHERE odoo_id = %s
                """,
                    (name, email, phone, contact_id),
                )
                logger.info("Updated contact with odoo_id %s", contact_id)
            else:
                # Insérer le contact
                cursor.execute(
                    """
                    INSERT INTO contacts_contact (odoo_id, name, email, phone) VALUES (%s, %s, %s, %s)
                """,
                    (contact_id, name, email, phone),
                )
                logger.info("Inserted contact with odoo_id %s", contact_id)

        conn.commit()
    except Exception as e:
        logger.error("Failed to sync contacts: %s", e)
        conn.rollback()


# Appeler la fonction de synchronisation
sync_contacts()
