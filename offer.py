import csv
from time import sleep
import myMaccas
from random import choice
#from pprint import pprint
userscsv = open('users.csv')
users = csv.reader(userscsv)
import pdb
mc = myMaccas.MyMaccas()
location = mc.postcodeLookup(3000)

users = list(users).copy()

def getOffer():
	print("getting offers")
	offers = mc.getOffers(stores[0]['address']['location']['lat'], stores[0]['address']['location']['lon'], "[{0}]".format(stores[0]['identifiers']['storeIdentifier'][0]['identifierValue']))
	if len(offers.json()['Data']) == 0:
		raise Exception("No Offers, logging in with another user")
	return offers.json()['Data']

def login():
	row = choice(list(users))
	print("logging in as {}".format(row[2]))
	mc.login(row[0], row[1])
	
login()

stores = mc.getStores(location[0]['latitude'], location[0]['longitude']).json()
while True:
	try:
		offers = getOffer()
	except Exception as e:
		print(e)
		mc.logout()
		login()
		continue
	break

for index, offer in enumerate(offers):  #TODO: Start from 1 not 0?
        print("Deal #{}: {}".format(index, offer['Name']))
        print("----------")

choice = int(input("Which deal to redeem: "))

x = mc.redeemCode(str(offers[choice]['Id']), stores[0]['identifiers']['storeIdentifier'][0]['identifierValue']).json()['Data']

print('Order Code: ' + x['RandomCode'])

mc.logout()
userscsv.close()
