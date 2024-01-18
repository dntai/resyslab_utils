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
        get_ipython().system('echo -e "$password\n$password" | passwd root >/dev/null 2>&1')

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

def start_ngrok(ngrok_tokens = [], ngrok_handler = None, only_kill = False):
    """
    start_ngrok:
    + ngrok_tokens: list of token getting from Authtoken in dashboard at https://ngrok.com
    + ngrok_handler: registry handler where default:
        def default_handler(ngrok, ngrok_info = {}):
        # bind with code-server: port 9000
        # vscode_tunnel = ngrok.connect(9000, "http")

        # bind with ssh: port 22
        try:
            ssh_tunnel = ngrok.connect(22, "tcp")
            ngrok_info["ssh"] = ssh_tunnel
        except:
            pass
        pass # default_handler
    """
    def default_handler(ngrok, ngrok_info = {}):
        # bind with code-server: port 9000
        # vscode_tunnel = ngrok.connect(9000, "http")
        
        # bind with ssh: port 22
        try:
            ssh_tunnel = ngrok.connect(22, "tcp")
            ngrok_info["ssh"] = ssh_tunnel
        except:
            pass
        pass # default_handler
    
    print(f'{"*" * 10} START NGROK {"*"*10}')
    try:
        from pyngrok import ngrok, conf
    except:
        # install pyngrok
        print(f'> Install ngrok...')
        get_ipython().system('pip install -qqq pyngrok 2>&1 > /dev/null')
        from pyngrok import ngrok, conf

    print(f'> Kill ngrok process...')
    get_ipython().system('kill -9 "$(pgrep ngrok)"')
    
    if only_kill is False:    
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

                    if ngrok_handler is None:
                        default_handler(ngrok, ngrok_info)
                    else:
                        ngrok_handler(ngrok, ngrok_info)

                    print("> Registry success!")
                    is_success = True
                    break
                except Exception as e:
                    print(e)
                    pass    
            # for

        for key in ngrok_info:
            print(f'{key}: {ngrok_info[key]}')
        pass # binding
    
    print(f"")
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass # start_ngrok

