# Alexa Actions
This repository hopes to explain the setup process of getting a custom skill integrated with the latest Alexa Media Player Home Assistant component to create actionable notifications to your Amazon Echo (or clone) devices.

# Example
You have an automation to notify you that the front door has been left unlocked for 5 mins. Instead of a simple notification, the following could take place.

Alexa: "Hi, I've noticed your front door has been left unlocked for 5 mins, would you like me to lock it?"

You: "Yes"

The front door locks.

# How does this work?

Technically spekaing, this takes advantage of rountines that you've seen in the iOS/Android alexa app. It is now possible to trigger the activation of a specific skill via routine. This allows us to craft any automation in Home Assistant to trigger a custom skill.

What amazon does not allow, yet, is for us to call a skill with specific text from a routine. Instead you'll be dropped into the skill as if you had said "Alexa, open <skillname>". This is where the custom skill comes into play. We want a skill that when launched reaches out to our home assistant installation and gathers info on what actionable notification an automation has triggered. 

Effectively, reaching out to home assistant on the custom skill launch allows the skill to get the text we want it to speak and what event we would like triggered when the user responds yes/no.






