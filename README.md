# Amazon Dash Button for Uber

Amazon Dash Buttons are small, $5 plastic buttons with a battery and a WiFi connection inside. Rather than have my Dash Button order 
products from the company like Amazon wants me to, I found a way to use my Dash Button to have an Uber Driver pick me up at my address.

# What You'll need to run this program

1. During activation of your Dash Button, do not connect a product to your dash button
2. You'll need the mac address of your Dash Button and notify your Wifi Network for it. (I used a python library called Scapy)
3. You'll also need a python client for the Uber API. (I used this https://github.com/tals/uber.py one , however, the Vehicle ID in the one is 
not updated. Feel free to use the modified one I included under the libs folder)
4. Now, fill in the following information in the AmazonDashForUber.py file
    amazonDashButtonMacAddress = 'yourDashMacAddressHere'
    uberUsername = 'yourUberUsernameHere'
    uberPassword = 'yourUberPasswordHere'
    uberPickUpAddress = 'yourPickUpAddressHere'

 Watch it in use at https://www.youtube.com/watch?v=b1eBnyHpWQU
 
 
# Credits

1. https://github.com/tals/uber.py for the Python Client Uber API
2. https://gist.github.com/eob/a8b5632f23e75b311df2#file-dash-listen-1-py for pointing out Scapy to me

