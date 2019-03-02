import csv
from time import sleep
import myMaccas
import traceback
from random import choice
from pprint import pprint
userscsv = open('users.csv')
users = csv.reader(userscsv)
import pdb
mc = myMaccas.MyMaccas()
location = mc.postcodeLookup(3000)

users = list(users).copy()

def getOffer():
	#print("getting offers")
	offers = mc.getOffers(stores[0]['address']['location']['lat'], stores[0]['address']['location']['lon'], "[{0}]".format(stores[0]['identifiers']['storeIdentifier'][0]['identifierValue']))
	if len(offers.json()['Data']) == 0:
		users.remove(row)
		raise Exception("No Offers, logging in with another user")
	return offers.json()['Data']

def login():
	global row
	row = choice(list(users))
	#print("logging in as {}".format(row[2]))
	try:
		mc.login(row[0], row[1])
	except Exception as e:
		print(e)

def offerLoop():
	while True:
		login()
		try:
			for o in getOffer():
				if o['Name'] == deal['Name']:
					x = mc.redeemCode(str(o['Id']), stores[0]['identifiers']['storeIdentifier'][0]['identifierValue']).json()['Data']
					users.remove(row)
					return('Order Code: ' + x['RandomCode'])
			raise Exception('Deal Not Found')
	#		mc.logout()
		except Exception as e:
			#print(e)
			#traceback.print_stack()
			#mc.logout()
			#login()
			continue
		mc.logout()
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
mc.logout()

for index, offer in enumerate(offers):  #TODO: Start from 1 not 0?
        print("Deal #{}: {}".format(index, offer['Name']))
        print("----------")

deal = offers[int(input("Which deal to redeem: "))]
#dealID = None
for index in range(int(input("How Many do you wANT TO REDEEM: "))):
	p = offerLoop()
	with open('codes.txt', 'a') as c:
		c.write(p + "\n")
	print(p)
userscsv.close()
