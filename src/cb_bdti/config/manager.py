from configobj import ConfigObj
from configobj import ConfigObjError
from datetime import datetime


# BDTI
from cb_bdti.config.constants import *
from cb_bdti.errors.core.handler import SectionKeyError


class ConfigManager:
	__instance = None
	__internal_instance = None
	__config_file_path = None

	def __init__(self, config_file_path):
		"""
		Instantiate the ConfigManager class. If it is not provided, it raises an error.

		:param config_file_path: Path where the config file is located.
		"""
		try:
			self.__config = ConfigObj(config_file_path, write_empty_values=True, raise_errors=True)
		except ConfigObjError as e:
			raise Exception(e.msg.strip('.'))

	@classmethod
	def get_instance(cls):

		"""
		Singleton method that retrieves the ConfigManager instance.
		If it is not instantiated yet, it does it with the __config_file_path that must be previously specified.

		:return: The ConfigManager class singleton.
		"""
		if cls.__instance is None:
			cls.__instance = ConfigManager(cls.__config_file_path)

		return cls.__instance

	@classmethod
	def get_internal_instance(cls):

		"""
		Singleton method that retrieves the ConfigManager instance.
		If it is not instantiated yet, it does it with the __config_file_path that must be previously specified.

		:return: The ConfigManager class singleton.
		"""
		if cls.__internal_instance is None:
			cls.__internal_instance = ConfigManager(INTERNAL_CONF)
		return cls.__internal_instance

	@classmethod
	def set_config_path(cls, config_file_path):
		"""
		Sets the value for the configuration file location.

		:param config_file_path: Path where the config file is.
		"""
		cls.__config_file_path = config_file_path

	@classmethod
	def _get_configparser(cls):
		"""
		Returns the previously set property __config parser.

		:return: The instance of the ConfigParser class.
		"""
		return cls.get_instance().__config

	@classmethod
	def get_sections(cls):
		"""
		:return: a list containing all the sections of the file
		"""
		return [section for section in cls._get_configparser()]

	@classmethod
	def set_value(cls, section, key, value):
		"""
		Given a section, a key and a value,
		writes the value to the corresponding section-key in the file.

		:param section: Section where the key is located in config file.
		:param key: Name of the key corresponding to the value to be added.
		:param value: value to be added in the corresponding section-key.
		"""
		cls._get_configparser()[section][key] = value

	@classmethod
	def get_value(cls, section, key):
		"""
		Reads a value from the config file.
		Raises a KeyError exception if either section or key are not preset.

		:param section: Section where the key is located in config file.
		:param key: Name of the key whose value has to be returned.
		:return: The value of the corresponding section-key.
		"""
		try:
			return cls._get_configparser()[section][key]
		except KeyError:
			raise SectionKeyError(section, key)

	@classmethod
	def is_section_present(cls, section):
		"""
		:param section: 
		:return: if some section is present in config file
		"""
		try:
			foo = cls._get_configparser()[section]
			return True
		except:
			return False

	@classmethod
	def get_section_dict(cls, section):
		"""
		Makes a dictionary from some section where the keys are the section 
		keys and values ​​are the values ​​from those keys

		:Param section: 
		:return: dict
		"""
		return cls._get_configparser()[section]

	@classmethod
	def get_hdfs_section(cls):
		"""
		Makes a dictionary from hdfs section w

		:return: dict
		"""
		dict = {HDFS_HOST: ConfigManager.get_value(HDFS_SECTION, HDFS_HOST),
				HDFS_PORT: ConfigManager.get_value(HDFS_SECTION, HDFS_PORT),
				HDFS_USERNAME: ConfigManager.get_value(HDFS_SECTION, HDFS_USERNAME),
				HDFS_FORMAT_FILE: ConfigManager.get_value(HDFS_SECTION, HDFS_FORMAT_FILE),
				HDFS_OAUTH2_TOKEN: ConfigManager.get_value(HDFS_SECTION, HDFS_OAUTH2_TOKEN),
				HDFS_KRB5_AUTH: ConfigManager.get_value(HDFS_SECTION, HDFS_KRB5_AUTH),
				HDFS_KRB5_USER: ConfigManager.get_value(HDFS_SECTION, HDFS_KRB5_USER),
				HDFS_KRB5_PASSWORD: ConfigManager.get_value(HDFS_SECTION, HDFS_KRB5_PASSWORD)}

		return dict

	@classmethod
	def _get_internal_conf_parser(cls):
		"""
		Returns the previously set property __config parser.

		:return: The instance of the ConfigParser class.
		"""
		return cls.get_internal_instance().__config


	@classmethod
	def get_internal_sections(cls):
		"""
		:return: a list containing all the sections of the file
		"""
		return [section for section in cls._get_internal_conf_parser()]

	@classmethod
	def get_datamodels_info(cls):
		return [{el: cls._get_internal_conf_parser()[el]} for el in cls._get_internal_conf_parser()]

	@classmethod
	def set_internal_datamodel(cls, datamodel, id, orion_url):
		datamodel_dict = {el: cls._get_configparser()[datamodel][el] for el in cls._get_configparser()[datamodel]}
		cls._get_internal_conf_parser()[datamodel] = datamodel_dict
		cls._get_internal_conf_parser()[datamodel][DATA_MODEL_SUBSCRIPTION_ID] = id
		cls._get_internal_conf_parser()[datamodel][ORION_SUBSCRIPTION_URL] = orion_url
		current_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		cls._get_internal_conf_parser()[datamodel][INTEGRATION_DATE] = current_date
		cls._get_internal_conf_parser()[datamodel][MODIFICATION_DATE] = ''

	@classmethod
	def update_internal_datamodel(cls, datamodel, id, orion_url):
		integration_date = cls.get_internal_value(datamodel, INTEGRATION_DATE)
		cls.remove_internal_datamodel(datamodel)
		datamodel_dict = {el: cls._get_configparser()[datamodel][el] for el in cls._get_configparser()[datamodel]}
		cls._get_internal_conf_parser()[datamodel] = datamodel_dict
		cls._get_internal_conf_parser()[datamodel][DATA_MODEL_SUBSCRIPTION_ID] = id
		cls._get_internal_conf_parser()[datamodel][ORION_SUBSCRIPTION_URL] = orion_url
		cls._get_internal_conf_parser()[datamodel][INTEGRATION_DATE] = integration_date
		current_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		cls._get_internal_conf_parser()[datamodel][MODIFICATION_DATE] = current_date

	@classmethod
	def remove_internal_datamodel(cls, datamodel):
		cls._get_internal_conf_parser().pop(datamodel)

	@classmethod
	def get_subscription_id(cls, datamodel):
		try:
			return cls._get_internal_conf_parser()[datamodel][DATA_MODEL_SUBSCRIPTION_ID]
		except:
			return None

	@classmethod
	def get_internal_value(cls, datamodel, key):
		return cls._get_internal_conf_parser()[datamodel][key]

	@classmethod
	def get_integrated_datamodels(cls):
		"""
		Makes a dictionary from some section where the keys are the section 
		keys and values ​​are the values ​​from those keys

		:Param section: 
		:return: dict
		"""
		return [cls._get_internal_conf_parser()[datamodel] for datamodel in cls._get_internal_conf_parser()]

	@classmethod
	def update_internal_conf_file(cls):
		"""
		Writes all the changes made using the set_ methods in the config file
		"""
		cls._get_internal_conf_parser().write()
