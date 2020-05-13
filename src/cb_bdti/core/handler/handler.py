import subprocess
import logging
import time
from cb_bdti.errors.core.handler import *
from cb_bdti.config.constants import *

class DeploymentHandler:
	def __init__(self, remote, ip, key_path, user):
		"""
		This method initializes the handler for the deployment of Cygnus

		:param bool remote: True if the connection is going to be remote
		:param str ip: Cygnus IP
		:param str key_path: path of the security key
		:param str user: name of the user
		:return: None
		"""
		self.remote = remote
		self.cygnus_ip = ip
		if remote:
			logging.info('Creating SSH session to {ip}'.format(ip=ip))
			import paramiko
			self.ssh_session = paramiko.SSHClient()
			self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			try:
				self.ssh_session.connect(ip, username=user, key_filename=key_path, timeout=5)
			except:
				raise CygnysNotReachableSSH()

	def copy_files(self):
		"""
		Copies the files to Cygnus through SFTP if Cygnus is deployed remotely

		:return: None
		"""
		logging.debug('Copying files to Cygnus...')
		sftp = self.ssh_session.open_sftp()
		sftp.put(AGENT, AGENT)
		sftp.put(GROUPING_RULES, GROUPING_RULES)
		sftp.close()

	def stop_cygnus(self):
		"""
		Stops Cygnus container

		:return: None
		"""
		logging.debug('Stopping Cygnus...')
		cygnus_container = self.get_cygnus_container_id()
		logging.debug("Stopping Cygnus container: " + cygnus_container)
		if not cygnus_container:
			return
		command = 'sudo docker rm -f {container}'.format(container=cygnus_container)
		logging.debug("Excecuting command: " + command)
		if self.remote:
			stdin, stdout, stderr = self.ssh_session.exec_command(command)
			stderr.read()
		else:
			command += ' >/dev/null 2>&1'
			os.system(command)

	def run_cygnus(self):
		"""
		Starts Cygnus container

		:return: None
		"""
		logging.debug('Running Cygnus...')
		cygnus_img_id = self.get_docker_img_id()
		command = 'sudo docker run --network=host -d -v {agent}:/opt/apache-flume/conf/agent.conf:ro' \
				  ' -v {grouping_rules}:/opt/apache-flume/conf/grouping_rules.conf ' \
				  '--name cygnus {cygnus_id}'.format(agent=AGENT, grouping_rules=GROUPING_RULES,
													 cygnus_id=cygnus_img_id)
		# command = 'sudo docker run --network=host -d -v {agent}:/opt/apache-flume/conf/agent.conf:ro' \
		# 		  ' -v {grouping_rules}:/opt/apache-flume/conf/grouping_rules.conf ' \
		# 		  '--name cygnus fiware/cygnus-ngsi:1.18.0 '.format(agent=AGENT, grouping_rules=GROUPING_RULES)
		logging.debug("Excecuting command: " + command)
		if self.remote:
			stdin, stdout, stderr = self.ssh_session.exec_command(command)
			stderr.read()
		else:
			command += ' >/dev/null 2>&1'
			os.system(command)
		time.sleep(10)


	def check_hdfs_connection(self, hdfs_host, hdfs_port):
		"""
		Returns the state of the HDFS connection

		:param str hdfs_host: HDFS host
		:param str hdfs_port: HDFS port
		:return: the state of the HDFS connection
		:rtype: bool
		"""
		logging.debug("Checking HDFS connection")
		command = 'curl {host}:{port} --max-time 3'.format(host=hdfs_host, port=hdfs_port)
		if self.remote:
			stdin, stdout, stderr = self.ssh_session.exec_command(command)
			healthy = True if stdout.read() else False
		else:
			command += ' >/dev/null 2>&1'
			stdout = os.system(command)
			healthy = True if stdout == 0 else False

		if not healthy:
			raise HdfsNotReachable(hdfs_host, hdfs_port, self.remote, self.cygnus_ip)

	def get_docker_img_id(self):
		"""
		Retrieves the ID of Cygnus image

		:return: Cygnus ID image
		:rtype: str
		"""
		logging.debug("Getting Cygnus image of Docker")
		# command = 'sudo docker images {cygnus_image_name} '.format(cygnus_image_name=CYGNUS_IMAGE_NAME)
		command = 'sudo docker images %s --format="{{.ID}}"' % CYGNUS_IMAGE_NAME
		logging.debug("Excecuting command: " + command)
		if self.remote:
			stdin, stdout, stderr = self.ssh_session.exec_command(command)
			cygnus_id = stdout.read().decode("utf-8").strip()

		else:
			p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
			cygnus_id = p.stdout.read().decode("utf-8").strip().strip('"')

		if not cygnus_id:
			raise CygnusImageNotFound()

		return cygnus_id.strip()

	def get_cygnus_container_id(self):
		"""
		Retrieves the ID of Cygnus container

		:return: Cygnus ID container
		:rtype: str
		"""
		cygnus_container_id = ''
		cygnus_img_id = self.get_docker_img_id()
		command = 'sudo docker ps --all --format "{{.ID}}|{{.Image}}"'
		if self.remote:
			stdin, stdout, stderr = self.ssh_session.exec_command(command)
			containers_images = stdout.read().decode("utf-8").strip()

		else:
			p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
			containers_images = p.stdout.read().decode("utf-8").strip()

		containers_images = [el.strip('"') for el in containers_images.split()]
		for container in containers_images:
			image = container.split('|')[1]
			if image == cygnus_img_id or CYGNUS_IMAGE_NAME in image:
				cygnus_container_id = container.split('|')[0]
				

		return cygnus_container_id


	def close_handler(self):
		if self.remote:
			self.ssh_session.close()
			logging.info('Closing SSH session to {cygnus_ip}'.format(cygnus_ip=self.cygnus_ip))


	def deploy_cygnus(self):
		"""
		Deploys Cygnus with the provided configuration

		:return: None
		"""
		if self.remote:
			logging.info('Deploying Cygnus remotely with new configuration...')
			self.copy_files()
		else:
			logging.info('Deploying Cygnus with new configuration...')

		self.stop_cygnus()
		self.run_cygnus()
		logging.info('Cygnus deployed successfully')
