"""
cloud_setup
+ start_ssh

Modified: 2024/01/18
Created : 2024/01/18
(c) Nhu-Tai Do
"""

def start_ssh(id_rsa_pub = "", password = "", install_ssh = False, config_ssh = False):
    """
    Start SSH as follows:
    + Add id_rsa.pub into ~/.ssh/authorized_keys
    + Install SSH service with Port 22 and password
    + Set command prompt

    Modified: 2024/01/18
    Created : 2024/01/18
    """    
    from IPython import get_ipython
    import os
    print(f'{"*" * 10} SETUP SSH SERVICE {"*"*10}')

    if install_ssh is True:
        get_ipython().system('echo "> Install ssh service..."')
        get_ipython().system('apt-get install ssh -y 2>&1 > /dev/null')
    
    if id_rsa_pub != "":
        get_ipython().system('echo "> Copy public key to authorized keys..."')
        get_ipython().system('mkdir -p ~/.ssh')
        get_ipython().system(f'echo {id_rsa_pub} > ~/.ssh/authorized_keys')

    if config_ssh is True:
        get_ipython().system('echo "> Config ssh service..."')
        get_ipython().system("sed -i 's/^#Port.*/Port 22/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#Port.*/Port 22/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#ListenAddress 0.*/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#ListenAddress ::.*/ListenAddress ::/' /etc/ssh/sshd_config")

        get_ipython().system("sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config")

        get_ipython().system("sed -i 's/^#AllowAgentForwarding.*/AllowAgentForwarding yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#AllowTcpForwarding.*/AllowTcpForwarding yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#PermitTTY.*/PermitTTY yes/' /etc/ssh/sshd_config")
        get_ipython().system("sed -i 's/^#GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config")
        # !systemctl reload sshd

    if password != "":
        get_ipython().system('echo "> Set root password..."')
        get_ipython().system(f'echo -e "$password\n{password}" | passwd root >/dev/null 2>&1')

    get_ipython().system('echo "> Restart SSH service..."')
    get_ipython().system('service ssh restart')
    print(f"")

    get_ipython().system('echo "> Process ~/.bashrc to registry PS1, TERM..."')
    get_ipython().system('grep -qx "^PS1=.*$" ~/.bashrc || echo "PS1=" >> ~/.bashrc')
    dest = "PS1='\\[\\e]0;\\u@\h: \\w\\a\\]${debian_chroot:+($debian_chroot)}\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\$ '"
    cmd = "sed -i \"s/$(echo $src | sed -e 's/\\([[\\/.*]\\|\\]\\)/\\\\&/g').*/$(echo $dest | sed -e 's/[\\/&]/\\\\&/g')/g\" ~/.bashrc"
    get_ipython().system(f'src="PS1=" && echo $src && dest="{dest}" && echo "$dest" && {cmd}')

    cmd = 'grep -qx "^TERM=.*$" ~/.bashrc || echo "TERM=xterm-256color" >> ~/.bashrc'
    get_ipython().system(f'{cmd}')
    print(f"")
    
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass # start_ssh

def start_ngrok(ngrok_tokens = [], 
                ngrok_binds  = {
                    'ssh': {'port':22, 'type':'tcp'}, 
                    'vscode': {'port':9000, 'type':'http'}
                }
               ):
    """
    start_ngrok:
    + ngrok_tokens: list of token getting from Authtoken in dashboard at https://ngrok.com
    + ngrok_binds : default: 
        {
            'ssh'   : {'port':22, 'type':'tcp'}, 
            'vscode': {'port':9000, 'type':'http'}
        }
    """
    def default_handler(ngrok, ngrok_info = {}):
        # bind with code-server: port 9000
        # vscode_tunnel = ngrok.connect(9000, "http")
        
        # bind with ports
        for name in ngrok_binds:
            try:
                tunnel = ngrok.connect(ngrok_binds[name].get('port', 80), 
                                   ngrok_binds[name].get('type', 'tcp'))
                ngrok_info[name] = tunnel
            except:
                print('failt')
            pass
        pass # default_handler
    
    print(f'{"*" * 10} SETUP NGROK {"*"*10}')
    try:
        from pyngrok import ngrok, conf
    except:
        # install pyngrok
        print(f'> Install ngrok...')
        get_ipython().system('pip install -qqq pyngrok 2>&1 > /dev/null')
        from pyngrok import ngrok, conf

    print(f'> Kill ngrok process...')
    get_ipython().system('kill -9 "$(pgrep ngrok)"')
    
    print(f'> Binding ports...')
    list_regions = ["us", "en", "au", "vn"]
    url, ssh_tunnel = None, None
    is_success = False
    ngrok_info = {}
    for auth_token in ngrok_tokens:
        if is_success: break
        for region in list_regions:  
            try:
                conf.get_default().region = region
                ngrok.set_auth_token(auth_token)

                default_handler(ngrok, ngrok_info)

                print("> Registry success!")
                is_success = True
                break
            except Exception as e:
                print(e)
                pass    
        # for

    for key in ngrok_info:
        print(f'{key}: {ngrok_info[key]}')
    
    print(f"")
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass # start_ngrok

