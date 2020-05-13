from cb_bdti.errors.core.handler import *
from cb_bdti.config.cygnus.manager import CygnusConfManager
from cb_bdti.config.manager import ConfigManager
from cb_bdti.core.handler.manager import SubscriptionManager
from cb_bdti.utils.helpers import Helpers
from cb_bdti.core.handler.handler import DeploymentHandler
from cb_bdti.utils.validators import Validators
from cb_bdti.utils.loggers import config_logging
from cb_bdti.config.constants import *
import logging
import sys
import os
from shutil import copyfile
from datetime import datetime
from cb_bdti.config import messages as msg

class BDTI(object):
	"""
	Principal class of the CB-BDTI integration solution. Implements the main methods (integrate, 
	modify and delete)

	:param str orion_url: URL to orion supscription service
	:param str orion_url: URL to cygnus notification service
	:param DeploymentHandler deployment_handler: handler to deploy cygnus locally o remotely
	"""

	def __init__(self, file_path, delete=False, deploy=True):
		"""
		Initialization of the class. Reads the passed configuration file and carry out 
		checks on the main fields

		:param str file_path: path of configuration file
		"""
		try:
			config_logging()
			logging.debug(msg.STARTING_BDTI)
			logging.debug(msg.READING_CONFIG.format(path=file_path))
			ConfigManager.set_config_path(file_path)
			if not delete:
				logging.debug(msg.GETTING_ORION_URL)
				self.orion_url = Helpers.get_orion_url(ConfigManager.get_value(MAIN_SECTION, ORION_HOST))
				Validators.check_orion_url(self.orion_url)
				logging.debug(msg.ORION_URL.format(url=self.orion_url))

				logging.debug(msg.GETTING_CYGNUS_URL)
				self.cygnus_url = Helpers.get_cygnus_url(ConfigManager.get_value(MAIN_SECTION, CYGNUS_HOST))
				logging.debug(msg.CYGNUS_URL.format(url=self.cygnus_url))
			if deploy:
				logging.debug(msg.INSTANTIATING_HANDLER)
				self.deployment_handler = self.initialize_deploy_handler()

		except ValueError:
			print(SUDO_ERROR.format(date=datetime.strftime(datetime.now(), '%H:%M:%S')))
			sys.exit()
		except Exception as e:
			logging.error(e)
			sys.exit()

	def subscribe(self, data_model):
		"""
		Makes a orion's subscription with datamodel info passed.

		:param str data_model:datamodel passed that will be create new suscription.
		:return: id of subscription done
		:rtype: str
		"""
		types = ConfigManager.get_value(data_model, DATA_MODEL_TYPES)
		Validators.validate_types(types, data_model)
		type_pattern = Helpers.get_type_pattern(types)
		fiware_service = ConfigManager.get_value(data_model, DATA_MODEL_FIWARE_SERVICE)
		fiware_servicepath = ConfigManager.get_value(data_model, DATA_MODEL_FIWARE_SERVICEPATH)
		throttling = ConfigManager.get_value(data_model, DATA_MODEL_THROTTLING)
		Validators.validate_throttling(throttling, data_model)
		expires = ConfigManager.get_value(data_model, DATA_MODEL_EXPIRES)
		Validators.validate_expires(expires, data_model)
		# file_path file_name only for comprobations pourposes
		ConfigManager.get_value(data_model, DATA_MODEL_FILE_NAME)
		ConfigManager.get_value(data_model, DATA_MODEL_FILE_PATH)
		description = Helpers.get_description(data_model)
		subscription_id = SubscriptionManager.do_subscription(self.orion_url, self.cygnus_url, type_pattern,
															  fiware_service, fiware_servicepath, throttling,
															  expires, description)
		return subscription_id

	def create_subscriptions(self, datamodels):
		"""
		Create the subsciptions of datamodels indicated in 'iot.datamodels' key of the configuration file
		and writes the  corresponding id of the subs

		:return: None
		"""
		logging.info(msg.CREATING_NEW_SUBSCRIPTIONS)
		cont = 0
		for data_model in datamodels:
			self.check_datamodel(data_model)
			old_subscription_id = ConfigManager.get_subscription_id(data_model)
			if old_subscription_id:
				logging.warning(msg.DATAMODEL_EXISTS.format(datamodel=data_model))
				modify_datamodel = Helpers.confirm_action(msg.ASK_MODIFY)
				if modify_datamodel:
					self.modify_subscriptions([data_model])
					cont += 1
			else:
				logging.debug(msg.CREATING_SUBSCRIPTION.format(datamodel=data_model))
				new_subscription_id = self.subscribe(data_model)
				cont += 1
				logging.info(msg.SUBSCRIPTION_CREATED.format(datamodel=data_model))
				logging.debug(msg.SUBSCRIPTION_INFO.format(datamodel=data_model,
																	  subscription_id=new_subscription_id))
				ConfigManager.set_internal_datamodel(data_model, new_subscription_id, self.orion_url)
				ConfigManager.update_internal_conf_file()
				logging.debug(msg.SUBSCRIPTION_ID_SAVED.format(datamodel=data_model))

		return cont > 0

	def modify_subscriptions(self, data_models, force=False):
		"""
		Remove a subscription and creates a new one with changes done in production.ini

		:param str data_model: datamodel passed by parameter on modify and delete commands.
		:return: None
		"""
		logging.info(msg.MODIFYING_SUBSCRIPTIONS)
		cont = 0
		for data_model in data_models:
			self.check_datamodel(data_model)
			old_subscription_id = ConfigManager.get_subscription_id(data_model)
			if old_subscription_id:
				fiware_service = ConfigManager.get_internal_value(data_model, DATA_MODEL_FIWARE_SERVICE)
				try:
					SubscriptionManager.rm_subscription(data_model, self.orion_url, old_subscription_id, fiware_service)
				except Exception as e:
					if force:
						logging.warning(e)
						logging.info(msg.FORCING_DELETE.format(datamodel=data_model))
					else:
						raise (e)
				logging.debug(msg.SUBSCRIPTION_REMOVED.format(datamodel=data_model))
				new_subscription_id = self.subscribe(data_model)
				cont += 1
				logging.debug(msg.NEW_SUBSCRIPTION.format(datamodel=data_model,
																			  id=new_subscription_id))
				ConfigManager.update_internal_datamodel(data_model, new_subscription_id, self.orion_url)
				ConfigManager.update_internal_conf_file()
				logging.debug(msg.SUBSCRIPTION_ID_SAVED.format(datamodel=data_model))
				logging.info(msg.SUBSCRIPTION_MODIFIED.format(datamodel=data_model))
			else:
				logging.warning(msg.DATAMODEL_NOT_INTEGRATED.format(datamodel=data_model))
				integrate_datamodel = Helpers.confirm_action(msg.ASK_INTEGRATE)
				if integrate_datamodel:
					self.create_subscriptions([data_model])
					cont += 1
		return cont > 0

	@staticmethod
	def delete_subscription(data_model, force=False):
		"""
		Delete datamodel subscription from the orion service.

		:param str data_model: datamodel passed by parameter on modify and delete commands.
		:return: None
		"""
		logging.info('Removing subscription for {datamodel} Data Model'.format(datamodel=data_model))
		try:
			fiware_service = ConfigManager.get_internal_value(data_model, DATA_MODEL_FIWARE_SERVICE)
			orion_url = ConfigManager.get_internal_value(data_model, ORION_SUBSCRIPTION_URL)
			Validators.check_orion_url(orion_url)
			subscription_id = ConfigManager.get_subscription_id(data_model)
			logging.debug(msg.DATAMODEL_SUBSCRIPTION.format(datamodel=data_model, id=subscription_id))
			SubscriptionManager.rm_subscription(data_model, orion_url, subscription_id, fiware_service)
			ConfigManager.remove_internal_datamodel(data_model)
			ConfigManager.update_internal_conf_file()
			logging.info(msg.SUBSCRIPTION_REMOVED_SUCCESSFULLY)

		except Exception as e:
			if force:
				logging.warning(e)
				logging.info(msg.FORCING_DELETE.format(datamodel=data_model))
				ConfigManager.remove_internal_datamodel(data_model)
				ConfigManager.update_internal_conf_file()
			else:
				raise e

	def create_cygnus_agent(self, out_file):
		"""
		Will create a Flume agent that cygnus needs to run

		:param str out_file: path on where agent file will be created
		:return: None
		"""
		logging.info(msg.CREATING_AGENT)
		hdfs_section_dict = ConfigManager.get_hdfs_section()
		Validators.check_hdfs_section(hdfs_section_dict)
		CygnusConfManager.generate_flume_agent(hdfs_section_dict, out_file)
		logging.info(msg.AGENT_CREATED)


	def create_grouping_rules(self, out_file):
		"""
		Will create a Grouping Rules file that cygnus needs to store data in HDFS under files paths and names

		:param str out_file: ath on where grouping rules file will be created
		:return: None
		"""
		logging.info(msg.CREATING_GROUPING_RULES)
		data_models_dicts = ConfigManager.get_integrated_datamodels()
		format_file = ConfigManager.get_value(HDFS_SECTION, HDFS_FORMAT_FILE)
		CygnusConfManager.generate_grouping_rules(data_models_dicts, format_file, out_file)
		logging.info(msg.GROUPING_RULES_CREATED)

	@classmethod
	def initialize_deploy_handler(cls):
		"""
		Initializes the deployment handler and checks HDFS's coneection.

		:return: None
		"""
		cygnus_ip = ConfigManager.get_value(MAIN_SECTION, CYGNUS_HOST)
		if not cygnus_ip: raise FieldNotInformed(CYGNUS_HOST, MAIN_SECTION)
		cygnus_key_path = ConfigManager.get_value(MAIN_SECTION, CYGNUS_KEY_PATH)
		cygnus_username = ConfigManager.get_value(MAIN_SECTION, CYGNUS_USERNAME)
		cygnus_remotely = cygnus_key_path is not '' and cygnus_username is not ''
		logging.debug(msg.CYGNUS_MODE.format(deploy_mode='remotely' if cygnus_remotely else 'locally'))

		deployment_handler = DeploymentHandler(cygnus_remotely, cygnus_ip, cygnus_key_path, cygnus_username)

		hdfs_host = ConfigManager.get_value(HDFS_SECTION, HDFS_HOST)
		if not hdfs_host: raise FieldNotInformed(HDFS_HOST, HDFS_SECTION)
		hdfs_port = ConfigManager.get_value(HDFS_SECTION, HDFS_PORT)
		if not hdfs_port: raise FieldNotInformed(HDFS_PORT, HDFS_SECTION)
		deployment_handler.check_hdfs_connection(hdfs_host, hdfs_port)

		return deployment_handler

	@staticmethod
	def check_datamodel(datamodel):
		"""
		Checks if datamodel is previously integrate and his section is present in production.ini

		:param str datamodel: datamodel passed by parameter on modify and delete commands.
		:return: if datamodel is integrated and is present in production.ini
		:rtype: bool
		"""
		if not ConfigManager.is_section_present(datamodel):
			raise DataModelNotPresent(datamodel)

	@classmethod
	def reset(cls, force):
		try:
			config_logging()
		except ValueError:
			print(SUDO_ERROR.format(date=datetime.strftime(datetime.now(), '%H:%M:%S')))
			sys.exit()

		overwrite = Helpers.confirm_action(msg.ASK_RESET_OPTION)
		if overwrite:
			try:
				os.remove(PRODUCTION_INI)
				logging.info(msg.CONFIGURATION_FILE_REMOVED)
			except Exception as e:
				logging.error(e)
			integrated_datamodels = cls.get_datamodels(all=True)
			for datamodel in integrated_datamodels:
				try:
					cls.delete_subscription(datamodel, force)
				except Exception as e:
					logging.error(e)

	@staticmethod
	def get_config_file():
		try:
			config_logging()
		except ValueError:
			print(SUDO_ERROR.format(date=datetime.strftime(datetime.now(), '%H:%M:%S')))
			sys.exit()
		try:
			if not os.path.isfile(PRODUCTION_INI):
				copyfile(PRODUCTION_TEMPLATE, PRODUCTION_INI)
				with open(INTERNAL_CONF, 'w') as f: f.write("")
				logging.info(msg.CONFIGURATION_FILE_CREATED.format(production=PRODUCTION_INI))
			else:
				logging.error(msg.CONFIGURATION_FILE_EXISTS)
		except:
			logging.error(msg.CONFIGURATION_FILE_PERMISSION_DENIED)

	@staticmethod
	def get_datamodels(datamodels_option=None, all=False, internal=False):
		if datamodels_option:
			if datamodels_option[0] == 'all':
				if internal:
					datamodels_option = ConfigManager.get_internal_sections()
				else:
					datamodels_option = [el for el in ConfigManager.get_sections() if el
										 not in [MAIN_SECTION, HDFS_SECTION]]
		elif all:
			datamodels_option = ConfigManager.get_internal_sections()
		return datamodels_option

	def integrate(self, datamodels):
		"""
		Main method of integrate command: creates subscription, Cygnus agent and Grouping Rules and deploy Cygnus

		:return: None 
		"""
		logging.info(msg.STARTING_INTEGRATION)
		try:
			datamodels = self.get_datamodels(datamodels)
			deploy_cygnus = self.create_subscriptions(datamodels)
			if deploy_cygnus:
				self.create_cygnus_agent(AGENT)
				self.create_grouping_rules(GROUPING_RULES)
				self.deployment_handler.deploy_cygnus()
			self.deployment_handler.close_handler()
			logging.info(msg.INTEGRATION_SUCCESS)
		except Exception as e:
			logging.error(e)
			logging.info(msg.INTEGRATION_ERROR)

	def modify(self, datamodels, force=False):
		"""
		Main method of modify command: modify subscriptions, creates Cygnus agent and Grouping Rules and deploy Cygnus

		:param list datamodels: list of datamodels passed by parameter on modify command
		:return: None
		"""
		logging.info(msg.STARTING_MODIFICATION)
		try:
			datamodels = self.get_datamodels(datamodels)
			deploy_cygnus = self.modify_subscriptions(datamodels, force)
			if deploy_cygnus:
				self.create_grouping_rules(GROUPING_RULES)
				self.create_cygnus_agent(AGENT)
				self.deployment_handler.deploy_cygnus()
			self.deployment_handler.close_handler()
			logging.info(msg.MODIFICATION_SUCCESS)
		except Exception as e:
			logging.error(e)
			logging.info(msg.MODIFICATION_ERROR)

	def delete(self, datamodels, deploy, force):
		"""
		Main method of delete command: delete subscriptions and, optionally, creates Cygnus agent and 
		Grouping Rules and deploy Cygnus

		:param list datamodels: datamodels passed by parameter on delete command
		:param bool deploy: Flag that indicates if redeployment of cygnus is needed
		:return: None
		"""
		try:
			logging.info(msg.STARTING_REMOVAL)
			integrated_datamodels = self.get_datamodels(all=True)
			datamodels2delete = self.get_datamodels(datamodels, internal=True)
			for datamodel in datamodels2delete:
				if datamodel in integrated_datamodels:
					self.delete_subscription(datamodel, force)
				else:
					logging.error(msg.DATAMODEL_NOT_INTEGRATED.format(datamodel=datamodel))

			logging.info(msg.CYGNUS_DEPLOYMENT.format(deploy='' if deploy else 'not '))
			if deploy:
				self.create_cygnus_agent(AGENT)
				self.create_grouping_rules(GROUPING_RULES)
				self.deployment_handler.deploy_cygnus()
				self.deployment_handler.close_handler()
			logging.info(msg.REMOVAL_SUCCESS)

		except Exception as e:
			logging.error(e)
			logging.info(msg.REMOVAL_ERROR)
