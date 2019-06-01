#!/usr/bin/python

from os import environ
import re
import subprocess

from ansible.module_utils.basic import *

def _check_output_strip(command):
    return subprocess.check_output(command).decode('utf-8').strip()

def _escape_single_quotes(string):
    return re.sub("'", r"'\''", string)

def _get_dbus_bus_address(user):
    if user is None:
        if environ.get('DBUS_SESSION_BUS_ADDRESS') is None:
            return None

        return "DBUS_SESSION_BUS_ADDRESS={}".format(environ['DBUS_SESSION_BUS_ADDRESS'])

    try:
        pid = _check_output_strip(['pgrep', '-u', user, 'gnome-session'])
    except subprocess.CalledProcessError:
       return None

    if pid:
        return _check_output_strip(
            ['grep', '-z', '^DBUS_SESSION_BUS_ADDRESS',
             '/proc/{}/environ'.format(pid)]).strip('\0')

def _run_cmd_with_dbus(user, cmd):
    dbus_addr = _get_dbus_bus_address(user)
    if not dbus_addr:
        command = ['export `/usr/bin/dbus-launch`', ';']
    else:
        command = ['export', dbus_addr, ';']
    command.extend(cmd)
    if not dbus_addr:
        command.extend([';',
            'kill $DBUS_SESSION_BUS_PID &> /dev/null'
        ])

    if user is None:
        return _check_output_strip(['/bin/sh', '-c', " ".join(command)])

    return _check_output_strip(['su', '-', user , '-c', " ".join(command)])

def _set_value(user, key, value):
    return _run_cmd_with_dbus(
        user,
        ['/usr/bin/dconf', 'write',
         key, "'%s'" % _escape_single_quotes(value)])

def _get_value(user, key):
    return _run_cmd_with_dbus(
        user,
        ['/usr/bin/dconf', 'read', key])

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present'], 'default': 'present' },
            'user': { 'default': None },
            'key': { 'required': True },
            'value': { 'required': True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(user, key)
    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(user, key, value)

    module.exit_json(**{
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
