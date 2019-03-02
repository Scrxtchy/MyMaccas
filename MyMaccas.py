import requests, json
from base64 import b64encode
from hashlib import md5
import logging
#logging.basicConfig(level=logging.DEBUG)

class MyMaccas(object):
	"""docstring for myMaccas"""
	def __init__(self, *args, **kwargs):
		#self.nonce = "happybaby"
		#self.versionId = "0.0.1.I"
		self.application = "MOT"

		self.api = requests.session()
		self.api.headers['mcd-marketId'] = "AU"
		self.api.headers['mcd-sourceapp'] = "MOT"
		self.api.headers['mcd_apikey'] = "AUDCUSANDPRODEAT932DHL2N5BXJ40KDLV5XXAU"
		self.api.headers['MarketID'] = "AU.PROD3"
		self.api.headers['X-NewRelic-ID'] = "UwUDUVNVGwIGVlVVDwkH" #UwU
		self.api.headers['mcd-locale'] = "en-AU"
		self.api.headers['mcd-apiuid'] = "644e1dd7-2a7f-18fb-b8ed-ed78c3f92c2bsd"
		self.api.headers['User-Agent'] = "User-Agent: Dalvik/2.1.0 (Linux; U; Android 8.1.0; Nexus 5X Build/OPM1.171019.011)"
	
		
	def get(self, endpoint, params=None, headers=None):
		return self.api.get("https://ap.api.mcd.com/" + endpoint, params=params, headers=headers)
	
	def post(self, endpoint, body=None, headers=None):
		return self.api.post("https://ap.api.mcd.com/" + endpoint, json=body, headers=headers)
	
	def put(self, endpoint, body=None, headers=None):
		return self.api.put("https://ap.api.mcd.com/" + endpoint, json=body, headers=headers)
	
	def computeHash(self, Id, Version, Nonce):
		return b64encode(md5("=PA64E47237FC34714AF852B795DAF8DEC\\o/{0}o|o{1}=/{2}".format(Version, Id, Nonce).encode('utf-8')).hexdigest().encode('utf-8')).decode('utf-8')
	
	def signup(self, username, password, fName, lName="-", postcode=3000, doInitialLogin=True): #Accounts have a period of time where they do not return offers. This could be 24 hours
		"""
		Signs up 
		"""
		from re import findall 
		from time import sleep
		reg = requests.session()
		reg.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
		form = reg.get('https://mcdonalds.com.au/mymaccas/register').text
		matches = findall(r'name=\"(?:csrf_test_name|timestamp)\" value=\"([0-9a-fA-F]+)\"/?>', form)
		sleep(5) #Server Processing Time, may fail anyway
		resp = reg.post('https://accounts.mcdonalds.com.au/signup', data={
			"firstname": fName,
			"lastname": lName,
			"email": username,
			"postcode": postcode,
			"password": password,
			"terms": "1",
			"usually_eat_with": "by_myself",
			"url": "",
			"timestamp": str(matches[0]),
			"csrf_test_name": str(matches[1]), 
		})

		if len(findall('Awesome', resp.text)) != 0:
			if (doInitialLogin):
				return self.loginWebsite(username, password)
			return True
		else:
			raise ValueError('Process failed, string not found')
	
	
	def login(self, username, password):
		"""
		Logs in via Application API
		"""
		resp = self.post('v2/customer/security/authentication?type=traditional', body={
		#"platform": "android",
		#"versionId": self.versionId,
		#"nonce": self.nonce,
		#"hash": self.computeHash(self.application, self.versionId, self.nonce),
		"loginUsername": username,
		"password": password,
		"type": "email"
		#"newPassword": None
		})
		try:
			#import pdb; pdb.set_trace()
			self.api.headers["Token"] = resp.json()['details']['token']
			self.username = username
			self.password = password
		except Exception as err:
			print("Login Failed")
			raise err
		return resp
	
	def loginMaccasPlay(self, username, password):
		"""
		Returns a requests response object
		Primarily used to validate accounts
		"""
		return self.loginWebsite(username, password, url="https://maccasplay.com.au/account/signin")

	def loginWebsite(self, username, password, url="https://mcdonalds.com.au/signin"):
		"""
		Returns a requests response object
		Primarily used to validate accounts
		"""
		from re import findall 
		from time import sleep
		reg = requests.session()
		reg.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
		form = reg.get('https://maccasplay.com.au/account/signin').text
		matches = findall(r'name=\"(?:csrf_test_name|timestamp)\" value=\"([0-9a-fA-F]+)\"/?>', form)
		sleep(5) #Server Processing Time, may fail anyway
		try:
			resp = reg.post(url, data={
				"email": username,
				"password": password,
				"url": "",
				"timestamp": str(matches[0]),
				"csrf_test_name": str(matches[1]), 
			})
		except Exception as e:
			print('Request Failure, trying again in five seconds')
			sleep(5)
			resp = reg.post(url, data={
				"email": username,
				"password": password,
				"url": "",
				"timestamp": str(matches[0]),
				"csrf_test_name": str(matches[1]), 
			})
		return resp

	def logout(self):
			del self.api.headers["Token"]
			self.username = None
			self.password = None
	
	def postcodeLookup(self, postcode):
		return requests.get('http://v0.postcodeapi.com.au/suburbs/{0}.json'.format(postcode)).json() #100 unique requests per hour, per IP
	
	def getStores(self, latitude, longitude):
		return self.get("v3/restaurant/location", params={
			"filter":"search",
			"query":'{"market":"AU","pageSize":"25","local":"en-AU","generalStoreStatusCode":"OPEN,TEMPCLOSE,RENOVATION","locationCriteria":{"latitude":'+str(latitude)+',"longitude":'+str(longitude)+',"distance":"20"}}'
			})
		
	def getOffers(self, latitude, longitude, storeid=None):
		"""
		Returns a list of offers
		"""
		resp = self.get('v3/customer/offer', params={
			"marketId": "AU",
			"application": self.application,
			"languageName": "en-AU",
			"platform": "android",
			"userName": self.username,
			"latitude": latitude,
			"longitude": longitude,
			"storeid": storeid
			})
		return resp
	
	def redeemCode(self, offerId, storeId):
		"""
		Returns a redemption object
		"""
		return self.post('/customer/offer/redemption', body={
			"marketId": "AU",
			"application": self.application,
			"languageName": "en-AU",
			"platform": "android",
			#"versionId": config["versionId"],
			#"nonce": config["nonce"],
			#"hash": computeHash(config["application"], config["versionId"], config["nonce"]),
			"offersIds": [offerId],
			"storeId": int(storeId),
			"userName": self.username
			})
	
	def initialLogin(self, username, password):
		"""
		Untested shit
		"""
		profile = self.login(username, password).json()["Data"]["CustomerData"]
		return self.post('customer/profile', body={
			'marketId': 'AU',
			'application': 'MOT',
			'languageName': 'en-AU',
			'platform': 'android',
			'userName': profile["UserName"],
			'password': password,
			'firstName': profile["FirstName"],
			'lastName': profile["LastName"],
			'middleName': profile["MiddleName"],
			'nickName': profile["NickName"],
			'mobileNumber': '',
			'emailAddress': username,
			'receivePromotions': False,
			'customerId': profile["CustomerID"],
			'yearOfBirth': profile["YearOfBirth"],
			'monthOfBirth': profile["MonthOfBirth"],
			'dayOfBirth': profile["DayOfBirth"],
			'cardItems': [],
			'isPrivacyPolicyAccepted': True,
			'isTermsOfUseAccepted': True,
			'zipCode': profile["ZipCode"],
			'subscribedToOffer': True,
			'optInForCommunicationChannel': False,
			'optInForSurveys': False,
			'optInForProgramChanges': False,
			'optInForContests': False,
			'optInForOtherMarketingMessages': False,
			'notificationPreferences': {'AppNotificationPreferences_Enabled': True,
			'AppNotificationPreferences_EverydayOffers': True,
			'AppNotificationPreferences_LimitedTimeOffers': True,
			'AppNotificationPreferences_OfferExpirationOption': 0,
			'AppNotificationPreferences_PunchcardOffers': True,
			'AppNotificationPreferences_YourOffers': True,
			'EmailNotificationPreferences_Enabled': True,
			'EmailNotificationPreferences_EverydayOffers': True,
			'EmailNotificationPreferences_LimitedTimeOffers': True,
			'EmailNotificationPreferences_OfferExpirationOption': 0,
			'EmailNotificationPreferences_PunchcardOffers': True,
			'EmailNotificationPreferences_YourOffers': True},
			'preferredOfferCategories': [],
			'preferredNotification': 1,
			'PreferredLanguage': 'en',
			'source': 'GMA',
			'restaurantId': '',
			'deviceToken': '',
			'deviceId': '',
			'socialNetworkProvider': None,
			'systemLanguage': 'en',
			'systemVersion': '8.1.0',
			'timeZone': 'Australia/Sydney',
			'systemName': 'Android',
			'title': None,
			'gender': None,
			'sourceProgram': 'GMA',
			'deviceBuildId': 4,
			'userKey': profile["CustomerID"],
			'uuid': None,
			'deviceName': 'Nexus 5X',
			'deviceBrand': 'google',
			'deviceManufacturer': 'LGE',
			'mobilePhone': '',
			'Opt-Ins': [{
				'AcceptanceTimestamp': None,
				'Status': True,
				'Type': 'OPT_IN_DISPLAYNAME'}]
			})

