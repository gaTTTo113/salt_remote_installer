
# salt_remote_installer

Module helps to install Saltstack-minion on remote server.
Working with Linux and Windows servers. You can choose Saltstack versions to install.
Use `Installation` class:
Specify: your master or syndic ip address , target server ip address, login and password(use base64 encryption) for the target server, target os (use 'linux' or 'windows'), and specify salt_version.  
#### All available versions of salt can be find here: 
Windows: 
http://repo.saltstack.com/windows/  
please, select .exe files as shown below, otherwise the latest Py3-AMD64 version will be installed  
```
salt_version_windows = `Salt-Minion-2019.2.0-Py3-x86-Setup.exe'  
 ```
 
Linux    
https://github.com/saltstack/salt/branches/all  
use only version number as below, otherwise the newest stable version will be installed
```  
salt_version_linux = '2019.2.1'
```

Example usage:
```
i = Installation(
	'104.5.5.5', 
	'104.5.5.3', 
	'some_username', 
	'some_base64_password', 
	'linux', 
	'2019.2.1'
	)
``` 



