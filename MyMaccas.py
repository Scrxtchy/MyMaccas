import requests, json
from base64 import b64encode
from hashlib import md5

config = {
	"username":"h@ck.the.gibson", #email
	"password":"GOD", #password
	"postcode":"3000", #store postcode	TODO: May get more than one town per lookup
	"nonce": "happybaby",				TODO: This also applies to multiple stores 
	"versionId": "0.0.1.I",
	"application": "MOT"
}

api = requests.session()
api.headers['mcd_apikey'] = "AUandPROD2TIHIKU895DF68RT23ERIAU"
api.headers['MarketID'] = "AU.PROD2"
api.headers['X-NewRelic-ID'] = "UwUDUVNVGwIGVlVVDwkH" #UwU
api.headers['User-Agent'] = "User-Agent: Dalvik/2.1.0 (Linux; U; Android 8.1.0; Nexus 5X Build/OPM1.171019.011)"

def get(endpoint, params=None, headers=None):
	return api.get("https://ap.api.mcd.com/v3" + endpoint, params=params, headers=headers)

def post(endpoint, body=None, headers=None):
	return api.post("https://ap.api.mcd.com/v3" + endpoint, json=body, headers=headers)

def computeHash(Id, Version, Nonce):
	return b64encode(md5("=PA64E47237FC34714AF852B795DAF8DEC\\o/{0}o|o{1}=/{2}".format(Version, Id, Nonce).encode('utf-8')).hexdigest().encode('utf-8')).decode('utf-8')

def login(username, password):			TODO: Catch bad logins
	resp = post('/customer/session/sign-in-and-authenticate', body={
	"marketId": "AU",
	"application": config["application"],
	"languageName": "en-AU",
	"platform": "android",
	"versionId": config["versionId"],
	"nonce": config["nonce"],
	"hash": computeHash(config["application"], config["versionId"], config["nonce"]),
	"userName": username,
	"password": password,
	"newPassword": None})
	return resp

def postcodeLookup(postcode):
	return requests.get('http://v0.postcodeapi.com.au/suburbs/{0}.json'.format(postcode)).json() #100 unique requests per hour, per IP

def getStores(latitude, longitude):
	return get("/restaurant/location", params={
		"filter":"search",
		"query":'{"market":"AU","pageSize":"25","local":"en-AU","generalStoreStatusCode":"OPEN,TEMPCLOSE,RENOVATION","locationCriteria":{"latitude":'+str(latitude)+',"longitude":'+str(longitude)+',"distance":"20"}}'
		})
	
def offers(latitude, longitude, storeid=None):
	resp = get('/customer/offer', params={
		"marketId": "AU",
		"application": config["application"],
		"languageName": "en-AU",
		"platform": "android",
		"userName": config["username"],
		"latitude": latitude,
		"longitude": longitude,
		"storeid": storeid
		})
	return resp

def redeemCode(offerId, storeId):
	return post('/customer/offer/redemption', body={
		"marketId": "AU",
		"application": config["application"],
		"languageName": "en-AU",
		"platform": "android",
		#"versionId": config["versionId"],
		#"nonce": config["nonce"],
		#"hash": computeHash(config["application"], config["versionId"], config["nonce"]),
		"offersIds": [offerId],
		"storeId": int(storeId),
		"userName": config["username"]
		})

import pprint

x = login(config["username"], config["password"])
api.headers["Token"] = x.json()["Data"]["AccessData"]["Token"]
location = postcodeLookup(config["postcode"])


stores = getStores(location[0]['latitude'], location[0]['longitude']).json()
offers  = offers(stores[0]['address']['location']['lat'], stores[0]['address']['location']['lon'], "[{0}]".format(stores[0]['identifiers']['storeIdentifier'][0]['identifierValue'])).json()['Data']

for index, offer in enumerate(offers):	#TODO: Start from 1 not 0?
	print("Deal #{}: {}".format(index, offer['Name']))
	print("----------")

choice = int(input("Which deal to redeem: ")) 

x = redeemCode(str(offers[choice]['Id']), stores[0]['identifiers']['storeIdentifier'][0]['identifierValue']).json()['Data']

print('Order Code: ' + x['RandomCode'])
