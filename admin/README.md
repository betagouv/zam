# Server install

## Requirements

*   Python 3.6+

## Installing dependencies

1.  Got to `admin`
2.  Run `python3 -m venv ~/.virtualenvs/zamadmin`
3.  Activate `source ~/.virtualenvs/zamadmin/bin/activate`
4.  Install `pip install -r requirements.txt`

## Adding somebody

1.  Install dependencies (see above) and/or activate venv
2.  Add the public key to `admin/fabric.yml` under `ssh_keys` section
3.  Run `fab -eH root@zam.beta.gouv.fr sshkeys`

## Bootstraping server

⚠️ Only required once.

1.  Install dependencies (see above) and/or activate venv
2.  Run `fab -eH root@zam.beta.gouv.fr bootstrap`
3.  Note that a password for Basic Auth access will be prompted

## Deploying client

1.  Generate the `index.html` file from sensitive sources
2.  Install dependencies (see above) and/or activate venv
3.  Run `fab -eH root@zam.beta.gouv.fr deploy --source=path/to/output/`
