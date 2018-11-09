#!/usr/bin/python
import json
import click
import boto3

@click.group()
def cli():
    """Cli to manage parameters for your environments stored on parameter store."""
    pass

## Commands for the cli

@cli.command()
@click.argument( 'prefix_name')
@click.option(  '--output_file','-o', help= "File to output the variables",default="")
@click.option(  '--region', help= "Region where you want to execute the script",default="us-east-1")
def list_parameters(prefix_name, output_file, region):
    """This method will list all the parameters that match the prefix name,
       Optionaly you can output the content of this method to a file with the
       output_file option, so you can use that file to further operations with delete_parameters and add_parameters
       Generally helpfull when you want to delete all the variables of an environment,
       or you want to create a copy of the variables of an environment.
       The output file of this method is ready to use with add_parameters and delete_parameters methods
   """
    parameters=list_parameter_store(prefix_name, region)
    if output_file == "" :
        print(parameters)
    else:
        try:
            f= open(output_file,"w+")
            f.write( "{ \"parameters\" : { \n" + parameters + "\n } \n }")
            f.close()
            print("File was created successfully")
        except:
            print("There was an error writing to the file, check you have proper permissionse")

@cli.command()
@click.argument( 'prefix_name' )
@click.option(  '--parameters_file' , '-p' , default="./parameters.json"  )
@click.option(  '--region', default="us-east-1")
def add_parameters(prefix_name, parameters_file, region):
    """ This method is going to read the parameter_file and will
        create the parameters that are written on that file, but
        it will add the prefix_name to each one of those.
    """
    file = open(parameters_file, "r")
    Json = json.loads(file.read())
    file.close()
    upload_parameters_store(prefix_name , Json["parameters"] , region)

@cli.command()
@click.argument('parameter_name')
@click.argument('value')
@click.option( '--region', default="us-east-1")
def add_single_parameter(parameter_name, value, region):
    """ This method is going to add a parameter, see that this method,
        does not ask for prefix_name, so you need to write the entire name
        of the parameter and also its value, the value will be encrypted with KMS.
    """
    client_parameter_store = boto3.client('ssm',region_name=region)
    response = client_parameter_store.put_parameter(Name=parameter_name,Value=value,Type='SecureString',Overwrite=True)
    print(parameter_name + " was added")

@cli.command()
@click.argument( 'prefix_name' )
@click.option(  '--parameters_file' , '-p' , default="./parameters.json"  )
@click.option(  '--region', default="us-east-1")
def delete_parameters(prefix_name, parameters_file, region):
    """ This method is going to read the parameter_file and will
        delete the parameters that are written on that file, Each
        a prefix prefix_name will be added to that parameter before
        trying to delete it
    """
    file = open(parameters_file, "r")
    Json = json.loads(file.read())
    file.close()
    delete_parameters_from_parameter_store(prefix_name , Json["parameters"] , region)

@cli.command()
@click.argument('parameter_name')
@click.option( '--region', default="us-east-1")
def delete_single_parameter(parameter_name, region):
    """ This method is going to delete a parameter, see that this method,
        does not ask for prefix_name, so you need to write the entire name
        of the parameter.
    """
    client_parameter_store = boto3.client('ssm',region_name=region)
    try:
        response = client_parameter_store.delete_parameter(Name=parameter_name)
        print(parameter_name + " was deleted")
    except:
        print(parameter_name + " does not exist")



@cli.command()
@click.option( '--region', default="us-east-1")
def list_prefixes(region):
    """ This method is going to check your aws account, in the region that you set
        And it will show you, the current prefixes that are already created
    """
    client_parameter_store = boto3.client('ssm',region_name=region)
    NextToken=""
    prefixes = []
    response = client_parameter_store.describe_parameters(MaxResults=50)
    while True :
        for key in response['Parameters']:
            prefix = key['Name'].split("/")
            prefix = prefix[slice(len(prefix)-1)]
            prefix = "/".join(prefix) + "/"
            if prefixes.count(prefix) == 0 :
                prefixes.append(prefix)

        if 'NextToken' in response :
            NextToken=response['NextToken']
            response = client_parameter_store.describe_parameters(MaxResults=50, NextToken=NextToken )
        else:
            break
    print ('\n'.join(prefixes))

## Helper methods

def delete_parameters_from_parameter_store(prefix_name , parameters , region):
    client_parameter_store = boto3.client('ssm',region_name=region)
    print("Deleting parameters from file")
    for key, value in parameters.iteritems():
        try:
            response = client_parameter_store.delete_parameter(Name=prefix_name + key)
            print(key)
        except:
            print(prefix_name + key + " does not exist")


def upload_parameters_store(prefix_to_parameter_store , parameters , region):
    client_parameter_store = boto3.client('ssm',region_name=region)
    for key, value in parameters.iteritems():
        response = client_parameter_store.put_parameter(Name=prefix_to_parameter_store + key,Value=value,Type='SecureString',Overwrite=True)
        print("Parameter " + key + " added ")

def list_parameter_store(prefix_name , region):
    print("Listing parameters for " + prefix_name + "...")
    client_parameter_store = boto3.client('ssm',region_name=region)
    output=""
    response = client_parameter_store.describe_parameters(MaxResults=50)
    while True :
        for key in response['Parameters']:
            parameter_name  =  key['Name']
            parameter_value =  client_parameter_store.get_parameter(Name=parameter_name,WithDecryption=True )
            complete_name   =  parameter_name.split("/")
            prefix          =  complete_name[slice(len(complete_name)-1)]
            prefix          =  "/".join(prefix) + "/"
            if prefix == prefix_name :
                if output == "" :
                    output = "\"" + "".join(complete_name[slice(len(complete_name)-1,len(complete_name))]) + "\" : \"" + parameter_value['Parameter']['Value'] + "\""
                else:
                    output = output + ",\n\"" + "".join(complete_name[slice(len(complete_name)-1,len(complete_name))]) + "\" : \"" + parameter_value['Parameter']['Value'] + "\""

        if 'NextToken' in response :
            NextToken=response['NextToken']
            response = client_parameter_store.describe_parameters(MaxResults=50, NextToken=NextToken )
        else:
            break
    return output


if __name__ == '__main__':
    cli()
