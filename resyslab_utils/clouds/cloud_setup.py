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
    print(f'{"*" * 10} SETUP SSH SERVICE {"*"*10}')

    if install_ssh is True:
        !echo "> Install ssh service..."
        !apt-get install ssh -y 2>&1 > /dev/null
    
    if id_rsa_pub != "":
        !echo "> Copy public key to authorized keys..."
        !mkdir -p ~/.ssh
        !echo $id_rsa_pub > ~/.ssh/authorized_keys

    if config_ssh is True:
        !echo "> Config ssh service..."
        !sed -i 's/^#Port.*/Port 22/' /etc/ssh/sshd_config
        !sed -i 's/^PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
        !sed -i 's/^#Port.*/Port 22/' /etc/ssh/sshd_config
        !sed -i 's/^#ListenAddress 0.*/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config
        !sed -i 's/^#ListenAddress ::.*/ListenAddress ::/' /etc/ssh/sshd_config

        !sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
        !sed -i 's/^#PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
        !sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

        !sed -i 's/^#AllowAgentForwarding.*/AllowAgentForwarding yes/' /etc/ssh/sshd_config
        !sed -i 's/^#AllowTcpForwarding.*/AllowTcpForwarding yes/' /etc/ssh/sshd_config
        !sed -i 's/^#PermitTTY.*/PermitTTY yes/' /etc/ssh/sshd_config
        !sed -i 's/^#GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config
        !systemctl reload sshd

    if password != "":
        !echo "> Set root password..."
        !echo -e "$password\n$password" | passwd root >/dev/null 2>&1

    !echo "> Restart SSH service..."
    !service ssh restart 
    print(f"")

    !echo "> Process ~/.bashrc for PS1, TERM..."
    !src="PS1=" && echo "$src" \
        && dest="PS1='\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '" && echo "$dest" \
        && sed -i "s/$(echo $src | sed -e 's/\([[\/.*]\|\]\)/\\&/g').*/$(echo $dest | sed -e 's/[\/&]/\\&/g')/g" ~/.bashrc
    !grep -qx "^TERM=.*$" ~/.bashrc || echo "TERM=xterm-256color" >> ~/.bashrc
    print(f"")
    
    print(f'{"-" * 10} Finished {"-"*10}\n')
    pass # start_ssh