def start_vscode(ws_dir = ".", 
                 password = "12345", 
                 vscode_dir = '~/.vscode', 
                 install = False, 
                 extensions = ["ms-python.python", 
                               "ms-toolsai.jupyter", 
                               "mechatroner.rainbow-csv", 
                               "vscode-icons-team.vscode-icons"]):
    print(f'{"*" * 10} SETUP VSCODE {"*"*10}')
    
    import os
    # vscode-server config
    extensions_dir=f"{vscode_dir}/extensions"
    user_data_dir=f"{vscode_dir}/user_data"

    get_ipython().system(f'mkdir -p {extensions_dir}')
    get_ipython().system(f'mkdir -p {user_data_dir}')

    # install code-server and start with port 9000
    if install is True:
        print('> Install Code-Server...')
        get_ipython().system('curl -fsSL https://code-server.dev/install.sh | sh 2>&1 > /dev/null')

    print('> Run code-server...')
    get_ipython().system(f'sudo screen -dmS vscode bash -c "PASSWORD=\"{password}\" code-server --port 9000 --bind-addr 0.0.0.0 --user-data-dir={user_data_dir} --extensions-dir={extensions_dir} --disable-telemetry {ws_dir}"')
    print(f"")

    print('> Download and Install code-server...')
    for extension in extensions:
        print(f'Install extension: {extension}...')
        get_ipython().system('code-server --install-extension $extension 2>&1 > /dev/null')
    print(f"")

    print('> Screen Background...')
    get_ipython().system('screen -wipe')
    get_ipython().system('screen -ls')
    
    print(f"")
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass # start_vscode

def setup_config_github(id_rsa_val, id_rsa_name, hostname="github.com", append = False, show_id_rsa = False):
    print(f'{"*" * 10} CONFIG GITHUB {"*"*10}')
    
    print('> Add id_rsa...')
    get_ipython().system('mkdir -p ~/.ssh')
    get_ipython().system(f'echo "{id_rsa_val}" > ~/.ssh/{id_rsa_name}')
    get_ipython().system(f'chmod 600 ~/.ssh/{id_rsa_name}')

    ssh_config  = f"Host {hostname}\n"
    ssh_config +=  "    HostName ssh.github.com\n"
    ssh_config +=  "    User git\n"
    ssh_config +=  "    Port 443\n"
    ssh_config +=  "    StrictHostKeyChecking no\n"
    ssh_config += f"    IdentityFile ~/.ssh/{id_rsa_name}"

    if append is False:
        print('> Add config file...')
        get_ipython().system('echo "$ssh_config" > ~/.ssh/config')
    else:
        print('> Append config file...')
        get_ipython().system('echo "$ssh_config" >> ~/.ssh/config')

    print('> List ~/.ssh...')
    get_ipython().system('ls ~/.ssh')
    
    if show_id_rsa:
        print('> Show id_rsa...')
        get_ipython().system(f'cat ~/.ssh/{id_rsa_name}')
    
    print('> Show config...')
    get_ipython().system(f'cat ~/.ssh/config')
    
    print('> Test ssh...')
    get_ipython().system(f'ssh {hostname}')
    pass # setup_config_github

def base64_encode(s):
    import os
    result = os.popen(f'echo "{s}" | base64 -w 0').read().strip()
    return result
    pass # base64_encode

def base64_decode(s):
    import base64
    return base64.b64decode(s).decode('ascii')
    pass # base64_decode