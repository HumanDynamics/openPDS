from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel
import json



class Policy():

    def __init__(self, scope, purpose, role, sharinglevel):
	self.scope = scope
	self.purpose = purpose
	self.role = role
	self.sharinglevel = sharinglevel
	

    def getPolicyJSON(self):
	policy_json ={'scope' : self.scope,
			'purpose' : self.purpose,
			'role' : self.role,
			'sharinglevel' : self.sharinglevel}
	return policy_json   

