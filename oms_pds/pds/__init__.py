import mongoengine
import OMS_PDS.settings as settings

# Connexion
mongoengine.connect(settings.MONGO_DATABASE_NAME)

