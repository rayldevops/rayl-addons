import subprocess
import os
import socket

"""

We have to add this to nginx vhost files.
Or better to add this to one single file
and include it in various vhosts

location ^~ /.well-known/acme-challenge/ {
    default_type "text/plain";
}



certbot certonly --webroot -w /home/www/letsencrypt -d domain.com --dry-run
todo:
"""

def create_dir(webroot_path="/usr/share/nginx/html/"):
    """
    Directory is automatically created, when using certbot.
    Only use this if creating .well-known/acme-challenge
    manually is specifically required.
    """

    acme_challenge_dir_path = os.path.join(webroot_path, ".well-known/acme-challenge")
    if os.path.exists(acme_challenge_dir_path):
        print(acme_challenge_dir_path, "exists")
    else:
        os.makedirs(acme_challenge_dir_path)

    return acme_challenge_dir_path

def check_ips(custom_domain, subdomain):
    """
    ip_addr1: ip address of custom domain.
    ip_addr2: ip address of subdomain.
    """    
    ip_addr1 = socket.gethostbyname(custom_domain)
    ip_addr2 = socket.gethostbyname(subdomain)
    if ip_addr1 != ip_addr2:
        print("Domain %s not yet mapped. Please make the necessary DNS changes before proceeding!!"%custom_domain)
        raise Exception("Domain %s not yet mapped. Please make the necessary DNS changes before proceeding!!"%custom_domain)
    return True

def generate_certificate(domain_name, client_email, webroot_path, dry_run):
    #path = create_dir()
    cmd = ["sudo", "certbot", "-n", "certonly", "--webroot", "-w", webroot_path]
    cmd.extend(["-d", domain_name])
    if dry_run:
        cmd.extend(["--agree-tos", "-m", client_email, "--dry-run"])
    else:
        cmd.extend(["--agree-tos", "-m", client_email])

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        """
        Function returns:
        status: return code of the process, return code > 1 means ERR and < 1 means OK.
        stdout: stdout of process.
        stderr: stderr of process.
        """
        return {
            "status": not bool(proc.returncode),
            "stdout": out.decode(),
            "stderr": err.decode()
        }
    except subprocess.CalledProcessError as e:
        print(e)

    # if command is successful then certs will be available in /etc/letsencrypt/live/<domain>

if __name__ == "__main__":
    generate_certificate("domain.com", "abc@email.com", "/usr/share/nginx/html/", dry_run=True)
    #check_ips("google.com", "youtube.com")

