import json
import unittest

from product_provider import app


def get_file_contents(path):
  '''
  Parse the contents of a valid JSON string and convert it into
  a Python Dictionary
  :param path: path to file
  :return:
  '''
  with open(path, 'r') as file:
    data = file.read()

  return json.loads(data)

class TestProductProvider(unittest.TestCase):

  def test_get_provisioning_artifacts(self):
    data = get_file_contents('tests/unit/sc_describe_product.json')
    result = app.get_provisioning_artifacts(data)
    expected = [
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-mwv4usw5laf7s",
        "Name": "1.1.9",
        "Description": "Update for strides"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-psujhj3yglxmg",
        "Name": "1.0.0",
        "Description": "Baseline version."
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-nas2v5nrgcbua",
        "Name": "1.1.13",
        "Description": "Fix policies"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-ys2nqzbpg2hbw",
        "Name": "1.1.14",
        "Description": "Restore set_env_vars. 1436"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-wywm54o3dnehu",
        "Name": "1.1.10",
        "Description": "Include params in mapping"
      }
    ]
    self.assertListEqual(result, expected)

  def test_get_latest_provisioning_artifact(self):
    data = get_file_contents('tests/unit/provisioning_artifacts.json')
    result = app.get_latest_provisioning_artifact(data)
    expected = {
      "ProductId": "prod-vorrf6jrm57si",
      "ProvisioningArtifactId": "pa-ys2nqzbpg2hbw",
      "Name": "1.1.14",
      "Description": "Restore set_env_vars. 1436"
    }
    self.assertDictEqual(result, expected)

  def test_get_artifacts_to_update_all_except_for_latest(self):
    data = get_file_contents('tests/unit/provisioning_artifacts.json')
    result = app.get_artifacts_to_update(data, 'ALL_EXCEPT_LATEST')
    expected = [
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-mwv4usw5laf7s",
        "Name": "1.1.9",
        "Description": "Update for strides"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-psujhj3yglxmg",
        "Name": "1.0.0",
        "Description": "Baseline version."
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-nas2v5nrgcbua",
        "Name": "1.1.13",
        "Description": "Fix policies"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-wywm54o3dnehu",
        "Name": "1.1.10",
        "Description": "Include params in mapping"
      }
    ]
    self.assertListEqual(result, expected)

  def test_get_artifacts_to_update_all(self):
    data = get_file_contents('tests/unit/provisioning_artifacts.json')
    result = app.get_artifacts_to_update(data, 'ALL')
    expected = [
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-mwv4usw5laf7s",
        "Name": "1.1.9",
        "Description": "Update for strides"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-psujhj3yglxmg",
        "Name": "1.0.0",
        "Description": "Baseline version."
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-nas2v5nrgcbua",
        "Name": "1.1.13",
        "Description": "Fix policies"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-ys2nqzbpg2hbw",
        "Name": "1.1.14",
        "Description": "Restore set_env_vars. 1436"
      },
      {
        "ProductId": "prod-vorrf6jrm57si",
        "ProvisioningArtifactId": "pa-wywm54o3dnehu",
        "Name": "1.1.10",
        "Description": "Include params in mapping"
      }
    ]
    self.assertListEqual(result, expected)
