import json
import logging
import argparse
import boto3

LOGGER = logging.getLogger('IAM-ROLE-TRUST-POLICY')
logging.basicConfig(level=logging.INFO)
PARSER = argparse.ArgumentParser()


def _main():
    """The _main method can take in a list of ARNs, role to update,
        and method [get, update, remove]."""
    PARSER.add_argument(
        '-a', '--arn',
        type=str,
        nargs='+',
        required=False,
        help='Add new ARNs to trust policy. Takes a comma-seperated list of ARNS.'
    )

    PARSER.add_argument(
        '-u', '--update_role',
        type=str,
        required=True,
        help='Role for updating trust policy. Takes an role friendly name as string.'
    )

    PARSER.add_argument(
        '-m', '--method',
        type=str,
        required=False,
        choices=['update', 'remove', 'get'],
        help='Takes choice of method to update, get, or remove.'
    )

    PARSER.add_argument(
        '-e', '--add_external_id',
        type=str,
        required=False,
        help='Takes an external id as a string.'
    )

    PARSER.add_argument(
        '-r', '--remove_external_id',
        type=str,
        required=False,
        help='Takes an external id as a string.'
    )

    PARSER.add_argument(
        '-j', '--json',
        action='store_true',
        required=False,
        help='Add to print json in get method.'
    )

    args = vars(PARSER.parse_args())

    if args['method'] == 'update':
        update_arn(
            args['arn'],
            args['update_role']
        )
    elif args['method'] == 'remove':
        remove_arn(
            args['arn'],
            args['update_role']
        )
    elif args['method'] == 'get':
        if args['json']:
            get_arpd(
                args['update_role'],
                json_flag=True
            )
        else:
            get_arpd(
                args['update_role']
            )

    if args['add_external_id'] is not None:
        add_external_id(
            external_id=args['add_external_id'],
            role_name=args['update_role']
        )
    if args['remove_external_id'] is not None:
        remove_external_id(
            external_id=args['remove_external_id'],
            role_name=args['update_role']
        )

def get_arpd(role_name, json_flag=False):
    """The get_arpd method takes in a role_name as a string
        and provides trusted ARNS and Conditions."""
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName=role_name)
    ardp = role['Role']['AssumeRolePolicyDocument']

    if json_flag:
        print(json.dumps(ardp['Statement'][0], indent=4, sort_keys=True))
    else:
        print(f"\nARNS:")
        if isinstance(ardp['Statement'][0]['Principal']['AWS'], list):
            for arn in ardp['Statement'][0]['Principal']['AWS']:
                print(f"  {arn}")
        else:
            print(f"  {ardp['Statement'][0]['Principal']['AWS']}")
        print(f"Conditions:")
        if ardp['Statement'][0]['Condition']:
            print(f"  {ardp['Statement'][0]['Condition']}")

def add_external_id(external_id, role_name):
    """The add_external_id method takes an external_id and role_name as strings
        to allow the addition of an externalId condition."""
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName=role_name)
    ardp = role['Role']['AssumeRolePolicyDocument']
    if ardp['Statement'][0]['Condition'] is None:
        ardp['Statement'][0]['Condition'] = {'StringEquals': {"sts:ExternalId": external_id}}
    else:
        ardp['Statement'][0]['Condition'] = {'StringEquals': {'sts:ExternalId': external_id}}

    iam_client.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(ardp)
    )
def remove_external_id(external_id, role_name):
    """The remove_external_id method takes an external_id and role_name as strings
        to allow the removal of an externalId condition."""
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName=role_name)
    ardp = role['Role']['AssumeRolePolicyDocument']

    if ardp['Statement'][0]['Condition'] is not None:
        ardp['Statement'][0]['Condition'] = {}
        iam_client.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(ardp)
        )

def update_arn(arn_list, role_name):
    """The update_arn method takes a list of ARNS(arn_list) and a role_name
        to add to trust policy of suppplied role."""
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName=role_name)
    ardp = role['Role']['AssumeRolePolicyDocument']
    old_principal_list = ardp['Statement'][0]['Principal']['AWS']

    for arn in arn_list:
        if arn not in old_principal_list:
            if isinstance(old_principal_list, list):
                [old_principal_list.append(arn) for arn in arn_list]
                ardp['Statement'][0]['Principal']['AWS'] = old_principal_list
            else:
                new_principal_list = []
                for arn in arn_list:
                    new_principal_list.append(arn)
                new_principal_list.append(old_principal_list)
                ardp['Statement'][0]['Principal']['AWS'] = new_principal_list

    for arn in arn_list:
        LOGGER.info("Updating Policy to add: '%s'", arn)

    iam_client.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(ardp)
    )

def remove_arn(arn_list, role_name):
    """The remove_arn method takes in a list of ARNS(arn_list) and a role_name
        to remove ARNS from trust policy of supplied role."""
    iam_client = boto3.client('iam')
    role = iam_client.get_role(RoleName=role_name)
    ardp = role['Role']['AssumeRolePolicyDocument']
    old_principal_list = ardp['Statement'][0]['Principal']['AWS']

    for arn in arn_list:
        if arn in old_principal_list:
            old_principal_list.remove(arn)

    ardp['Statement'][0]['Principal']['AWS'] = old_principal_list

    for arn in arn_list:
        LOGGER.info("Updating Policy to remove: '%s'", arn)

    iam_client.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(ardp)
    )

if __name__ == "__main__":
    _main()
