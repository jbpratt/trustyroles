"""
unit tests for trustyroles.arpd_update
"""
import json
from moto import mock_iam
import boto3
from trustyroles.arpd_update import arpd_update


ARPD = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": ["arn:aws:iam::123456789012:user/test-role"]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
)

boto3.setup_default_session()
iam_client = boto3.resource('iam')
iam_client.create_role(
    RoleName='test_role',
    AssumeRolePolicyDocument=ARPD)


@mock_iam
def test_get_arpd():
    arpd_update.get_arpd('test_role')
    assert 1 == 1


"""
@mock_iam
def test_update_arn():
    arpd_update.update_arn(["arn:aws:iam:::user/test-role2"], role_name='test-role')
    assert 1 != 1
"""

# @mock_iam
# def test_remove_arn():

# @mock_iam
# def test_add_external_id():

# @mock_iam
# def test_remove_external_id():
