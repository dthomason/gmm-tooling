# AWS Setup
## EBS Volume Creation
Currently we're using EBS Volumes for pods that require persistent storage.  This requires
you to do two things
 - Create the EBS Volume on AWS
 - Add the volume ID to the appropriate configMap so we can inject the value into the pod template when we're creating the pod

Here's what drives you'll need to create per each region:
|Container|Size (GiB)|Type|Purpose|
|--|--|--|--|
Kafka|500|st1|kafka-logs|
Prometheus|500|st1|prometheus-data|
Grafana|1|gp2|grafana-data|

## PostgreSQL DB Creation
Create a db in the same VPC (and preferrably same subnet) as the cluster.  I've been using a db instance with
the following characteristics:
 - Size: db.m3.large
 - HDD: 100 GB SSD

# Cluster Management Setup
Steps for working with Kubernetes cluster:
 - Ensure you have Bash for Windows installed as per [instructions](https://msdn.microsoft.com/en-us/commandline/wsl/install_guide)
 - Download `kubectl` via `..\rtb-ensemble\kubernetes\cluster-management\install-kubectl.sh` and make sure it is in your path
 - Get credentials from KeePass/Kubernetes group
     - Find the Kubernetes entry and open kubectl config
     - Click on the Advanced tab and there will be an attachment
     - Save the kubectl config to your local disk and copy it to `~/.kube/config` in the Linux subsystem
     - Get Kubernetes ssh keys to allow access to masters
            - `~/.ssh/dev_kube_rsa`
            - `~/.ssh/prd_kube_rsa`
 - Install [ktmpl](https://github.com/InQuicker/ktmpl) for working with templated Kubernetes YAML files
 - Setup kops
    - Install [kops](https://github.com/kubernetes/kops) as a robust cluster editing/deployment solution
 - Gulp tasks exist for performing common Kubernetes operations

The config contains information on each region we support.  You can only manage a single
Kubernetes cluster at a time with `kubectl`.  You can see which region you're currently
managing by:
```
kubectl config current-context
```

You can change which region you're currently managing by:
```
kubectl config use-context <context from config>
```
substituting the desired cluster for one listed in the `config`.  For example, to manage
our cluster in the AWS region in the `us-west-1` region:
```
kubectl config use-context aws_us-west-1
```

## Installing ktmpl
We're using [ktmpl](https://github.com/InQuicker/ktmpl) for making our Kubernetes templates generic. Kubernetes templates
[currently](https://github.com/kubernetes/kubernetes/blob/master/docs/proposals/templates.md) do not allow for the utilization
of variables within a template (and you call yourself a template), meaning that we would have to maintain a different template for
each AWS region that we deploy in to account for differences such as EBS backed volume IDs. ktmpl allows for the use of variables
to be specified within Kubernetes template files and follows the proposed spec which will soon be implemented by Kubernetes
natively, allowing for a (hopefully) seamless transition to a newer version of Kubernetes when templates are incorporated.

To get setup, first make sure you have Cargo (and why not Rust too while you're at it) installed
if not already installed
```
curl -sSf https://static.rust-lang.org/rustup.sh | sh
```

Install Build-Essential

```
apt-get install build-essential
```

Then, install ktmpl using Cargo
```
cargo install ktmpl
```

Make sure you add Cargo binaries to your path by putting something like this in your `~/.profile`, `~/.bashrc`,
[etc.](https://help.ubuntu.com/community/EnvironmentVariables#Persistent_environment_variables)

```
pathadd() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="${PATH:+"$PATH:"}$1"
    fi
}
pathadd ~/.cargo/bin
```

## kops
kops is used to deploy/modify Kubernetes clusters.  It's the best solution currently out there for easily working
with Kubernetes on AWS. We're running [v1.6.0](https://github.com/kubernetes/kops/releases/tag/v1.6.0). You might
need to install [Go](https://github.com/golang/go) as a prerequisite for kops, but try it without first.

If you find Go is required, using [Go Version Manager](https://github.com/moovweb/gvm) is the easiest way to work
with it. We're running with 1.7, so using GVM you can do something like this:

```
gvm install go1.7 -B
gvm use go1.7 --default
```

# Deployment
Most of the component deployment process is automated via gulp with just a few manual steps. Even though deploying of the
components is automated, the order in which their brought up is not as full automation of cluster deploys was not a huge
priority in an MVP.

When bringing up a new cluster, you will want to bring up the cluster features in this order:
 - services
 - configmaps
 - secrets
 - deployments

One place that requires manual intervention process is after creation of services as those endpoints need to be known and
filled out in the configmaps so that they can be consumed by other clusters which need to reach them.  Since we're using
SSH tunneling to connect cluster components that require it, we need to add the endpoints at which ssh is made available
to configmaps so that they can be read in by connections.  So you'll need to create the services and the use
`kubectl describe svc` to find out what the ELB endpoint is for those services.  If we setup DNS entries for those ELBs
we could skip this step as they'd be known before they're created but then we'd be exposing our SSH endpoints with
predictable URLs which might be bad.

## AZ CIDRs
kops usually picks a `\19` CIDR (something like `172.31.0.0/19`) for the subnet. When I
have to manually add another AZ, I've been trying to match theses settings:
|3rd Octet|AZ|
|--|--|
|32|a|
|64|b|
|128|c|
|192|d|
|224|e|

## Development
Here's how I initially deployed the development cluster using kops. We may want to change the sizes of things down the road.

### us-east-1.dev.teamac.me
```
export AWS_DEFAULT_PROFILE=dev
export AWS_PROFILE=dev
export NAME=us-east-1.dev.teamac.me
export KOPS_STATE_STORE=s3://programmatic-bidding/private/deployment/kops
kops create cluster --cloud=aws --zones=us-east-1b --master-size=m3.medium --node-count=2 --node-size=m4.large --ssh-public-key=~/.ssh/dev_kube_rsa.pub ${NAME}
kops update cluster us-east-1.dev.teamac.me --yes
```

### us-west-1.dev.teamac.me
```
export AWS_DEFAULT_PROFILE=dev
export AWS_PROFILE=dev
export NAME=us-west-1.dev.teamac.me
export KOPS_STATE_STORE=s3://programmatic-bidding/private/deployment/kops
kops create cluster --cloud=aws --zones=us-west-1b --master-size=m3.medium --node-count=2 --node-size=m4.large --ssh-public-key=~/.ssh/dev_kube_rsa.pub ${NAME}
kops update cluster us-west-1.dev.teamac.me --yes
```

## Production
### us-east-1.prd.teamac.me
```
export AWS_DEFAULT_PROFILE=prd
export AWS_PROFILE=prd
export NAME=us-east-1.prd.teamac.me
export KOPS_STATE_STORE=s3://acmeprogrammatic/private/deployment/kops
kops create cluster --cloud=aws --zones=us-east-1a --master-size=m3.medium --node-count=2 --node-size=m4.large --ssh-public-key=~/.ssh/prd_kube_rsa.pub ${NAME}
kops update cluster us-east-1.prd.teamac.me --yes
```

### us-west-1.prd.teamac.me
```
export AWS_DEFAULT_PROFILE=prd
export AWS_PROFILE=prd
export NAME=us-west-1.prd.teamac.me
export KOPS_STATE_STORE=s3://acmeprogrammatic/private/deployment/kops
kops create cluster --cloud=aws --zones=us-west-1a --master-size=m3.medium --node-count=2 --node-size=m4.large --ssh-public-key=~/.ssh/prd_kube_rsa.pub ${NAME}
kops update cluster us-west-1.prd.teamac.me --yes
```

# Manual Addition of Kubernetes Security Groups & Permissions
You'll need to add additional permissions to certain security groups to allow them to work with our architecture.

## Firewall Rules
When using NodePort to expose connectivity to a pod, Kubernetes exposes a random port in the range shown
below.  You'll need to add firewall rules to the VPC so that external address can access the following port ranges
on the minions.
|Type|Protocol|Port Range|Source|
|--|--|--|--|
Custom TCP Rule|TCP|30000 - 32767|0.0.0.0/0

## Programmatic-ReadOnlyAccessForSSHAuthorizedKeys
Add this to the Kubernetes master to allow it to pull in our SSH keys from our S3 bucket. 
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListingOfAuthorizedKeysFolderContents",
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::programmatic-bidding"
            ],
            "Condition": {
                "StringLike": {
                    "s3:prefix": [
                        "private/deployment/ssh/authorized_keys/*"
                    ]
                }
            }
        },
        {
            "Sid": "ReadOnlyAccessOfAuthorizedKeysFolderContents",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::programmatic-bidding/private/deployment/ssh/authorized_keys/*"
            ]
        }
    ]
}
```

## AmazonEC2ContainerRegistryReadOnly
Add this to our Master/Minions to allow them to pull containers from our private repos on ECR.
{
	"Version": "2012-10-17",
	"Statement": [{
		"Effect": "Allow",
		"Action": [
			"ecr:GetAuthorizationToken",
			"ecr:BatchCheckLayerAvailability",
			"ecr:GetDownloadUrlForLayer",
			"ecr:GetRepositoryPolicy",
			"ecr:DescribeRepositories",
			"ecr:ListImages",
			"ecr:BatchGetImage"
		],
		"Resource": "*"
	}]
}

# Slack Webhooks for Notifications
A Slack webhook integration is currently being used to alert when containers come online, and go offline. The scripts responsible for the posting are located at:
- `templates/secrets/post-start-slack-webhook.sh`
- `templates/secrets/pre-stop-slack-webhook.sh`

The webhook is additionally being used for the prometheus Alertmanager. The webhook url is defaulted in the alertmanager template:
- `templates/configmaps/alertmanager/alertmanager.yml`
