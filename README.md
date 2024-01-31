# Alexa Actionable notifications ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/keatontaylor/alexa-actions?label=Release&style=flat-square) ![GitHub](https://img.shields.io/github/license/keatontaylor/alexa-actions?label=Licence&style=flat-square)

## This fork was updated with the following (see commit notes for more details):
- EN-US.json
  - AMAZON.Person slot was deleted and replaced with AMAZON.FirstName with "User1Name" and "User2Name" (with nickname) as samples. **NOTE: Update with your user names/nicknames.
  - New "Intents" slot was created with common intent triggers, including current (1/2024) Assist intents. **NOTE: Update to add your own intents.
  - New "UserIntent" created that listens for {Users} listed in the AMAZON.FirstName slot.
  - "StringIntent" edited to listen for {Strings} based on the new Intent slot.
 
- const.py and lambda_function.py
  - Edited to include "UserResponse" event type.
 
- configuration.yaml
  - Added input_text helpers to save the skill's incoming data and data that is returned by Assist.
  - Added input_boolean helper to determine if there is an Alexa Actionable Notification event in progress or not.
  - Edited the script to include turning on the input_boolean. **NOTE: You need to add turning it off at the end of your response automations.
 
- new_automations.yaml (NEW)
  - Added automation that turns off the input_boolean after one minute. This is a catch-all, just in case your response automation fails or you forget to include turning it off.
  - Added automation that saves the incoming event data to the new input_text helper.
  - Added automation that listens for user-initiated incoming requests. There is a sample that uses Choose to create a custom response. The default action is to pass the message to Assist and announce the Assist response (plus save response in the new input_text helper).
 
About the custom response:
My sample triggers finding a users phone by looking for "find", then "userName", then turning on a find_userName_phone toggle. [Check this out](https://github.com/foxymichelle/Home-Assistant-Find-Phone/tree/main) for my Find Phone automations, including triggering an Alexa Actionable Notification if the user is not home, asking if you'd like to proceed, then completing the action based on your response. 

## ----- Original Content -----

Alexa Actionable Notifications allows Home Assistant users to create interactions and workflows using Alexa.

Thanks to the amazing HACS integrations [Alexa Media Player](https://github.com/custom-components/alexa_media_player/) this allows you to not only talk using you alexa device but also get responses and take actions accordingly!

## 📥 Getting Started
To get started, head over to the [Wiki](https://github.com/keatontaylor/alexa-actions/wiki).

## 🤝 Acknowledgement
Thanks to [@alandtse](https://github.com/alandtse) for his continued worked on the Alexa Media Player custom component.

## 📧 CONTACT
Join [Zeus Developers Discord](https://discord.gg/yw2DkWZKpB) to get help with your integration

## 📝 CONTRIBUTING
Want to help us maintain this awesome feature? 

You can do so by contributing with code and helping us fix bugs or if you prefer to support us financially feel free to use the links bellow:

Creator of Alexa Actions Keaton Taylor:

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/ogFeLZl)

Contributor and Maintainer DeadSec-Security (AKA: Zeus):

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/zeus500k)


## 🤝 Contributors
<a href="https://github.com/keatontaylor/alexa-actions/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=keatontaylor/alexa-actions"/>
</a>

Made with [contrib.rocks](https://contrib.rocks).

