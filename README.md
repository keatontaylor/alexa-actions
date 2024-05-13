# Alexa Actionable notifications with Tailscale

[![release][release-badge]][release-url]
![downloads][downloads-badge]
![build][build-badge]
[![CodeQL](https://github.com/MelleD/alexa-actions/actions/workflows/codeql.yml/badge.svg)](https://github.com/MelleD/alexa-actions/actions/workflows/codeql.yml) 
[![Formatting & Linting](https://github.com/MelleD/alexa-actions/actions/workflows/formating_linting.yml/badge.svg)](https://github.com/MelleD/alexa-actions/actions/workflows/formating_linting.yml)

<a href="https://www.paypal.me/MelleDennis" target="_blank"><img src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/pplogo.png" alt="PayPal.Me MelleDennis" style="height: 50px !important;width: 50px !important;" ></a>

<a href="https://www.buymeacoffee.com/melled" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>


## Introduction

This integration was forked from the [alexa-actions](https://github.com/keatontaylor/alexa-actions). Big thanks to this create project. 
I hope the open pull request will be merged at some point and the projects get married. In the meantime, I maintain the fork and some documentation in the README

I give no guarantee for the functionality and no promise of lifelong maintenance, as I do the whole thing in my free time. Of course, I am happy about every contribution and PullRequest :heart:

Please ⭐️ or sponsor this repo when you like it :heart:.

Also thanks to the amazing [Tailscale](https://www.home-assistant.io/integrations/tailscale/)integrations!

## Getting started


## Installation

### Getting started

See for some basic information the available [wiki] (https://github.com/keatontaylor/alexa-actions/wiki)

### Step 1 Setup repository with AWS

Here are some steps you need to take. Since this guide is fairly new, please create a ticket or PR to resolve any confusion.
The premise is that  [Tailscale](https://www.home-assistant.io/integrations/tailscale/) Integration is installed in HA and the HA instance is available as a node.

1. The Git repo must be forked so that the Docker image for the AWS Lambda can be pushed to your private repository in the Amazon Elastic Container Registry.
1. Create a private repository on AWS [Amazon Elastic Container Registry](https://aws.amazon.com/de/ecr/). The name must be _ha-custom-lambda-tailscale_ for the repo
<img alt="ecr-private" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/ecr_private.png">

See for more information [AWS Introduction ECR] (https://aws.amazon.com/de/ecr/getting-started/)

1. Create a keypair on AWS Identity Management (IM) to allow github action to push the Docker image to ECR.
Create AWS_ACCESS_KEY_ID_ and _AWS_SECRET_ACCESS_KEY_
<img alt="Zugriff Schlüssel" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/zugriff_key.png">

See for more information [AWS Introduction credentials] (https://docs.aws.amazon.com/de_de/keyspaces/latest/devguide/access.credentials.html#SigV4_credentials)

Remember both carefully because the secret is only displayed once and is required in the next step.

1. Go to your forked repo under settings. Go to secrets and variables. Create two new secrets with _AWS_ACCESS_KEY_ID_ and _AWS_SECRET_ACCESS_KEY_ from the previous step
<img alt="github secret" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/github_secret.png">

1. Then build and push the Docker image under Github Actions. To do this, run ```.github/workflows/docker-build-push.yml```
<img alt="githubaction" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/githubaction.png">


**Congratulations! This is the first step and the result should look like this.** :confetti_ball:

### Step 2 Create AWS Lamdba

1. Create a new function. Select Container Image at the top
<img alt="Add Lambda" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/add_lambda.png">

See for more information [AWS Lambda] (https://docs.aws.amazon.com/de_de/lambda/latest/dg/getting-started.html)

1. Name the function alexa-actionable-notifications-function and select the Docker image from the ECR and click create function
<img alt="Select Container Lambda" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/select_container_lambda.png"> 

<img alt="Create Lambda" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/create_lambda.png"> 
<img alt="Overview Lambda" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/overview_lambda.png"> 


1. Click "Add Trigger" and copy your skill id from the previous step from the [Skill](https://developer.amazon.com/alexa/console/ask)

<img alt="Lambda Alexa Skill" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/lambda_alexa_skill.png"> 
<img alt="Trigger" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/trigger.png"> 


1. Now we have to log in to our Tailscale account and create an ephemeral key. Go to settings --> key
<img alt="Key" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/key.png"> 

<img alt="Key1" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/key1.png"> 
Please remember the key. You currently have to do this step every 3 months because the key can no longer be created.

1. An HA long-living token (10 years) must then be created that Lambda can access to your HA-Instance, which is only available into your VPN. Please remember the key.

1. Now the following ENV variables must be inserted into the function.
<img alt="Key1" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/ha_env.png"> 


| ENV                       | Type     | Default       | Description                                           |
| ------------------------- | -------- | ------------- | ----------------------------------------------------- |
| DEBUG                     | boolean  | false         | Type of the card.                                     |
| HA_TOKEN                  | string   |               | The long living HA token                              |
| HA_URL                    | string   |               |**Important the TAILSCALE ip from HA** e.g http://{tailscale-ha-ip}:8123. Should be start with 100.xxx.xxx.xxx TAILSCALE_AUTHKEY the ephemeral key. Should be start with tskey-auth-xxxxx          |


1. Save function to deploy the function new

Now the Alexa skill can be tested and integrated into HA. These are the same steps like in the [wiki](https://github.com/keatontaylor/alexa-actions/wiki/Alexa-Talking-to-Home-Assistant-(The-Skill))

The only thing that changes in the Alexa Skill chapter in the editor is that you don't have to create a PY for the template. 
Actually always click Customize

Troubleshooting:
I rarely get timeouts from tailscale. [Ticket](https://github.com/tailscale/tailscale/issues/11886) is open. That's why I increased the timeout to 10 seconds.

<img alt="Troubleshooting" src="https://github.com/MelleD/alexa-actions/blob/main/docs/images/trouble.png"> 


## Danger :bangbang:

The ECR and the AWS Lambda can cost money. For this reason the image was kept small.
But you need to have a lot of traffic and updates. With testing and everything, my most expensive month was 4 cents :heart:

## Known limitations

1. Cannot create a ephemeral key automatically
1. I rarely get timeouts from tailscale. [Ticket](https://github.com/tailscale/tailscale/issues/11886) is open. That's why I increased the timeout to 10 seconds.

<!-- Badges -->

[release-badge]: https://img.shields.io/github/v/release/MelleD/alexa-actions?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/MelleD/alexa-actions/total?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/MelleD/alexa-actions/build-linux.yml?branch=main&style=flat-square

<!-- References -->

[home-assistant]: https://www.home-assistant.io/
[hacs]: https://hacs.xyz
[release-url]: https://github.com/MelleD/alexa-actions/releases