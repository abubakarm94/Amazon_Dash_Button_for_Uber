#import all necessary library
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import json
from os import path
import shlex
import signal
import time
from uber import UberClient, geolocate, ClientStatus, UberException
from uber.model_base import Model, StringField
import sys
from scapy.all import *



#set up all the data we will be needing
amazonDashButtonMacAddress = 'yourAmazonDashButtonMacAddress'
uberUsername = 'yourUberUsernameHere'
uberPassword = 'yourUberPasswordHere'
uberPickUpAddress = 'yourPickupAddressHere'
#uber client
global client



def do_checkout_address(address):
  #looks up an address
  result = geolocate(address)
  for entry in result:
      print "pick up at " + entry['formatted_address']+'\n'

def ping_address_for_available_vehicles(address):
  #shows you available cars close to you
  global client
  if not address:
    print
    
  results = geolocate(address)
  if not results:
    print 'address not found '
    return

  geodecoded_address = results[0]
  print 'searching for available vechicles near pick up address'
  app_state = client.ping(geodecoded_address)
  city = app_state.city
  vehicle_views = city.vehicle_views

  for key in city.vehicle_views_order:
    nearby_info = app_state.nearby_vehicles.get(key)
    view = vehicle_views[key]
    count = len(nearby_info.vehicle_paths)

    if count:
      additional_info = ''
      if view.surge:
        additional_info = 'Warning - x{multiplier} surge pricing is active!'.format(multiplier=view.surge.multiplier)

      print '{name} has {count} cars near by (eta {eta}). {additional_info}'.format(
        name=view.description,
        count=len(nearby_info.vehicle_paths),
        eta=nearby_info.eta_string,
        additional_info=additional_info
        )
    else:
      print '{name} has no vehicles nearby :('.format(name=view.description)


    
def do_pickup(address):
  #Set the pick up location for Uber
  results = geolocate(address)
  if not results:
    print 'address not found '
    return

  if len(results) == 1:
    geo_address = results[0]
  else:
    for i in xrange(len(results)):
      entry = results[i]
      print '{index}) {entry}'.format(
        index = i+1,
        entry = entry['formated_address']
      )
    print ''

    selection_num = int(raw_input('choose address# (0 to abort)> ') or 0)
    if not selection_num:
      return

    geo_address = results[selection_num - 1]

  print 'booking UberX for {}...'.format(geo_address['formatted_address'])
  book_uber_ride_now(geo_address)


def book_uber_ride_now(location):
  #books an Uber X
  global client
  abort_signal = []

  def handle_abort(*args):
    abort_signal.append(None)
    print ''
    print 'cancelling ride'
    client.cancel_pickup()
    print 'ride cancelled'
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit("Ride Cancelled: End Application") #quits the application

  signal.signal(signal.SIGINT, handle_abort)
  client.request_pickup(location)

  print_state = True
  last_status = None
  print 'waiting for ride (ctrl+c at any time to cancel ride) \n'

  while print_state and not abort_signal:
    state = client.ping(None)
    status = state.client.status
    if status != last_status:
      print 'status: '+ status
      last_status = status

    if status == ClientStatus.LOOKING:
      print state.client.last_request_note
      break

    if status == ClientStatus.WAITING_FOR_PICKUP:
      trip = state.trip
      vehicle = trip.vehicle
      sys.stdout.write("\r{driver} will pick you up in {eta} with a {color} {make} {model}.".format(
        driver=trip.driver.name,
        eta=trip.eta_string_short,
        color=vehicle.exterior_color,
        make=vehicle.vehicle_type.make,
        model=vehicle.vehicle_type.model,
      ))
      sys.stdout.flush()

    time.sleep(1)
  
      

def login_into_uber( username, password):
  #Logs into Uber
  try:
    global client
    token = UberClient.login(username, password)
    username = username

    if token:
      client = UberClient(username, token)
      if client:
        print "Logged into Uber as " + username+'\n'
        #checkout our pickup address
        do_checkout_address(uberPickUpAddress)
        #ping pickup address for nearby vehicles
        ping_address_for_available_vehicles(uberPickUpAddress)
        #order the uber to your location
        do_pickup(uberPickUpAddress)
      
  except UberException as e:
    print e.description
    
  


def AmazonDashButton4Uber(pkt):
  if pkt[ARP].op == 1: #who-has (request)
    if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
      if pkt[ARP].hwsrc == amazonDashButtonMacAddress: #order Uber Now
        print 'Connecting to Uber... \n'
        login_into_uber(uberUsername,uberPassword)
      else:
        print "ARP Probe from an unknown device: " + pkt[ARP].hwsrc

print sniff(prn=AmazonDashButton4Uber, filter="arp", store=0, count=10)

