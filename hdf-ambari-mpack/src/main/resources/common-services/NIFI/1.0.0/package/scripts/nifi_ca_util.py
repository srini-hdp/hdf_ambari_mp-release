import json, nifi_constants, os
from resource_management.core import sudo
from resource_management.core.resources.system import File

script_dir = os.path.dirname(__file__)
files_dir = os.path.realpath(os.path.join(os.path.dirname(script_dir), 'files'))

def load_config(config_json):
  return json.loads(sudo.read_file(config_json))

def dump_config(config_json, config_dict):
  import params
  File(config_json,
    owner=params.nifi_user,
    group=params.nifi_group,
    mode=0600,
    content=json.dumps(config_dict, sort_keys=True, indent=4)
  ) 

def load_and_overlay_config(config_json, overlay_dict):
  if sudo.path_isfile(config_json):
    config_dict = load_config(config_json)
  else:
    config_dict = {}
  for k, v in overlay_dict.iteritems():
    if v or k not in config_dict:
      config_dict[k] = v
  return config_dict

def load_overlay_dump(config_json, overlay_dict):
  return load_overlay_dump_and_execute(config_json, overlay_dict, lambda: None)

def load_overlay_dump_and_execute(config_json, overlay_dict, execute):
  config_dict = load_and_overlay_config(config_json, overlay_dict)
  dump_config(config_json, config_dict)
  execute()
  return load_config(config_json)

def get_toolkit_script(scriptName, scriptDir = files_dir):
  nifiToolkitDir = None
  for dir in os.listdir(scriptDir):
    if dir.startswith('nifi-toolkit-'):
      nifiToolkitDir = os.path.join(scriptDir, dir)

  if nifiToolkitDir is None:
    raise Exception("Couldn't find nifi toolkit directory in " + scriptDir)
  result = nifiToolkitDir + '/bin/' + scriptName
  if not sudo.path_isfile(result):
    raise Exception("Couldn't find file " + result)
  return result

def update_nifi_properties(client_dict, nifi_properties):
  nifi_properties[nifi_constants.NIFI_SECURITY_KEYSTORE_TYPE] = client_dict['keyStoreType']
  nifi_properties[nifi_constants.NIFI_SECURITY_KEYSTORE_PASSWD] = client_dict['keyStorePassword']
  nifi_properties[nifi_constants.NIFI_SECURITY_KEY_PASSWD] = client_dict['keyPassword']
  nifi_properties[nifi_constants.NIFI_SECURITY_TRUSTSTORE_TYPE] = client_dict['trustStoreType']
  nifi_properties[nifi_constants.NIFI_SECURITY_TRUSTSTORE_PASSWD] = client_dict['trustStorePassword']
