# Server install

## Requirements

*   Python 3.6+
*   Having a ssh key-based root access

## Installing dependencies

1.  Go to `admin`
2.  Run `python3 -m venv ~/.virtualenvs/zam-admin`
3.  Activate `source ~/.virtualenvs/zam-admin/bin/activate`
4.  Install `pip install -r requirements.txt`

## Adding somebody

1.  Install dependencies (see above) and/or activate venv
2.  Add the public key to `admin/fabric.yml` under `ssh_keys` section
3.  Run `fab -eH ubuntu@zam-test.beta.gouv.fr sshkeys`

## Bootstrapping server

⚠️ Only required once.

1.  Install dependencies (see above) and/or activate venv
2.  Run `fab -eH ubuntu@zam-test.beta.gouv.fr bootstrap`
3.  Note that a password for Basic Auth access will be prompted

## Deploying changelog

1.  Edit the `CHANGELOG.md` file at the root of the repository
2.  Install dependencies (see above) and/or activate venv
3.  Run `fab -eH ubuntu@zam-test.beta.gouv.fr deploy-changelog`

## Deploying répondeur

1.  Run `fab -eH ubuntu@zam-test.beta.gouv.fr deploy-repondeur --branch=master`
