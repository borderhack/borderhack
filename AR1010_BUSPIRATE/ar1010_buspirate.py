#!/usr/bin/env python
# encoding: utf-8
"""
Simple script to tune the AR1010 FM Radio Module 
using the Bus Pirate's I2C binmode
Created by Fell on 2010-12-10
Based on the i2c-test.py testscript from Peter Huewe
"""

import sys
from decimal import Decimal
from pyBusPirateLite.I2C import *


class AR1010(object):

  def __init__(self):
    #  Recommended initial values for the AR1010
    self.init_reg_vals =  [0xfffb, 0x5b15, 0xf4b9, 0x8012,
                            0x0400, 0x28aa, 0x4400, 0x1ee7,
                            0x7141, 0x007d, 0x82c6, 0x4f55,
                            0x970c, 0xb845, 0xfc2d, 0x8097,
                            0x04a1, 0xdf6a]
   
    # Set each of our registers with the recommended values
    for reg in range(len(self.init_reg_vals)):
      # grab first byte
      val1 = (self.init_reg_vals[reg] & 0xFF00) >> 8
      # grab second byte
      val2 = (self.init_reg_vals[reg] & 0x00FF)
      # Write the values to our register
      print "Writing initial values to register %d" % reg
      self.write([0x20, reg, val1, val2])
      print "OK."

  def write(self, data):
    """ Writes to a AR1010 register using I2C """
    i2c.send_start_bit()
    i2c.bulk_trans(len(data), data)
    i2c.send_stop_bit()

  def tune(self, frequency):
    """ Tunes the AR1010 to a given frequency """
    # Algorithm to derive channel
    # given in the AR1010 Programmer's Guide
    chan = int((Decimal(freq)*10)-690)

    # Set value we will write to tuning register and clear tune bit
    tune_vals = ((chan | 0xd000) & ~(1<<9))
    # Seperate tune_vals to 1 byte values
    val1 = (tune_vals & 0xFF00) >> 8
    val2 = (tune_vals & 0x00FF)
    # Write tuning values to register 2
    print "Tuning to station..."
    self.write([0x20, 2, val1, val2])
    # Turn tune bit on and write our tuning value to register 2 again
    val1 = (tune_vals | (1<<9)) >> 8
    self.write([0x20, 2, val1, val2])
    print "OK."


if __name__ == '__main__':
 
  i2c = I2C("/dev/ttyUSB0", 115200)

  print "Entering binmode: "
  if i2c.BBmode():
    print "OK."
  else:
    print "failed. Resetting Bus Pirate"
    # reset Bus Pirate
    i2c.resetBP()
    sys.exit()

  print "Entering raw I2C mode: "
  if i2c.enter_I2C():
    print "OK."
  else:
    print "failed. Resetting Bus Pirate"
    i2c.resetBP()
    sys.exit()

  print "Configuring I2C."
  if not i2c.cfg_pins(I2CPins.POWER):
    print "Failed to set I2C peripherals. Resetting Bus Pirate..."
    i2c.resetBP()
    sys.exit()
  if not i2c.set_speed(I2CSpeed._100KHZ):
    print "Failed to set I2C speed. Resetting Bus Pirate..."
    i2c.resetBP()
    sys.exit()
  i2c.timeout(0.2)

  ar1010 = AR1010()
  while (1):
    freq = raw_input('Enter radio frequency(x to exit): ')
    if (freq == 'x'):
      rst = raw_input('Reset Bus Pirate?(Y/n')
      if (rst != 'n'):
        i2c.resetBP()
        sys.exit()
      sys.exit()
    else:
      try:
          ar1010.tune(freq)
      except:
          print "Error tuning AR1010! Resetting Bus Pirate..."
          i2c.resetBP()
          sys.exit()
