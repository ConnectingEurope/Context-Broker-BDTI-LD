import requests
import json
import logging
from cb_bdti.errors.core.handler import *

class SubscriptionManager:
	"""
	This class manages the subscriptions to the Orion CB. It implements the method
	to make a new subscription (do_subscription) and to remove a subscription (rm_dubscription)
	"""
	@staticmethod
	def do_subscription(orion_url, cygnus_url, type_pattern, fiware_service,
						fiware_servicepath, throttling, expires, description):
		"""
		Makes a Orion subscription under rules passed by arguments and
		raises an exception if it is not successful

		:param args: parameters required to make a subscription
		:return: the outcome of the subscription
		:rtype: str
		"""
		headers = {
			'Content-Type': 'application/json',
			# 'Content-Type': 'application/json' if @context in body
			'fiware-service': fiware_service,
			'fiware-servicepath': fiware_servicepath,
		}

		payload = {
			"description": description,
			"subject": {
				"entities": [
					{"idPattern": ".*",
					 "typePattern": type_pattern
					 }]},
			"notification": {
				"http": {"url": cygnus_url},
				"attrsFormat": "legacy"
			}
		}
		if (throttling):
			payload["throttling"] = throttling

		if (expires):
			payload["expires"] = expires

		logging.debug('Doing POST request to Orion: {url}'.format(url=orion_url))
		response = requests.post(orion_url, headers=headers, data=json.dumps(payload))
		if response.status_code == 201:
			logging.debug('Correct Orion response after POST request')
			return response.headers["location"].split("/")[-1]
		else:
			raise CreateSubscriptionError(response.status_code)

	@staticmethod
	def rm_subscription(data_model, orion_url, subscription_id, fiware_service):
		"""
		Removes an existing Orion subscription and
		raises an exception if the removal fails

		:param str orion_url: the Orion URL where the dubscription is made
		:param str subscription_id: the subscription ID to be removed
		:param str fiware_service: fiware service of the subscription
		:return: None
		"""
		delete_url = os.path.join(orion_url, subscription_id).replace("\\", "/")
		headers = {'fiware-service': fiware_service, }

		logging.debug('Doing delete request to Orion: {url}'.format(url=delete_url))
		response = requests.delete(delete_url, headers=headers)
		if response.status_code == 204:
			logging.debug('204 Orion response OK')
		elif response.status_code == 404:
			logging.debug('Orion request returned wrong status code')
			msg = 'Subscription ID not found: 404'
			raise DeleteSubscriptionError(data_model, orion_url, msg)
		elif response.status_code == 405:
			logging.debug('Orion request returned wrong status code')
			msg = 'Empty subscription ID'
			raise DeleteSubscriptionError(data_model, orion_url, msg)
		else:
			logging.debug('Orion request returned wrong status code')
			raise DeleteSubscriptionError(data_model, orion_url)
