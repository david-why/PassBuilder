from workflowpy.magic import *
from workflowpy.magic import base64, hashlib
from workflowpy.magic.custom import *
from workflowpy.magic.types import *
from workflowpy.magic import types as T

inputs: dict = dict(shortcut_input())
if inputs is None:
    print(
        'You shouldn\'t call this shortcut directly, or the parameters supplied are invalid (please pass a dictionary with the "pass" and "images" keys).'
    )
    exit()

pass_data: dict = inputs['pass']
if pass_data is None:
    print(
        'The "pass" key is not found. This key should contain the contents of the "pass.json" file.'
    )
    exit()

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

pass_data['serialNumber'] = serial_number
pass_data['teamIdentifier'] = '75242Z93HR'
pass_data['passTypeIdentifier'] = 'pass.me.davidwhy.PassBuilder'
pass_b64 = base64.b64encode(set_name(pass_data, 'pass.json'))

images = variable(inputs['images'])
if images is None:
    images = {}

files = variable({'pass.json': pass_b64})
for image in images:
    files[image] = images[image]

manifest = variable({})
for file in files:
    manifest[file] = hashlib.sha1(files[file]).hexdigest()
manifest_json = set_name(manifest, 'manifest.json')
manifest_b64 = base64.b64encode(manifest_json)
files['manifest.json'] = manifest_b64

signature_data: dict = dict(
    fetch('https://passbuilder.davidwhy.me/sign', method='POST', data=manifest)  # type: ignore
)
is_success: bool = signature_data['success']
if is_success:
    pass
else:
    print(f'Failed to sign the pass: {signature_data["error"]}')
    exit()
files['signature'] = base64.b64decode(signature_data['signatureBase64'])

to_zip = variable([])
for file in files:
    contents = base64.b64decode(files[file])
    to_zip.append(set_name(contents, file))

zipped = action(
    'is.workflow.actions.makezip',
    {'WFInput': attachment(to_zip)},
    ('Archive', T.file),
)

print(zipped)
