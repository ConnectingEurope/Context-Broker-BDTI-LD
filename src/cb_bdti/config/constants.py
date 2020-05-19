from pathlib import Path

BASE_PATH = Path(__file__).parent.parent

LOG_FOLDER_PATH = BASE_PATH / 'logs'
TEST_PATH = BASE_PATH / 'tests'

# CONFIG FILE
import os

# Variables name into config.ini
MAIN_SECTION = "fiware"
ORION_HOST = "orion.host"
CYGNUS_HOST = "cygnus.host"
CYGNUS_KEY_PATH = "cygnus.ssh_key_path"
CYGNUS_USERNAME = "cygnus.ssh_username"

HDFS_SECTION = "hdfs"
HDFS_HOST = "hdfs.host"
HDFS_PORT = "hdfs.port"
HDFS_USERNAME = "hdfs.username"
HDFS_FORMAT_FILE = "hdfs.format_file"
HDFS_OAUTH2_TOKEN = "hdfs.oauth2_token"
HDFS_KRB5_AUTH = "hdfs.krb5_auth"
HDFS_KRB5_USER = "hdfs.krb5_user"
HDFS_KRB5_PASSWORD = "hdfs.krb5_password"

DATA_MODEL_TYPES = "types"
DATA_MODEL_FIWARE_SERVICE = "fiware_service"
DATA_MODEL_FIWARE_SERVICEPATH = "fiware_servicepath"
DATA_MODEL_FILE_PATH = "file_path"
DATA_MODEL_FILE_NAME = "file_name"
DATA_MODEL_THROTTLING = 'throttling'
DATA_MODEL_EXPIRES = 'expires'
DATA_MODEL_SUBSCRIPTION_ID = "subscription_id"
ORION_SUBSCRIPTION_URL = "orion_url"
INTEGRATION_DATE = "integration_date"
MODIFICATION_DATE = "modification_date"

# Variables about agent.conf building
TEMPLATE_AGENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cygnus/agent_hdfs.conf")
MAP_AGENT_CONF = {
	HDFS_HOST: "cygnus-ngsi.sinks.hdfs-sink.hdfs_host",
	HDFS_PORT: "cygnus-ngsi.sinks.hdfs-sink.hdfs_port",
	HDFS_USERNAME: "cygnus-ngsi.sinks.hdfs-sink.hdfs_username",
	HDFS_FORMAT_FILE: "cygnus-ngsi.sinks.hdfs-sink.file_format",
	HDFS_OAUTH2_TOKEN: "cygnus-ngsi.sinks.hdfs-sink.oauth2_token",
	HDFS_KRB5_AUTH: "cygnus-ngsi.sinks.hdfs-sink.krb5_auth",
	HDFS_KRB5_USER: "cygnus-ngsi.sinks.hdfs-sink.krb5_user",
	HDFS_KRB5_PASSWORD: "cygnus-ngsi.sinks.hdfs-sink.krb5_password"
}

# HDFS posible formats files
HDFS_FORMAT_FILE_LIST = ["json-row", "json-column", "csv-row", "csv-column"]

# Cygnus services vars
CYGNUS_IMAGE_NAME = 'fiware/cygnus-ngsi'
CYGNUS_NOTIFICATION_PORT = "5050"
CYGNUS_NOTIFICATION_PATH = "/notify"

# CONFIGURATION files paths
INTERNAL_CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "internal_conf.ini")
PRODUCTION_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.ini")
PRODUCTION_INI_PATH = '/etc'
PRODUCTION_INI_NAME = 'cb_bdti.ini'
PRODUCTION_INI = os.path.join(PRODUCTION_INI_PATH, PRODUCTION_INI_NAME)

CYGNUS_FILES_PATH = '/var/tmp'
AGENT = os.path.join(CYGNUS_FILES_PATH, "agent.conf")
GROUPING_RULES = os.path.join(CYGNUS_FILES_PATH, "grouping_rules.conf")

# Types of 17 Fiware Datamodels
FIWARE_DATAMODELS = {"Alert": ["Alert"],
					 "CivicIssueTracking": ["Open311:ServiceType", "Open311:ServiceRequest"],
					 "Device": ["Device", "DeviceModel"],
					 "Environment": ["AeroAllergenObserved", "AirQualityObserved", "WaterQualityObserved",
									 "NoiseLevelObserved"],
					 "Indicators": ["KeyPerformanceIndicator"],
					 "Parking": ["OffStreetParking", "OnStreetParking", "ParkingGroup", "ParkingAccess", "ParkingSpot"],
					 "ParksAndGardens": ["Garden", "GreenspaceRecord", "FlowerBed"],
					 "PointsOfInterest": ["PointOfInterest", "Beach", "Museum"],
					 "StreetLightning": ["Streetlight", "StreetlightModel", "StreetlightGroup",
										 "StreetlightControlCabinet"],
					 "Transportation": ["BikeHireDockingStation", "Road", "RoadSegment", "TrafficFlowObserved",
										"Vehicle", "VehicleModel", "EVChargingStation"],
					 "Weather": ["WeatherObserved", "WeatherForecast", "WeatherAlert"],
					 "WasteManagement": ["WasteContainerIsle", "WasteContainerModel", "WasteContainer"],
					 "Agrifood": ["AgriApp", "AgriCrop", "AgriFarm", "AgriGreenhouse", "AgriParcel",
									"AgriParcelOperation","AgriParcelRecord", "AgriPest"],
					 "Building": ["Building", "BuildingOperation"],
					 "Energy":["ThreePhaseAcMeasurement"],
					 "PointsOfInteraction":["SmartPointOfInteraction", "SmartSpot"],
					 "UrbanMobility":["GtfsAgency", "GtfsStop", "GtfsStation", "GtfsAccessPoint", "GtfsRoute",
									"GtfsTrip", "GtfsStopTime", "GtfsService", "GtfsCalendarRule", "GtfsCalendarDateRule",
									"GtfsFrequency", "GtfsTransferRule","GtfsShape ", "ArrivalEstimation"],
					}

# Message of errors
SUDO_ERROR = "{date} ERROR    [main] Permission denied: you must run cb-bdti with sudo privileges"
INI_NOT_FOUND = "{date} ERROR    [main] No such config file: {path}"
DEFAULT_INI_NOT_FOUND = "{date} ERROR    [main] No such config file: {path}. Try use get_config command"
