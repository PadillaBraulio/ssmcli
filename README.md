# Uploading parameters and secrets

This script will upload parameters to parameter store

## Getting Started

These instructions will allow you to update secrets values on secret manager and non-secret values on parameter store.

### Prerequisites

Select the correct AWS profile, install the requirements for the script.
```
export AWS_PROFILE=af
pip install -r requirement.txt
```
The parameter.json file have the following format.
```
{
  "parameters":{
    "parameter1":"value1"
    "parameter2":"value2"
  }
}
```
Fill your file with that format. the script will replace or create  (if it doesnt exist) the parameters.

### Optional post installation

You can copy the ssmcli.py file to your /usr/local/bin/ with the name *ssmcli*, so you can use it as you were using another cli, without invoking it with python.

### Usage

This cli has six methods.

- add-parameters
- add-single-parameter
- delete-parameters
- delete-single-parameter
- list-parameters
- list-prefixes

Each method has their own help page, so you can check the functionality of each method and what parameter and arguments is expecting each method.

```
# To check available methods
ssmcli --help
# To check specific method information
ssmcli add-parameters --help
ssmcli delete-parameters --help
```
