import boto3
import enum
import json
import logging
import os

from crhelper import CfnResource
from semver import VersionInfo

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def sc_client():
  return boto3.client('sc')

def get_env_var_value(env_var):
  '''Get the value of an environment variable
  :param env_var: the environment variable
  :returns: the environment variable's value, None if env var is not found
  '''
  value = os.getenv(env_var)
  if not value:
    log.warning(f'cannot get environment variable: {env_var}')

  return value

def get_latest_provisioning_artifact(provisioning_artifacts):
  '''
  Get the latest the latest version of a product's provisioning artifact.
  :param provisioning_artifacts: a list from get_provisioning_artifacts
  :return: a dict with the product's info about the latest provisioning artifact
  '''
  versions = []
  for provisioning_artifact in provisioning_artifacts:
    versions.append(provisioning_artifact['Name'])

  latest_version = max(versions, key=VersionInfo.parse)
  log.debug(f"latest version: {latest_version}")

  for provisioning_artifact in provisioning_artifacts:
    if VersionInfo.parse(latest_version) == VersionInfo.parse(provisioning_artifact['Name']):
      return provisioning_artifact


def get_provisioning_artifacts(product_info):
  '''
  Takes a list of SC product info and generates a list of provisioning
  artifacts with semantic version numbers in the Name field.

  We assume that the product's provisioning artifact summary names contains
  a version number, something (i.e. v1.0.0, v1.0.2, etc..).  We strip the `v`
  from the version names to conform to semantic versions so we can use it
  to compare version numbers.

  :param product_info: response from https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/servicecatalog.html#ServiceCatalog.Client.describe_product_as_admin
  :return: A list of the product's provisioned artifacts
  '''
  ProductId = product_info['ProductViewDetail']['ProductViewSummary']['ProductId']
  summaries = product_info['ProvisioningArtifactSummaries']
  artifacts = []
  for summary in summaries:
    # remove `v` from the name to get semver
    semantic_version = summary['Name'][1:]
    if not VersionInfo.isvalid(semantic_version):
      raise ValueError(f"invalid semantic version: {semantic_version}")

    artifact = {
      "ProductId": ProductId,
      "ProvisioningArtifactId": summary["Id"],
      "Name": semantic_version,
      "Description": summary["Description"]
    }
    artifacts.append(artifact)

  return artifacts


def get_artifacts_to_update(provisioning_artifacts, action):
  '''
  Get a list of provisioning artifacts to update
  :param provisioning_artifacts: a list from get_provisioning_artifacts
  :param action: the type of action for updating ALL|ALL_EXCEPT_LATEST
  :return: a list containing all of a product's provisioned artifacts
           except for the latest version
  '''
  artifacts = None
  if action == 'ALL':
    artifacts = provisioning_artifacts
  if action == 'ALL_EXCEPT_LATEST':
    latest_artifact = get_latest_provisioning_artifact(provisioning_artifacts)
    artifacts = []
    for provisioning_artifact in provisioning_artifacts:
      if provisioning_artifact['ProvisioningArtifactId'] != latest_artifact['ProvisioningArtifactId']:
        artifacts.append(provisioning_artifact)
  
  return artifacts

def update_provisioning_artifacts(provisioning_artifacts, action='ALL', active=True, guidance='DEFAULT'):
  '''
  Update the product's provisioned artifacts.
  :param provisioning_artifacts: a list from get_provisioning_artifacts
  :param action: the action to take, ALL|ALL_EXCEPT_LATEST
  :param active: indicates whether the product version is active, True|False
  :param guidance: guidance to end users about which provisioning artifacts to use, 'DEFAULT'|'DEPRECATED'
  :return:
  '''
  artifacts = get_artifacts_to_update(provisioning_artifacts, action)
  log.debug(f"Provisioning artifacts to update: {artifacts}")
  for artifact in artifacts:
    response = sc_client.update_provisioning_artifact(
      ProductId=artifact['ProductId'],
      ProvisioningArtifactId=artifact['ProvisioningArtifactId'],
      Active=active,
      Guidance=guidance
    )

@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.debug('Start Lambda processing')

  product_id = get_env_var_value('PRODUCT_ID')
  provisioning_artifact_active = get_env_var_value('PROVISIONING_ARTIFACT_ACTIVE')
  provisioning_artifact_guidance = get_env_var_value('PROVISIONING_ARTIFACT_GUIDANCE')
  provisioning_artifact_action = get_env_var_value('PROVISIONING_ARTIFACT_ACTION')

  product_info = sc_client.describe_product_as_admin(Id=product_id)
  log.debug(f"Product info: ${product_info}")
  provisioning_artifacts = get_provisioning_artifacts(product_info)
  log.debug(f"All provisioning_artifacts: ${provisioning_artifacts}")
  update_provisioning_artifacts(provisioning_artifacts,
                                active=provisioning_artifact_active,
                                action=provisioning_artifact_guidance,
                                guidance=provisioning_artifact_action)

@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass

def lambda_handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
