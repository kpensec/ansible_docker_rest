#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: docker_rest_image 

short_description: docker_image over rest api

version_added: "2.4"

description:
    - ""

options:
    image:
        description:
            - Desired image
        required: true
    tag:
        description:
            - Desired tag
        required: false
    registry:
        description:
            - Registry from where to pull
        required: false

    host:
        description:
            - dockerd http host
        required: false

    host_port:
        description:
            - dockerd http port
        required: false

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pulling alping:latest image
- name: pull alpine latest
  docker_rest_image:
    image: alpine
    tag: latest
'''

RETURN = '''
status:
    description: Last status line returned by API
    type: str
    returned: on success
message:
    description: Error message
    type: str
    returned: on error
'''

from ansible.module_utils.basic import AnsibleModule

def get_last_json(text):
    import json
    return json.loads(next(filter(None, reversed(text.split(b'\r\n')))))

def pull_image(host, host_port, image, tag, registry):
    import requests
    image_fullname= f"{registry}/{image}:{tag}"
    response = requests.post(f"http://{host}:{host_port}/v1.24/images/create?fromImage={image_fullname}")
    data=get_last_json(response.content)
    status=data.get("status", data.get("message", ""))
    return {
      "changed": status != f"Status: Image is up to date for {image_fullname}",
      "error": not response.ok,
      "message": status
    }

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        registry=dict(type='str', required=False, default="registry.hub.docker.com/library"),
        host=dict(type='str', required=False, default="127.0.0.1"),
        host_port=dict(type='int', required=False, default=2375),
        image=dict(type='str', required=True),
        tag=dict(type='str', required=True)
    )
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result = {**result, **pull_image(**module.params)}


    if result['error']:
        module.fail_json(msg="error pulling image", **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
