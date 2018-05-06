import requests
import json
import os
import random
from time import sleep

RESULTS = 'orders.txt' # Text file where orders are located in email:ordernumber format
DELAY = 0 # Delay in seconds between checking orders
PROXY_FILE = 'proxies.txt' # Text file where proxies are located in ip:host or ip:host:user:pass format

WIDTH = 30 # Don't touch

def center(string, spacer):
	count = ((WIDTH - len(string)) / 2)
	if count > 0:
		return (count - 1) * spacer + ' ' + string + ' ' + (count - 1) * spacer
	else:
		return string

def header():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')
	print center('Nike Order Checker', '~')
	print center('Made by @DefNotAvg', '~')
	print ''

def smart_sleep(DELAY):
	for a in xrange (DELAY, 0, -1):
		print 'Sleeping for {} seconds...\r'.format(str(a)),
		sleep(1)
	print 'Sleeping for {} seconds complete!'.format(str(DELAY))

def set_proxy(PROXIES):
	if PROXIES != []:
		proxy = random.choice(PROXIES)
		proxies = {
		  'http': 'http://{}'.format(proxy),
		  'https': 'http://{}'.format(proxy),
		}
	else:
		proxies = {
		  'http': None,
		  'https': None,
		}
	return proxies
	
header()
with open(RESULTS, 'r') as myfile:
	text = myfile.read()
info = [item for item in text.split('\n') if item != '' and len([field for field in item.split(':') if item != '']) > 1]
statuses = []
if len(info) > 0:
	print center('Gathering order status for {} orders...\n'.format(str(len(info))), ' ')
else:
	print center('No orders found in {}'.format(RESULTS), ' ')
sleep(1)
try:
	with open(PROXY_FILE, 'r') as myfile:
		PROXIES = ['{}:{}@{}:{}'.format(PROXY.split(':')[2], PROXY.split(':')[3], PROXY.split(':')[0], PROXY.split(':')[1]) if PROXY != '' and PROXY.count(':') == 3 else PROXY for PROXY in myfile.read().split('\n') if PROXY != '']
except:
	with open(PROXY_FILE, 'w') as myfile:
		PROXIES = myfile.write('')
	PROXIES = []
if PROXIES == []:
	proxies = set_proxy(PROXIES)
for i in range(0,len(info)):
	header()
	print '[{}/{}] Gathering order status...'.format(str(i + 1), str(len(info)))
	line = info[i]
	if PROXIES != []:
		proxies = set_proxy(PROXIES)
	session = requests.Session()
	order = line.split(':')
	email = order[0]
	order_number = order[1]
	headers = {
	    'origin': 'https://secure-store.nike.com',
	    'accept-encoding': 'gzip, deflate, br',
	    'accept-language': 'en-US,en;q=0.9',
	    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	    'content-type': 'application/x-www-form-urlencoded',
	    'accept': '*/*',
	    'referer': 'https://secure-store.nike.com/common/content/endpoint.html',
	    'authority': 'secure-store.nike.com',
	    'x-requested-with': 'XMLHttpRequest',
	}
	data = [
	  ('action', 'getAnonymousOrderDetails'),
	  ('lang_locale', 'en_US'),
	  ('country', 'US'),
	  ('endpoint', 'getAnonymousOrderDetails'),
	  ('orderId', order_number),
	  ('email', email),
	  ('deviceType', 'desktop'),
	]
	response = session.post('https://secure-store.nike.com/nikestore/html/services/orders/orderDetails', headers=headers, data=data, proxies=proxies)
	try:
		status = json.loads(response.content)['data']['order']['status']
	except:
		status = 'Error getting order status'
	tracking_number = ''
	expected_delivery = ''
	if status == 'Shipped':
		try:
			status = json.loads(response.content)['data']['order']['shippingGroups'][0]['status']
			if status != 'Delivered':
				for item in json.loads(response.content)['data']['order']['shippingGroups']:
					try:
						tracking_number = item['trackingNumber']
					except:
						pass
				for field in item['commerceItems']:
					try:
						expected_delivery = field['expectedDeliveryDate']
					except:
						pass
		except:
			tracking_number = 'Error getting tracking number'
	statuses.append(status)
	if len(order) > 2:
		order[2] = status
		final = ':'.join(order[:3])
	else:
		order.append(status)
		final = ':'.join(order[:3])
	if tracking_number != '':
		if len(order) > 3:
			order[3] = tracking_number
			final = ':'.join(order[:4])
		else:
			order.append(tracking_number)
			final = ':'.join(order[:4])
	if expected_delivery != '':
		if len(order) > 4:
			order[4] = expected_delivery
			final = ':'.join(order[:5])
		else:
			order.append(expected_delivery)
			final = ':'.join(order[:5])
	with open(RESULTS, 'r') as myfile:
		text = myfile.read()
	with open(RESULTS, 'w') as myfile:
		myfile.write(text.replace(line, final))
	if DELAY > 0 and i != len(info) - 1:
		print 'Order {}: {}\n'.format(order_number, status)
		smart_sleep(DELAY)
if len(info) > 0:
	header()
	print center('Output', '~')
	print ''
	for category in sorted(list(set(statuses))):
		print center('{}: {}'.format(category, str(sum(category == status for status in statuses))), ' ')
	with open(RESULTS, 'r') as myfile:
		text = myfile.read()
	info = [item for item in text.split('\n') if item != '' and len([field for field in item.split(':') if item != '']) > 1]
	sorted_text = ''
	for category in sorted(list(set(statuses))):
		sorted_text += category + '\n\n'
		for item in info:
			if item.split(':')[2] == category:
				sorted_text += item + '\n'
		sorted_text += '\n'
	with open(RESULTS, 'w') as myfile:
		myfile.write(sorted_text)
	raw_input('\n' + WIDTH * '~' + '\n\n' + center('Output saved to {}'.format(RESULTS), ' ') + '\n\n' + center('Press enter to quit', ' '))
else:
	raw_input('\n' + center('Press enter to quit', ' '))

quit()