import argparse
import boto3
import collections
import configparser
import os
import sys
from pathlib import Path
from ruamel.yaml import YAML

def getPaths(d, parentKey='', separator='/'):
    items = []
    for k, v in d.items():
        newKey = parentKey + separator + k if parentKey else k
        if isinstance(v, collections.MutableMapping):
            items.extend(getPaths(v, newKey, separator).items())
        else:
            items.append((newKey, v))
    return dict(items)

def putParams(secrets, asFiles=False):
    secretType = "string"
    if asFiles:
        secretType = "file"
    print("Processing " + secretType + "s block...")
    if not secrets:
        print("Nothing to push: " + secretType + "s block is empty")
        return 1
    flatSecrets = {}
    for k in secrets:
        tmpDict = getPaths(k, '', '/')
        flatSecrets = {**flatSecrets, **tmpDict}

    for k, v in flatSecrets.items():
        value = v
        if asFiles:
            file = open(v,"r")
            fileContents = file.read()
            value = fileContents
        path = config[args.profile]['basepath'] + "/" + k
        resultMessage = "Putting secret " + path + " as " + secretType
        paramArgs = dict(
            Name=path,
            Description='Added by param-pusher',
            Value=value,
            Type='SecureString',
            Overwrite=True
        )
        if config[args.profile]['keyId']:
            paramArgs['KeyId'] = config[args.profile]['keyId']
        
        response = ssm.put_parameter(**paramArgs)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resultMessage += "... Success"
        else:
            resultMessage += "Error: " + response
        print(resultMessage)
    return 0


ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", help="The config file to use", default="config/pp.ini")
ap.add_argument("-p", "--profile", help="The profile in config file to use", default="DEFAULT")
ap.add_argument("-s", "--secrets", help="The secrets file", default="secrets/secrets.yml")
args = ap.parse_args()

setupError = False

if not os.path.isfile(args.config):
    print("Config file not found at " + args.config)
    setupError = True
if not os.path.isfile(args.secrets):
    print("Secrets file not found at " + args.secrets)
    setupError = True

config = configparser.ConfigParser()
config.read(args.config)

if not args.profile in config:
    print("No profile [" + args.profile + "] in " + args.config)
    setupError = True

if setupError:
    print("ERROR: Setup failed. Exiting.")
    sys.exit(1)


if config[args.profile]['rolearn']:
    sts = boto3.client('sts')
    assumedRoleObject = sts.assume_role(
        RoleArn=config[args.profile]['rolearn'],
        RoleSessionName="ParamPusherSession"
    )
    credentials=assumedRoleObject['Credentials']
    ssm = boto3.client(
        'ssm',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
else:
   ssm = boto3.client('ssm') 

secretsPath = Path(args.secrets)
yaml = YAML(typ='safe')
yaml.default_flow_style = False
secretsData = yaml.load(secretsPath)
if 'strings' in secretsData:
    stringSecrets = secretsData.get('strings')
    putParams(stringSecrets)
if 'files' in secretsData:
    fileSecrets = secretsData.get('files')
    putParams(fileSecrets, True)
print("Done.")

