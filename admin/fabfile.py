from hashlib import md5
from pathlib import Path

from invoke import task
import requests


def sudo_put(ctx, local, remote, chown=None):
    tmp = str(Path('/tmp') / md5(remote.encode()).hexdigest())
    ctx.put(local, tmp)
    ctx.run('sudo mv {} {}'.format(tmp, remote))
    if chown:
        ctx.run('sudo chown {} {}'.format(chown, remote))


@task
def system(ctx):
    ctx.run('sudo apt update')
    ctx.run('sudo apt install -y python3.6 nginx')
    ctx.run('sudo mkdir -p /srv/zam')
    ctx.run('sudo mkdir -p /srv/zam/letsencrypt/.well-known/acme-challenge')
    ctx.run('sudo useradd -N zam -d /srv/zam/ || exit 0')
    ctx.run('sudo chown zam:users /srv/zam/')
    ctx.run('sudo chsh -s /bin/bash zam')


@task
def http(ctx):
    sudo_put(ctx, 'letsencrypt.conf', '/etc/nginx/snippets/letsencrypt.conf')
    sudo_put(ctx, 'ssl.conf', '/etc/nginx/snippets/ssl.conf')
    certif = "/etc/letsencrypt/live/zam.beta.gouv.fr/fullchain.pem"
    exists = ctx.run('if [ -f "{}" ]; then echo 1; fi'.format(certif))
    if exists.stdout:
        conf = 'nginx-https.conf'
    else:
        # Before letsencrypt.
        conf = 'nginx-http.conf'
    sudo_put(ctx, conf, '/etc/nginx/sites-enabled/default')
    ctx.run('sudo systemctl restart nginx')


@task
def bootstrap(ctx):
    system(ctx)
    http(ctx)
    letsencrypt(ctx)
    basicauth(ctx)
    # Now put the https ready Nginx conf.
    http(ctx)


@task
def basicauth(ctx):
    ctx.run('sudo apt update')
    ctx.run('sudo apt install -y apache2-utils')
    # Will prompt for password.
    ctx.run('sudo htpasswd -c /etc/nginx/.htpasswd demozam')


@task
def letsencrypt(ctx):
    ctx.run('sudo add-apt-repository ppa:certbot/certbot')
    ctx.run('sudo apt update')
    ctx.run('sudo apt install -y certbot software-properties-common')
    sudo_put(ctx, 'certbot.ini', '/srv/zam/certbot.ini')
    sudo_put(ctx, 'ssl-renew', '/etc/cron.weekly/ssl-renew')
    ctx.run('chmod +x /etc/cron.weekly/ssl-renew')
    ctx.run('certbot certonly -c /srv/zam/certbot.ini --non-interactive '
            '--agree-tos')


@task
def sshkeys(ctx):
    for name, url in ctx.config.get('ssh_key_urls', {}).items():
        key = requests.get(url).text.replace('\n', '')
        ctx.run('grep -q -r "{key}" .ssh/authorized_keys '
                '|| echo "{key}" '
                '| sudo tee --append .ssh/authorized_keys'.format(key=key))


@task
def deploy(ctx, source):
    sudo_put(ctx, source, '/srv/zam/index.html', chown='zam')
