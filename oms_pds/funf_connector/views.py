#-*- coding: utf-8 -*- 
from django.shortcuts import render_to_response
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json_simple
import dbmerge, os
import dbdecrypt
import decrypt
import sqlite3
import json, ast
from oms_pds import settings
from oms_pds.authorization import PDSAuthorization
from oms_pds.pds.models import Profile
from oms_pds.pds.internal import getInternalDataStore, InternalDataStore
import pdb

upload_dir = settings.SERVER_UPLOAD_DIR

def insert_pds(internalDataStore, token, pds_json):
    internalDataStore.saveData(pds_json)

def write_key(request):
    '''write the password used to encrypt funf database files to your PDS'''
    response = None
    try:
        token = request.GET['bearer_token']
        scope = "funf_write"
        scope = AccessRange.objects.get(key="funf_write")
        authenticator = Authenticator(scope=scope)
        try:
            # Validate the request.
            authenticator.validate(request)
        except AuthenticationException:
            # Return an error response.
            return authenticator.error_response(content="You didn't authenticate.")
        profile = authenticator.user.get_profile()
        profile.funf_password = json.loads(request.raw_post_data)['key']
        profile.save()
        response_content = json.dumps({'status':'success'})
        response = HttpResponse(content=response_content)        
    except Exception as ex:
        print "EXCEPTION:"
        print ex
        response = HttpResponseBadRequest('failed to write funf key')
    return response
 
def data(request):
    '''decrypt funf database files, and upload them to your PDS'''
    result = {}
    if request.method == 'GET':
        template = {'token':request.GET['bearer_token']}
        return HttpResponse("File not found", status=404)
    pds = None
    #scope = AccessRange.objects.get(key="funf_write")
    authorization = PDSAuthorization("funf_write", audit_enabled=True)
    if (not authorization.is_authorized(request)):
        return HttpResponse("Unauthorized", status=401)

    scope = 'funf_write'
    token = request.GET['bearer_token']
    datastore_owner_uuid = request.GET["datastore_owner__uuid"]
    datastore_owner, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
    print "Creating IDS for %s" % datastore_owner_uuid
    #internalDataStore = getInternalDataStore(datastore_owner, "MGH smartCATCH", "Social Health Tracker", "Activity", token)
    internalDataStore = getInternalDataStore(datastore_owner, "MGH smartCATCH", "Social Health Tracker", token)
    #collection = connection[datastore_owner.getDBName()]["funf"]
    funf_password = "changeme"
    key = decrypt.key_from_password(str(funf_password))
    print "PDS: set_funf_data on uuid: %s" % datastore_owner_uuid

    for filename, file in request.FILES.items():
        try:
            try:
                file_path = upload_dir + file.name
                write_file(str(file_path), file)
            except Exception as ex:
                print "failed to write file to "+file_path+".  Please make sure you have write permission to the directory set in settings.SERVER_UPLOAD_DIR"
            dbdecrypt.decrypt_if_not_db_file(file_path, key)
            con = sqlite3.connect(file_path)
            cur = con.cursor()
            cur.execute("select name, value from data")
            inserted = []
            for row in cur:
                name = convert_string(row[0])
                json_insert = clean_keys(json.JSONDecoder().decode(convert_string(row[1])))
                #print json_insert$
                # Insert into PDS$
                pds_data= {}
                pds_data['time']=json_insert.get('timestamp')
                pds_data['value']=json_insert
                pds_data['key']=name
                insert_pds(internalDataStore, token, pds_data)
                inserted.append(convert_string(json_insert)+'\n')
            result = {'success': True, 'rows_inserted': len(inserted)}
            print "Inserted %s rows" % len(inserted)
        except Exception as e:
            print "Exception from funf_connector on pds:"
            print "%s"%e
            result = {'success':False, 'error_message':e.message}
        finally:
            response_dict = {"status":"success"}
    return HttpResponse(json.dumps(result), content_type='application/json')

    
TMP_FILE_SALT = '2l;3edF34t34$#%2fruigduy23@%^thfud234!FG%@#620k'
TEMP_DATA_LOCATION = "/data/temp/"

def random_hash(pk):
    randstring = "".join([random.choice(string.letters) for x in xrange(20)])
    hash = hashlib.sha224(TMP_FILE_SALT + pk + randstring).hexdigest()[0:40]
    return hash

    
def direct_decrypt(file, key, extension=None):
    assert key != None
    decryptor = DES.new(key) #TODO to make sure the key is 8 bytes long. DES won't accept a shorter key
    encrypted_data = file.read()
    data = decryptor.decrypt(encrypted_data)
    return data


def write_file(filename, file):
    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
    filepath = os.path.join(upload_dir, filename)
    if os.path.exists(filepath):
        backup_file(filepath)
    with open(filepath, 'wb') as output_file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            output_file.write(chunk)

def backup_file(filepath):
    shutil.move(filepath, filepath + '.' + str(int(time.time()*1000)) + '.bak')


def convert_string(s):
    return "%s" % s

def clean_keys(d):
    '''replace all "." with "-" and force keys to lowercase'''
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = clean_keys(v)
	if isinstance(v, list):
	    for idx,i in enumerate(v):
		if isinstance(i, dict):
       		    v[idx] = clean_keys(i)	
        new[k.replace('.', '-').lower()] = v
    return new


