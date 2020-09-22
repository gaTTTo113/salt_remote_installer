import subprocess
import threading
import winrm
import warnings

warnings.filterwarnings("ignore")


class Installation:
    def __init__(self, master_ip, server_ip,
                 login, password, os_name,
                 salt_version):
        self.error_message = ''

        self.master_ip = master_ip
        self.server_ip = server_ip
        self.login = login
        self.salt_version = salt_version
        self.lock = threading.Lock()

        self.stage = 'Password checking'
        try:
            self.password = password.decode('base64')
        except Exception as exception:
            # print('Wrong password ' + server_ip)
            self.error_message = 'Wrong password, ' + str(exception.args)
            # todo exception handling here here
        # todo if salt_version not on_list Exception here too

        if os_name == 'linux':
            self.linux()
        elif os_name == 'windows':
            self.windows()
        else:
            # todo Exception handling here
            pass

    def windows(self):
        self.stage = 'Initialise'
        winrm_session = winrm.Session(self.server_ip, auth=(self.login, self.password), transport='ntlm')
        try:
            r = winrm_session.run_ps(
                'curl https://repo.saltstack.com/windows/'
                + self.salt_version
                + ' -Method Get -OutFile C:\\salt_setup.exe')
            if r.status_code != 0:
                self.error_message = self.server_ip \
                                     + ' : Can\'t download setup-file.\n' \
                                     + str(r.std_out + r.std_err)
                return 1
        except Exception as exc:
            self.error_message = self.server_ip \
                                 + 'Can\'t connect to ' \
                                 + self.server_ip + '\n' + str(exc.args)
            return 2
        r = winrm_session.run_cmd('C:\\salt_setup.exe /S /master=' + self.master_ip + ' /minion-name=' + self.server_ip)
        if r.status_code != 0:
            self.error_message = self.server_ip \
                                 + ' : Installation crushed ' \
                                 + str(r.std_out + r.std_err)
            return 3

        self.stage = 'Checking installation'
        r = winrm_session.run_cmd('type C:\\salt\\conf\\minion')

        if self.master_ip in r.std_out:
            if self.master_ip in r.std_out:
                self.stage = 'Installation completed'
                return 0
            else:
                self.error_message = self.server_ip \
                                     + 'Can\'t validate data on server.' \
                                       ' Manual check needed.'
                return 4

    def linux(self):
        self.stage = 'Initialise'

        def execute_command(command):
            process = subprocess.Popen(
                ['sshpass', '-p', self.password] + command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, stderr = process.communicate()
            message = str(stderr) + str(stdout)
            if process.returncode != 0:
                return message
            return ''

        self.error_message += execute_command(
            ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
             'install_salt.sh',
             self.login + '@' + str(self.server_ip) + ':~'])

        if self.error_message != '':
            return 2

        self.error_message += execute_command(
            ['ssh', '-o', 'StrictHostKeyChecking=no', '-t', self.login + '@'
             + self.server_ip, 'echo \''
             + self.password
             + '\' | sudo -S sh install_salt.sh -F -A '
             + self.master_ip + ' git '
             + self.salt_version])

        if self.error_message != '':
            # print("Installation crushed " + server_ip + '\n\r')
            return 3
        # print("Installation completed " + server_ip + '\n\r')
        return 0
