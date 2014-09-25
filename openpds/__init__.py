#from backends.mongo import InternalDataStore
import settings
import importlib

def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

def getInternalDataStore(profile, app_id, lab_id, token):
    module = settings.PDS_BACKEND["ENGINE"]
    c = class_for_name(module, "getInternalDataStore")
    return c(profile, app_id, lab_id, token)

