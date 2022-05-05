from create_certificate import generate_certificate, check_ips
import os
import subprocess
from configparser import SafeConfigParser
import shutil

"""
TODO: EDGE-CASE: 1. TO GREP PROXY PASS OUT OF MULTIPLE LOCATION BLOCK.
normal vhost copy part 
"""

CLIENT_EMAIL = "saasclient@odoo-saas.webkul.com"
WEBROOT_PATH = "/usr/share/nginx/html/" 
REVERSE_PROXY_CHECK = "sudo nginx -t"
REVERSE_PROXY_RELOAD = "sudo nginx -s reload"

def execute_on_shell(cmd):
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(e)
        return False

def grep_backends_from_conf(odoo_saas_data, subdomain):
    conf_path = os.path.join(odoo_saas_data, subdomain+".conf")
    # print(conf_path)
    cmd = "grep LONGPOLLINGBACKEND" + conf_path
    grep_data = subprocess.Popen("grep LONGPOLLINGBACKEND " + conf_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = grep_data.communicate()

    if err:
        print("Couldn't get LONGPOLLINGBACKEND PORT")
    # print(out.decode().strip().split(';')[0].split(' ')[-1])
    longpolling_backend = out.decode().strip().split(';')[0].split(' ')[-1].split('//')[-1]
    grep_data = subprocess.Popen("grep ODOOBACKEND " + conf_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = grep_data.communicate()
    if err:
        print("Couldn't get ODOOBACKEND PORT")
    odoo_backend = out.decode().strip().split(';')[0].split(' ')[-1].split('//')[-1]
    # print(longpolling_backend, odoo_backend)

    return odoo_backend, longpolling_backend

def replace_placeholders(vhost_file, odoo_backend, longpolling_backend, custom_domain):
    cmd = "sed -i \"s/LONG_BACKEND_TO_BE_REPLACED/%s/g\" %s"%(longpolling_backend,vhost_file)
    if not execute_on_shell(cmd):
        print("Couldn't Replace Port!!")
        return False
    cmd = "sed -i \"s/BACKEND_TO_BE_REPLACED/%s/g\" %s"%(odoo_backend,vhost_file)
    if not execute_on_shell(cmd):
        print("Couldn't Replace Port!!")
        return False
    cmd = "sed -i \"s/DOMAIN_TO_BE_REPLACED/%s/g\"  %s"%(custom_domain,vhost_file)
    if not execute_on_shell(cmd):
        print("Couldn't Replace Subdomain!!")
        return False
    if not execute_on_shell(REVERSE_PROXY_CHECK):
        print("Couldn't Replace Subdomain!!")
        return False
    if not execute_on_shell(REVERSE_PROXY_RELOAD):
        print("Couldn't Replace Subdomain!!")
        return False
    return True

def create_vhost_redirect(custom_domain, docker_vhosts):
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    if os.path.exists(new_conf):
        custom_domain_vhost = open(new_conf, 'a+')
        vhosttemplateredirect = open(os.path.join(docker_vhosts, "vhosttemplateredirect.txt"))
        custom_domain_vhost.write("\n\n" + vhosttemplateredirect.read())
        
        custom_domain_vhost.close()
        vhosttemplateredirect.close()
        
        cmd = "sed -i \"s/DOMAIN_TO_BE_REPLACED/%s/g\"  %s"%(custom_domain, new_conf)
        if not execute_on_shell(cmd):
            print("Couldn't Replace Subdomain!!")
            return False
        if not execute_on_shell(REVERSE_PROXY_CHECK):
            print("Couldn't Replace Subdomain!!")
            return False
        if not execute_on_shell(REVERSE_PROXY_RELOAD):
            print("Couldn't Replace Subdomain!!")
            return False
    else:
        print("File not created")

def create_vhost_https(subdomain, custom_domain, odoo_backend, longpolling_backend, docker_vhosts="/opt/odoo/Odoo-SAAS-Data/docker_vhosts"):
    #sed -i 's/.*ssl_certificate\ .*/ ssl_certificate \/this\/is\/test/' ssl.conf
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    if os.path.exists(new_conf):
        os.remove(new_conf)
    shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplatehttps.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
    # new_conf = custom_domain+".conf" #only for testing the code
    certificate_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/fullchain.pem")
    privkey_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/privkey.pem")
    cmd = "sed -i 's/.*ssl_certificate .*/ ssl_certificate %s;/' %s"%(certificate_path.replace("/", "\/"), new_conf)
    if not execute_on_shell(cmd):
        print("Couldn't add ssl certificate path")
        return False
    cmd = "sed -i 's/.*ssl_certificate_key .*/ ssl_certificate_key %s;/' %s"%(privkey_path.replace("/", "\/"), new_conf)
    if not execute_on_shell(cmd):
        print("Couldn't add ssl key in vhostfile")
        return False
    return replace_placeholders(new_conf, odoo_backend, longpolling_backend, custom_domain)

def create_vhost_http(subdomain, custom_domain, odoo_backend, longpolling_backend, docker_vhosts="/opt/odoo/Odoo-SAAS-Data/docker_vhosts", ssl_flag=False):
    #sed -i 's/.*ssl_certificate\ .*/ ssl_certificate \/this\/is\/test/' ssl.conf
    new_conf = os.path.join(docker_vhosts, custom_domain+".conf")
    
    if ssl_flag:
        shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplatehttps.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
        # new_conf = custom_domain+".conf" #only for testing the code
        certificate_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/fullchain.pem")
        privkey_path = os.path.join("/etc/letsencrypt/live/", custom_domain + "/privkey.pem")
        cmd = "sed -i 's/.*ssl_certificate .*/ ssl_certificate %s;/' %s"%(certificate_path.replace("/", "\/"), new_conf)
        if not execute_on_shell(cmd):
            print("Couldn't add ssl certificate path")
            return False
        cmd = "sed -i 's/.*ssl_certificate_key .*/ ssl_certificate_key %s;/' %s"%(privkey_path.replace("/", "\/"), new_conf)
        if not execute_on_shell(cmd):
            print("Couldn't add ssl key in vhostfile")
            return False
        return replace_placeholders(new_conf, odoo_backend, longpolling_backend, custom_domain)        
    else:
        shutil.copyfile(os.path.join(docker_vhosts, "vhosttemplate.txt"), os.path.join(docker_vhosts, custom_domain+".conf"))
        return replace_placeholders(new_conf, odoo_backend, longpolling_backend, custom_domain)

def remove_vhost(domain, docker_vhosts):
    if os.path.exists(os.path.join(docker_vhosts, domain + ".conf")):
        os.remove(os.path.join(docker_vhosts, domain + ".conf"))
        print("%s removed successfully"%domain)
    else:
        print("Vhost does not exists")

def read_path_saas_conf(module_path):
    print("Reading saas.conf")
    saas_conf_path = os.path.join(module_path, "models/lib/saas.conf")
    print(saas_conf_path)
    parser = SafeConfigParser()
    parser.read(saas_conf_path)
    odoo_saas_data = parser.get("options", "odoo_saas_data")

    return odoo_saas_data

def run_certbot(custom_domain, client_email, webroot_path, dry_run):
    out = generate_certificate(custom_domain, client_email, webroot_path, dry_run)
    print(out)
    if not out['status']:
        print("Certificate generation failed", out['stderr'])
        exit(1)
    else:
        print(out['stdout'], out['stderr'])

def main_remove(custom_domain, module_path):
    odoo_saas_data = read_path_saas_conf(module_path)
    docker_vhosts = os.path.join(odoo_saas_data, "docker_vhosts")
    remove_vhost(custom_domain, docker_vhosts)

def main_add(subdomain, custom_domain, ssl_flag, module_path):
    odoo_saas_data = read_path_saas_conf(module_path)
    if  check_ips(custom_domain, subdomain):
        odoo_backend, longpolling_backend = grep_backends_from_conf(os.path.join(odoo_saas_data, "docker_vhosts"), subdomain)
        create_vhost_http(subdomain, custom_domain, odoo_backend, longpolling_backend, docker_vhosts=os.path.join(odoo_saas_data, "docker_vhosts"))
        print("HTTP Createf for %s"%custom_domain)
        #create_vhost(subdomain, custom_domain, odoo_backend, longpolling_backend, docker_vhosts=os.path.join(odoo_saas_data, "docker_vhosts"))
        if ssl_flag:
            print("SSL to be done for %s"%custom_domain)
            run_certbot(custom_domain, client_email=CLIENT_EMAIL, webroot_path=WEBROOT_PATH, dry_run=False)
            print("SSL generated")
            create_vhost_https(subdomain, custom_domain, odoo_backend, longpolling_backend, docker_vhosts=os.path.join(odoo_saas_data, "docker_vhosts"))
            print("Create HHTPS vhost")
            #create_vhost_redirect(custom_domain, docker_vhosts=os.path.join(odoo_saas_data, "docker_vhosts"))

if __name__ == '__main__':

    """
    USAGE: 
    Just call main() function with params:
    subdomain: existing domain
    custom_domain: new domain
    ssl_flag: to notify if ssl certs are already present
    """

    subdomain = "trial_test_4.odoo12-saas.webkul.com"
    custom_domain = "gc-new.odoo12-saas.webkul.com"

    main_add(subdomain=subdomain, custom_domain=custom_domain, ssl_flag=True, module_path="/opt/odoo14/webkul_addons/odoo_saas_kit/")
    
    # EVERTHING UNDERNEATH THIS IS FOR TESTING
    #odoo_saas_data = os.getcwd()
    #odoo_backend, longpolling_backend = grep_backends_from_conf(odoo_saas_data, "test.odoo-saas.webkul.com")
    # run_certbot(domain_name="domain.com", client_email="abc@domain.com", webroot_path="/usr/share/nginx/html/", dry_run=True)
    #create_vhost("test.odoo-saas.webkul.com", "domain.ml", odoo_backend, longpolling_backend, docker_vhosts=odoo_saas_data, ssl_flag=True)
    #remove_vhost("test.abc.com", docker_vhosts="")
