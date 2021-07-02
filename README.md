# cfn-cr-sc-product-provider
A custom resource for managing service catalog products

## Usage

### UpdateProvisioningArtifactFunction

To use this custom resource add the following snippet to a cloudformation template:
```yaml
  UpdateProductVersions:
    Type: Custom::ProductProvider
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-sc-product-provider-UpdateProvisioningArtifactFunctionArn'
      ProductId: !Ref MyProductId
      ProvisioningArtifactActive: "True"
      ProvisioningArtifactGuidance: "DEPRECATED"
      ProvisioningArtifactAction: "ALL_EXCEPT_LATEST"
```

Properties:
* ProductId [required] - The service catalog product ID (i.e. prod-iugafjcy2eyro).
* ProvisioningArtifactActive - Indicates whether the product version is active.
  Inactive provisioning artifacts are invisible to end users. End users cannot launch
  or update a provisioned product from an inactive provisioning artifact. Allowed
  values are True|False.  Default is "True"
* ProvisioningArtifactGuidance - The value to apply to the product version guidance.
  Allowed values are DEFAULT|DEPRECATED.  Default value is "DEFAULT"
* ProvisioningArtifactAction - ALL to apply to all artifacts, ALL_EXCEPT_LATEST to
  apply to all except latest artifact.  Default value is "ALL"

More info about properties can be found in the
[update_provisioning_artifact API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/servicecatalog.html#ServiceCatalog.Client.update_provisioning_artifact)

## Development

### Contributions
Contributions are welcome.

### Requirements
Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Create a local build

```shell script
$ sam build
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```shell script
$ python -m pytest tests/ -v
```

### Run integration tests
Running integration tests
[requires docker](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html)

```shell script
$ sam local invoke HelloWorldFunction --event events/event.json
```

## Deployment

### Deploy Lambda to S3
Deployments are sent to the
[Sage cloudformation repository](https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/index.html)
which requires permissions to upload to Sage
`bootstrap-awss3cloudformationbucket-19qromfd235z9` and
`essentials-awss3lambdaartifactsbucket-x29ftznj6pqw` buckets.

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/cfn-cr-sc-product-provider.yaml

aws s3 cp .aws-sam/build/cfn-cr-sc-product-provider.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cr-sc-product-provider/master/
```

## Publish Lambda

### Private access
Publishing the lambda makes it available in your AWS account.  It will be accessible in
the [serverless application repository](https://console.aws.amazon.com/serverlessrepo).

```shell script
sam publish --template .aws-sam/build/cfn-cr-sc-product-provider.yaml
```

## Install Lambda into AWS

### Sceptre
Create the following [sceptre](https://github.com/Sceptre/sceptre) file
config/prod/cfn-cr-sc-product-provider.yaml

```yaml
template_path: "remote/cfn-cr-sc-product-provider.yaml"
stack_name: "cfn-cr-sc-product-provider"
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
hooks:
  before_launch:
    - !cmd "curl https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/cfn-cr-sc-product-provider/master/cfn-cr-sc-product-provider.yaml --create-dirs -o templates/remote/cfn-cr-sc-product-provider.yaml"
```

Install the lambda using sceptre:
```shell script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-cr-sc-product-provider.yaml
```

### AWS Console
Steps to deploy from AWS console.

1. Login to AWS
2. Access the
[serverless application repository](https://console.aws.amazon.com/serverlessrepo)
-> Available Applications
3. Select application to install
4. Enter Application settings
5. Click Deploy

## Releasing

We have setup our CI to automate a releases.  To kick off the process just create
a tag (i.e 0.0.1) and push to the repo.  The tag must be the same number as the current
version in [template.yaml](template.yaml).  Our CI will do the work of deploying and publishing
the lambda.
