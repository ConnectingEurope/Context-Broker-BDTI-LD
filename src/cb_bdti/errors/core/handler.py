from cb_bdti.config.constants import *


class OrionNotReachable(Exception):
	def __init__(self, url):
		"""
		This exception is called when the Orion's subscription service is not reachable

		:param str url: URL to reach Orion
		"""
		message = "Orion's subscription service is not reachable at {url}".format(url=url)
		super(OrionNotReachable, self).__init__(message)


class CygnysNotReachable(Exception):
	def __init__(self, url):
		"""
		This exception is called when the Cygnus's notification service is not reachable

		:param str url: URL to reach Cygnus
		"""
		message = 'Cygnus notification service is not reachable at {url}'.format(url=url)
		super(CygnysNotReachable, self).__init__(message)

class CygnysNotReachableSSH(Exception):
	def __init__(self):
		"""
		This exception is called when the Cygnus's notification service is not reachable

		:param str url: URL to reach Cygnus
		"""
		message = 'Cygnus host is not reachable via SSH'
		super(CygnysNotReachableSSH, self).__init__(message)


class SectionKeyError(Exception):
	def __init__(self, section, key):
		"""
		This exception is called if a key is not present in the given section

		:param str section: a section of the configuration file
		:param str key: a key of a section of the configuration file
		"""
		message = '"{key}" key is not present in "{section}" section'.format(key=key, section=section)
		super(SectionKeyError, self).__init__(message)


class NoDataModelsIntegrated(Exception):
	def __init__(self):
		"""
		This exception is called if a key is not present in the given section

		:param str section: a section of the configuration file
		:param str key: a key of a section of the configuration file
		"""
		message = 'You did not specify any Data Model for {datamodels} key in config file'.format(datamodels=FIWARE_DATAMODELS)
		super(NoDataModelsIntegrated, self).__init__(message)


class HdfsNotReachable(Exception):
	def __init__(self, host, port, remotely, cygnus_ip):
		"""
		This exception is called if the HDFS cannot be reached with the given parameters

		:param str host: HDFS host
		:param str port:  HDFS port
		:param bool remotely: indicates if the connection to HDFS is a remote connection
		:param str cygnus_ip: Cygnus IP if connection is remote
		"""
		message = 'HDFS is not reachable. Unable to connect to {host}:{port}'.format(host=host, port=port)
		message += " from Cygnus ({cygnus_ip})".format(cygnus_ip=cygnus_ip)
		super(HdfsNotReachable, self).__init__(message)


class NotValidHdfsFormatFile(Exception):
	def __init__(self, format_file):
		"""
		This exception is called if a not valid format file is provided

		:param str format_file: the format file
		"""
		message = '"%s" file format is not valid. Allowed file formats: %s' % (
			format_file, ", ".join(HDFS_FORMAT_FILE_LIST))
		super(NotValidHdfsFormatFile, self).__init__(message)


class CygnusImageNotFound(Exception):
	def __init__(self):
		"""
		This exception is called if the dfocker image from Cygnus is not found
		"""
		message = 'Docker image from Cygnus ({cygnus_image_name}) was not found'.format(cygnus_image_name=CYGNUS_IMAGE_NAME)
		super(CygnusImageNotFound, self).__init__(message)


class NotValidThrottling(Exception):
	def __init__(self, datamodel):
		"""
		This exception is called if a datamodel contains an invalid throttling value

		:param str datamodel: the name of a datamodel
		"""
		message = 'Not valid throttling for {datamodel} Data Model. It must be an integer value'.format(datamodel=datamodel)
		super(NotValidThrottling, self).__init__(message)


class NotValidExpires(Exception):
	def __init__(self, datamodel):
		"""
		This exception is called if a datamodel contains an invalid expiration value

		:param str datamodel: the name of a datamodel
		"""
		message = 'Not valid expires for {datamodel} Data Model. Must be in ISO8601 format. E.g. 2020-01-01, 2020-01-01T10:10.'.format(datamodel=datamodel)
		super(NotValidExpires, self).__init__(message)


class NotValidTypes(Exception):
	def __init__(self, datamodel, valid_types):
		"""
		This exception is called if a datamodel contains an invalid types value

		:param str datamodel: the name of a datamodel
		:param valid_types: types allowed for a datamodel
		"""
		message = 'Not valid types for %s Data Model. Must be one or more of these values: %s' % (datamodel, ', '.join(valid_types))
		super(NotValidTypes, self).__init__(message)


class CreateSubscriptionError(Exception):
	def __init__(self, status_code):
		"""
		This exception is called if a subscription for a datamodel cannot be created

		:param str url: the URL of the subscription
		"""
		message = 'Orion request subscription failed. Code error: {status_code}'.format(status_code=status_code)
		super(CreateSubscriptionError, self).__init__(message)

class DeleteSubscriptionError(Exception):
	def __init__(self, data_model, url, msg=None):
		"""
		This exception is called if a subscription for a datamodel cannot be deleted

		:param str url: the URL of the subscription
		"""
		message = 'Error trying to delete a {datamodel} subscription at {url}'.format(datamodel=data_model, url=url)
		message = '%s. %s'%(message, msg) if msg else message
		super(DeleteSubscriptionError, self).__init__(message)

class NotValidHost(Exception):
	def __init__(self, type_host, host):
		"""
		This exception is called when an invalid host and type host are given

		:param str type_host: type host
		:param str host: name of the host
		"""
		message = 'Not valid %s host: %s' %(type_host, host if host else 'empty host')
		super(NotValidHost, self).__init__(message)

class DataModelNotIntegrated(Exception):
	def __init__(self, datamodel):
		"""
		This exception is called when attempting to modify or delete
		a datamodel that has not been previosuly implemented

		:param str datamodel: the name of a datamodel
		"""
		message = 'The {datamodel} Data Model has not been previously integrated'.format(datamodel=datamodel)
		super(DataModelNotIntegrated, self).__init__(message)

class FieldNotInformed(Exception):
	def __init__(self, key, section):
		"""
		This exception is called when attempting to integrate
		a datamodel not included in the configuration file

		:param str datamodel: the name of a datamodel
		"""
		message = "{key} key is not informed in {section} section".format(key=key, section=section)
		super(FieldNotInformed, self).__init__(message)

class DataModelNotPresent(Exception):
	def __init__(self, datamodel):
		"""
		This exception is called when attempting to integrate
		a datamodel not included in the configuration file

		:param str datamodel: the name of a datamodel
		"""
		message = 'There is no {datamodel} section in the configuration file' .format(datamodel=datamodel)
		super(DataModelNotPresent, self).__init__(message)
