from workflowpy.magic import *
from workflowpy.magic import base64
from workflowpy.magic.custom import *
from workflowpy.magic.types import *

serial_number = action(
    'com.sindresorhus.Actions.GenerateUUIDIntent',
    {
        'AppIntentDescriptor': {
            'AppIntentIdentifier': 'GenerateUUIDIntent',
            'BundleIdentifier': 'com.sindresorhus.Actions',
            'Name': 'Actions',
            'TeamIdentifier': 'YG56YK5RN5',
        }
    },
    ('UUID', text),
)

pass_data = raw_dict(
    {
        'formatVersion': 1,
        'passTypeIdentifier': 'pass.me.davidwhy.PassBuilder',
        'serialNumber': f'{serial_number}',
        'teamIdentifier': '75242Z93HR',
        'organizationName': 'Toy Town',
        'description': 'Toy Town Membership',
        'logoText': 'Toy Town',
        'foregroundColor': 'rgb(255, 255, 255)',
        'backgroundColor': 'rgb(197, 31, 31)',
        'generic': {
            'primaryFields': [
                {
                    'key': 'member',
                    'value': 'Johnny Appleseed',
                }
            ],
            'secondaryFields': [
                {
                    'key': 'subtitlte',
                    'label': 'MEMBER SINCE',
                    'value': '2012',
                }
            ],
        },
    }
)
pass_json = set_name(pass_data, 'pass.json')
pass_b64 = base64.b64encode(pass_json)

icon_b64 = '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'

files = {}
files['pass.json'] = pass_b64
files['icon.png'] = icon_b64

manifest = variable({})
for file in files:
    manifest[file] = files[file]

print(manifest)
