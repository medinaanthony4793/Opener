import sys
import subprocess
import re
import os
import shutil
import json
from slimit import minify # https://github.com/rspivak/slimit (run `pip install slimit`, to fix lextab issue see https://bit.ly/2D30f9s)
from collections import OrderedDict # http://stackoverflow.com/a/10982037

if len(sys.argv) < 2:
    print "No path specified"
    sys.exit()
    
path = sys.argv[1]

data = json.loads(open(path).read(), object_pairs_hook=OrderedDict) # http://stackoverflow.com/a/6921760

# Use the --prefer-script-v1 flag when use need the v2 format (includes only 'script', not 'script2')
preferredScriptName = 'script2'
stripNewField = False
mangle = True
# if len(sys.argv) > 2:
for i in range(2,len(sys.argv)):
    val = sys.argv[i]
    if val == '--prefer-script-v1':
        preferredScriptName = 'script'
        data.pop('redirectRules', None) # Also strip the "redirectRules" entry, which isn't supported by older versions of the app.
        data.pop('previews', None) # Ditto for "previews".
    elif val == '--strip-new':
        stripNewField = True
    elif val == '--no-mangle':
        mangle = False

# Strip unneeded keys from apps
appKeysToKeep = ["identifier", "displayName", "storeIdentifier", "scheme", "platform", "iconURL", "country"]
if not stripNewField:
    appKeysToKeep.append("new");
for appIndex,app in enumerate(data['apps']):
	appKeys = app.keys()
	for keyIndex,key in enumerate(appKeys):
		if not key in appKeysToKeep:
			# print "Removing " + key + " from " + app["identifier"]
			app.pop(key, None)
		elif key == 'scheme':
			app[key] = app[key].replace('://', ':');
			
# Strip unneeded keys from actions
actionIndex = 0
while actionIndex < len(data['actions']):
    action = data['actions'][actionIndex]
    actionIndex = actionIndex + 1
    actionKeys = action.keys()
    for keyIndex,key in enumerate(actionKeys):
        if not key in ["title", "regex", "includeHeaders", "formats"]:
            # print "Removing " + key + " from action"
            action.pop(key, None)

    # Strip unneeded keys from formats
    formatIndex = 0
    while formatIndex < len(action['formats']):
        format = action['formats'][formatIndex]
        formatIndex = formatIndex + 1
        # print '== ' + format['appIdentifier'] + ' ' + action['title'] + ' =='
        
        formatKeys = format.keys()
        for keyIndex,key in enumerate(formatKeys):
            if not key in ["appIdentifier", "app", "format", "script", "script2"]:
                # print "Removing " + key + " from format"
                format.pop(key, None)
            elif (key == "script2" or key == "script") and mangle:
                format[key] = minify(format[key], mangle=True)
                # print format[key]
            elif key == 'app' and format['app']['scheme'] != None:
                format['app']['scheme'] = format['app']['scheme'].replace('://', ':')

        # Ensure only necessary script is included
        if not 'format' in formatKeys:
            if preferredScriptName == 'script2' and 'script2' in formatKeys:
                # print 'Removing v1 script from ' + format['appIdentifier']
                format.pop('script', None)
            elif preferredScriptName == 'script':
                if 'script' in formatKeys:
                    # print 'Removing v2 script from ' + format['appIdentifier']
                    format.pop('script2', None)
                else:
                    # print 'Removing format ' + format['appIdentifier'] + ' from ' + action['title']
                    action['formats'].remove(format)
                    formatIndex = formatIndex - 1

    if len(action['formats']) == 0:
        # print 'Removing action ' + action['title']
        data['actions'].remove(action)
        actionIndex = actionIndex - 1

# Strip unneeded keys from browsers
browserKeysToKeep = ["identifier", "displayName", "storeIdentifier", "scheme", "platform", "iconURL", "country", "regex", "format", "script", "script2"]
if not stripNewField:
    browserKeysToKeep.append("new");
if 'browsers' in data:
	browserIndex = 0
	while browserIndex < len(data['browsers']):
		browser = data['browsers'][browserIndex]
		browserIndex = browserIndex + 1
		browserKeys = browser.keys()
		for keyIndex,key in enumerate(browserKeys):
			if not key in browserKeysToKeep:
                # print "Removing " + key + " from browser"
				browser.pop(key, None)
			elif (key == "script2" or key == "script") and mangle:
				browser[key] = minify(browser[key], mangle=True)
				# print browser[key]
			elif key == 'scheme':
				browser[key] = browser[key].replace('://', ':');
    
        # Ensure only necessary script is included
		if not 'format' in browserKeys:
			if preferredScriptName == 'script2' and 'script2' in browserKeys:
                # print 'Removing v1 script from ' + browser['identifier']
				browser.pop('script', None)
			elif preferredScriptName == 'script':
				if 'script' in browserKeys:
                    # print 'Removing v2 script from ' + browser['identifier']
					browser.pop('script2', None)
				else:
                    # print 'Removing browser ' + browser['identifier']
					data['browsers'].remove(browser)
					browserIndex = browserIndex - 1
                    
# Strip unneeded keys from previews
if 'previews' in data:
    previewKeysToKeep = ["regex", "format", "script", "script2", "canSave"]
    for index,preview in enumerate(data['previews']):
    	keys = preview.keys()
    	for keyIndex,key in enumerate(keys):
    		if not key in previewKeysToKeep:
				# print 'Removing ' + key
				preview.pop(key, None)
    		elif (key == "script2" or key == "script") and mangle:
				preview[key] = minify(preview[key], mangle=True)
				# print preview[key]

if 'redirectRules' in data:
    ruleKeysToKeep = ["param", "format"]
    for ruleIndex,ruleRegex in enumerate(data['redirectRules']):
        rule = data['redirectRules'][ruleRegex]
    	ruleKeys = rule.keys()
    	for keyIndex,key in enumerate(ruleKeys):
    		if not key in ruleKeysToKeep:
    			# print "Removing " + key + " from " + ruleRegex
    			rule.pop(key, None)

				
data = json.dumps(data, separators=(',',':'))
open(path.replace('.json', '-minified.json'), 'w').write(data)

# if v3
#     pop script if both exist
# else if v2
#     pop script2 if both exist
#     pop format if script1 doesn't exist