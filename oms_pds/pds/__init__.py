import mongoengine
import oms_pds.settings as settings

# Connexion
mongoengine.connect(settings.MONGO_DATABASE_NAME)

