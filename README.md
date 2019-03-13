# param-pusher

Push secrets to SSM Parameter Store from YAML

## Requirements

See `requirements.txt`, but mainly: 

* Python3 (built on 3.7.2)
* boto3 (built on 1.9.112)
* ruamel.yaml (built on 0.15.89)


## Usage

`python param-pusher.py -h`

```
usage: param-pusher.py [-h] [-c CONFIG] [-p PROFILE] [-s SECRETS]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The config file to use
  -p PROFILE, --profile PROFILE
                        The profile in config file to use
  -s SECRETS, --secrets SECRETS
                        The secrets file
```                        

## Config

Defaults to `config/pp.ini`

Specify a different config file with the `-c` or `--config` option

e.g. `python param-pusher.py -c /path/to/config.ini`

The config file uses profile blocks. Specify a profile with the `-p` or `--profile` option

e.g. `python param-pusher.py -p example-profile`

The `DEFAULTS` profile will override any unset values in your profile

Uses ConfigParser https://docs.python.org/3/library/configparser.html

```
[example-profile]
basePath	= /param-pusher/test/example-profile
keyId		= alias/aws/ssm
roleARN		= arn:aws:iam::account-id:role/role-name
```

* basePath - a path prefix for all your secrets
* keyId - the AWS KMS key used to encrypt your secrets (empty will use your default key)
* roleARN - the ARN of the role you need to assume (if any)

General AWS credentials are managed the same way you would any `boto` interaction. See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

## Secrets

Defaults to `secrets/secrets.yml`

Specify a different secrets file with the `-s` or `--secrets` option

e.g. `python param-pusher.py -s /path/to/secrets/file.yml`

String value secrets should be placed under `strings:`

Secrets that should be read from a file should be placed under `files:`

No strings/files? Remove the relevant block or leave it empty. Fails in an ugly way if the secrets file is empty. 

Sample YAML:

```
strings:
  - mangodb:
      user: "admin"
      pass: "password"
  - other: 
      secret1: "my secret"
      secret2: "my other secret"
      cabbages:
        andkings: "0y5t3rZ"
  - app:
      frontend:
        user: "AzureDiamond"
        pass: "hunter2"
      backend:
        user: "Swordfish"
        pass: "correct horse feathers"
files:
  - mangodb:
      cacert: "files/cert.pem"
```

This will create the following secrets in Param Store:

* $BASEPATH/mangodb/user
* $BASEPATH/mangodb/pass
* $BASEPATH/other/secret1
* $BASEPATH/other/secret2
* $BASEPATH/other/cabbages/andkings
* $BASEPATH/app/frontend/user
* $BASEPATH/app/frontend/pass
* $BASEPATH/app/backend/user
* $BASEPATH/app/backend/pass
* $BASEPATH/mangodb/cacert


## License

GNU General Public License v3.0

See COPYING to see the full text.
