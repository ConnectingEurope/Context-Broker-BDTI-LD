import socket
import re
import requests
import telnetlib
from cb_bdti.errors.core.handler import *
from cb_bdti.config.constants import *



class Validators(object):
	def __init__(self):
		"""
		All the classes methods should be classmethod, making it unnecessary to instanciate the class whatsoever
		"""
		pass

	@staticmethod
	def is_ip(host):
		try:
			socket.inet_aton(host)
			return True
		except socket.error:
			return False

	@staticmethod
	def is_valid_url(host):
		"""
		Check if host passed is a valid url.

		:param str host:
		:return: if host is valid
		:rtype: bool
		"""
		regex = re.compile(
			r'^(?:http|ftp)s?://'  # http:// or https://
			r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
			r'localhost|'  # localhost...
			r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
			r'(?::\d+)?'  # optional port
			r'(?:/?|[/?]\S+)$', re.IGNORECASE)

		return re.match(regex, host) is not None

	@staticmethod
	def check_orion_url(orion_url):
		"""
		Check if some url have a valid Orions subscription service. Otherwise is an error

		:param str orion_url: url of orion
		:return: if a is valid url
		:rtype: bool
		"""
		try:
			response = requests.get(orion_url, timeout=3)
			if (response.status_code != 200):
				raise OrionNotReachable(orion_url)
		except:
			raise OrionNotReachable(orion_url)


	@staticmethod
	def check_cygnus_notifications(cygnus_host):
		"""
		Check if cygnus is able to receive notifications. If not raise an error

		:param str cygnus_host: cygnus notification url.
		:return: None
		"""
		try:
			telnetlib.Telnet(cygnus_host, CYGNUS_NOTIFICATION_PORT, 3)
		except:
			raise CygnysNotReachable(cygnus_host)

	@staticmethod
	def validate_types(types, datamodel):
		"""
		Validate if types of some datamodel that is part of 12 Fiware datamodels are correctly.
		If not raise an error

		:param str types: types indicated for datamodel in production.ini
		:param str datamodel: datamodel indicated in iot.datamodels in production.ini
		:return: None
		"""
		if not types:
			raise FieldNotInformed(DATA_MODEL_TYPES, datamodel)

		valid = True
		valid_types = []
		for fiware_datamodel in FIWARE_DATAMODELS:
			if fiware_datamodel in datamodel:
				valid_types = FIWARE_DATAMODELS[fiware_datamodel]
				valid = set(types.split()).issubset(valid_types)
				break
		if not valid:
			raise NotValidTypes(datamodel, valid_types)

	@staticmethod
	def validate_throttling(throttling, datamodel):
		"""
		Validate if throttling for some datamodel is an integer.

		:param str throttling: value of throttling indicated in production.ini
		:param str datamodel: name of datamodel
		:return: None
		"""
		if not throttling:
			return
		try:
			int(throttling)
		except:
			raise NotValidThrottling(datamodel)

	@staticmethod
	def validate_expires(expires, datamodel):
		"""
		Validate if value of expires key for some datamodel comply ISO rule.

		:param str expires: value of expires 
		:param str datamodel: name of datamodel 
		:return: None
		"""
		if not expires:
			return
		regex = re.compile(
			r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]'
			r'|[12][0-9])(T(2[0-3]|[01][0-9]):([0-5][0-9])(:([0-5][0-9])(\.'
			r'[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?)?)?$', re.IGNORECASE
		)
		if not re.match(regex, expires):
			raise NotValidExpires(datamodel)


	@staticmethod
	def check_format_file(file_format):
		"""
		Checks if fomart file indicated in hdfs section is correct

		:param str file_format: value of format file 
		:return: None
		"""
		healthy = True if file_format in HDFS_FORMAT_FILE_LIST else False
		if not healthy:
			raise NotValidHdfsFormatFile(file_format)


	@staticmethod
	def check_hdfs_section(hdfs_dict):
		"""
		Checks if fomart file indicated in hdfs section is correct

		:param str file_format: value of format file 
		:return: None
		"""
		for key in [HDFS_HOST, HDFS_PORT, HDFS_FORMAT_FILE, HDFS_USERNAME]:
			if not hdfs_dict[key]:
				raise FieldNotInformed(key, HDFS_SECTION)

		if not hdfs_dict[HDFS_FORMAT_FILE] in HDFS_FORMAT_FILE_LIST:
			raise NotValidHdfsFormatFile(hdfs_dict[HDFS_FORMAT_FILE])