import json
import logging
from cb_bdti.config.constants import *
from cb_bdti.utils.helpers import Helpers


class CygnusConfManager(object):
	"""
	Creation manager for files that Cygnus needs to run  
	"""
	@staticmethod
	def generate_flume_agent(hdfs_dict, out_file):
		"""
		Generates a new flume agent with fields indicated in hdfs section of config file

		:param dict hdfs_dict: values of hdfs section
		:param out_file: path of where flume agent file will be writed 
		:return: None
		"""
		logging.debug('Generating Flume agent file')
		logging.debug('Loading agent file template at {path}'.format(path=TEMPLATE_AGENT))
		with open(TEMPLATE_AGENT) as file:
			config_str = file.read()

		for key, value in hdfs_dict.items():
			config_str += "{key_name} = {key_value}\n".format(key_name=MAP_AGENT_CONF[key], key_value=value)

		with open(out_file, 'w') as config_path:
			config_path.write(config_str)
			logging.debug('New Cygnus agent file created: {path}'.format(path=out_file))

		logging.debug('Flume agent generation process finished OK')

	@staticmethod
	def generate_grouping_rules(models, format_file, out_file):
		"""
		Generates a new flume grouping rules fields indicated in datamodels sections of config file

		:param dict hdfs_dict: values of hdfs section
		:param out_file: path of where grouping rules file will be writed 
		:return: None
		"""
		logging.debug('Generating grouping rules file')
		rules = {"grouping_rules": []}
		for counter, model in enumerate(models, start=1):
			logging.debug('Processing {model}'.format(model=model))
			model[DATA_MODEL_FILE_PATH] = "%s_%s" %(format_file.replace('-', '_'), model[DATA_MODEL_FILE_PATH])

			if not model[DATA_MODEL_FILE_PATH].startswith('/'):
				model[DATA_MODEL_FILE_PATH] = '/' + model[DATA_MODEL_FILE_PATH]

			fields = ["entityType"]
			regex = Helpers.get_type_pattern(model[DATA_MODEL_TYPES])
			if model[DATA_MODEL_FIWARE_SERVICEPATH]:
				fields.append("servicePath")
				regex += model[DATA_MODEL_FIWARE_SERVICEPATH]

			dic = {"id": counter,
				   "fields": fields,
				   "regex": regex,
				   "destination": model[DATA_MODEL_FILE_NAME],
				   "fiware_service_path": model[DATA_MODEL_FILE_PATH]
				   }
			rules["grouping_rules"].append(dic)

		with open(out_file, "w") as js:
			json.dump(rules, js, indent=4)
			logging.debug('New grouping rules file created: {path}'.format(path=out_file))

		logging.debug('Grouping rules generation process finished OK')
