from winrm.protocol import Protocol
from requests.exceptions import ConnectionError
import os

Path_to_agent = r'\\IP\agent'
Path_to_ip = '/poogas/ip'

def agent_install(ip):
    p = Protocol (
    endpoint=f'http://{ip}:5985/wsman',
    transport='ntlm',
    username='',
    password='',
    server_cert_validation='ignore')

    try:
        shell_id = p.open_shell()
        command_id = p.run_command(shell_id, 'powershell.exe Copy-Item', [rf'-Path {Path_to_agent} -Destination Microsoft.Powershell.Core\FileSystem::C:\Progra~1\ -Recurse'])
        command_if = p.run_command(shell_id, 'powershell.exe', [r'C:\Progra~1\agent\install-service-agent.ps1'])
        status_code = p.get_command_output(shell_id, command_id)
        if status_code != 0:
            command_id = p.run_command(shell_id, 'powershell.exe', [r'-ExecutionPolicy UnRestricted -File C:\Progra~1\agent\install-service-agent.ps1'])
            std_err = p.get_command_output(shell_id, command_id)
        command_id = p.run_command(shell_id, 'powershell.exe Start-Service', ['agent']
        std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
        p.cleanup_command(shell_id, command_id)
        p.close_shell(shell_id)

        if status_code == 0:
            print('successful', ip)
        else:
            if 'Cannot start' in str(std_err):
                print('cannot start service', ip)
            else:
                print('unsuccessufullu', ip)
                try:
                    agent_install(ip)
                except ConnectionError:
                    return print('unsuccessufullu connect to', ip)
    except ConnectionError:
        return print('unsuccessufully connection to', ip)

with open(Path_to_ip, 'r') as file:
    list = file.read().splitlines()
    for i in list:
        status = os.system('ping -w3 -c2 ' + i + ' > /dev/null 2>&1')
        if status == 0:
            winlogbeat_install(i)
        else:
            print('unssuccessfullu ping to', i)

