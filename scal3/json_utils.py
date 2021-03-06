#!/usr/bin/env python3
import sys
try:
	import ujson as json
except ImportError:
	try:
		import json
	except ImportError:
		import simplejson as json

from collections import OrderedDict


def dataToPrettyJson(data, ensure_ascii=False, sort_keys=False):
	return json.dumps(
		data,
		sort_keys=sort_keys,
		indent=2,
		ensure_ascii=ensure_ascii,
	)


def dataToCompactJson(data, ensure_ascii=False, sort_keys=False):
	kwargs = dict(
		sort_keys=sort_keys,
		ensure_ascii=ensure_ascii,
	)
	# ujson.dumps does not accept separators= arguments
	# but for standard json module, this argument is needed to get the most compact json
	if json.__name__ == "json":
		kwargs["separators"] = (",", ":")
	return json.dumps(data, **kwargs)


jsonToData = json.loads


def jsonToOrderedData(text):
	return json.JSONDecoder(
		object_pairs_hook=OrderedDict,
	).decode(text)


###############################


def loadJsonConf(module, confPath, decoders={}):
	from os.path import isfile
	###
	if not isfile(confPath):
		return
	###
	try:
		text = open(confPath).read()
	except Exception as e:
		print("failed to read file \"%s\": %s" % (confPath, e))
		return
	###
	try:
		data = json.loads(text)
	except Exception as e:
		print("invalid json file \"%s\": %s" % (confPath, e))
		return
	###
	if isinstance(module, str):
		module = sys.modules[module]
	for param, value in data.items():
		if param in decoders:
			value = decoders[param](value)
		setattr(module, param, value)


def saveJsonConf(module, confPath, params, encoders={}):
	if isinstance(module, str):
		module = sys.modules[module]
	###
	data = {}
	for param in params:
		value = getattr(module, param)
		if param in encoders:
			value = encoders[param](value)
		data[param] = value
	###
	text = dataToPrettyJson(data, sort_keys=True)
	try:
		open(confPath, "w").write(text)
	except Exception as e:
		print("failed to save file \"%s\": %s" % (confPath, e))
		return


def loadModuleJsonConf(module):
	if isinstance(module, str):
		module = sys.modules[module]
	###
	decoders = getattr(module, "confDecoders", {})
	###
	try:
		sysConfPath = module.sysConfPath
	except AttributeError:
		pass
	else:
		loadJsonConf(
			module,
			sysConfPath,
			decoders,
		)
	####
	loadJsonConf(
		module,
		module.confPath,
		decoders,
	)
	## should use module.confParams to restrict json keys? FIXME


def saveModuleJsonConf(module):
	if isinstance(module, str):
		module = sys.modules[module]
	###
	saveJsonConf(
		module,
		module.confPath,
		module.confParams,
		getattr(module, "confEncoders", {}),
	)
