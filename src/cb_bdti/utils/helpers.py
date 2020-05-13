import os.path
import sys
from cb_bdti.utils.validators import Validators
from datetime import datetime
from cb_bdti.errors.core.handler import *
from cb_bdti.config.constants import *

class Helpers(object):
	def __init__(self):
		"""
		All the classes methods should be classmethod, making it unnecessary to instanciate the class whatsoever
		"""
		pass

	@staticmethod
	def get_orion_url(host):
		"""
		Makes a valid orion url in order to access to the subscription service

		:param str host: orion host given in conf.ini
		:return: orion's subscriptions service url
		"""
		if not host:
			raise FieldNotInformed(ORION_HOST, MAIN_SECTION)
		if Validators.is_ip(host):
			orion_url = "http://{host}:1026/ngsi-ld/v1/subscriptions".format(host=host)
		elif Validators.is_valid_url(host):
			orion_url = os.path.join(host, "ngsi-ld/v1/subscriptions")
		else:
			raise NotValidHost('Orion LD', host)
		return orion_url

	@staticmethod
	def get_cygnus_url(host):
		"""
		Makes a valid cygnus url in order to the receive orion's notifications

		:param host: cygnus host given in conf.ini
		:return: cygnus's target norifications url
		:rtype: str
		"""
		if not host:
			raise FieldNotInformed(CYGNUS_HOST, MAIN_SECTION)
		if Validators.is_ip(host):
			cygnus_url = "http://{host}:5050/notify".format(host=host)
		elif Validators.is_valid_url(host):
			cygnus_url = "{host}:5050/notify".format(host=host)
		else:
			raise NotValidHost('Cygnus', host)
		return cygnus_url

	@staticmethod
	def get_type_pattern(type):
		"""
		Get regex for datamodels type

		:param str type: Type extracted from production.ini
		:return: regex from types
		:rtype: str
		"""
		return "(%s)" %"|".join(type.split())

	@staticmethod
	def get_description(data_model):
		"""
		Makes a subscription description

		:param data_model: Name of datamodel
		:return: the description
		:rtype: str
		"""
		return "Notify Cygnus of all context changes about {datamodel} datamodel".format(datamodel=data_model)

	@staticmethod
	def get_config_path(path_from_option):
		"""
		Checks the configuration file indicated by user

		:param path_from_option: '-' by default
		:return: valid config path
		:rtype: str
		"""
		if path_from_option == '-':
			if os.path.isfile(PRODUCTION_INI):
				config_path = PRODUCTION_INI
			else:
				print(DEFAULT_INI_NOT_FOUND.format(date=datetime.strftime(datetime.now(), '%H:%M:%S'),
												   path=PRODUCTION_INI))
				sys.exit()

		elif os.path.isfile(path_from_option):
			config_path = path_from_option
		else:
			print(INI_NOT_FOUND.format(date=datetime.strftime(datetime.now(), '%H:%M:%S'),
									   path=path_from_option))
			sys.exit()
		return config_path

	@staticmethod
	def confirm_action(msg):
		done = False
		answer = ''
		while not done:
			answer = input('{message} (y/n): '.format(message=msg))
			if answer.lower() not in ('y', 'n'):
				print("Your response ('{answer}') was not one of the expected responses: y, n" .format(answer=answer))
			else:
				done = True
		return answer.lower() == 'y'