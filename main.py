import machine
import random
import array
import utime
import sys
import os

sys.path.append('./pkg/color')
print(sys.path)

from time import sleep

#from color import *
#print("test colors", atRandom())

# a random color 0 -> 255
def random_color():
    return random.randint(0, 255)

def reverseBits(n, no_of_bits):
    result = 0
    for i in range(no_of_bits):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result

spi_sck=machine.Pin(2)
spi_tx=machine.Pin(3)
spi_rx=machine.Pin(4)

spi=machine.SPI(0,baudrate=100000, sck=spi_sck, mosi=spi_tx, miso=spi_rx)

NUM_LEDS = 144
#value from 0 to 31
BRIGHTNESS = 0.04
sleeptime = 0.3
brightnessIncrement = 0.03225806
brightnessMin = 0.03225806
brightnessMax = 1
customBrightnessMax = 0.2
defaultDimmer = 0.1
defaultBrightnessMax = 1


START_HEADER_SIZE = 4
LED_START = 0b11100000  # Three "1" bits, followed by 5 brightness bits

RGB = (0, 1, 2)
RBG = (0, 2, 1)
GRB = (1, 0, 2)
GBR = (1, 2, 0)
BRG = (2, 0, 1)
BGR = (2, 1, 0)

pixel_order=BGR

#defaultColor = (247, 98, 5)
defaultColor = (250, 243, 55)

# Supply one extra clock cycle for each two pixels in the strip.
end_header_size = NUM_LEDS // 16
if NUM_LEDS % 16 != 0:
    end_header_size += 1
_buf = bytearray(NUM_LEDS * 4 + START_HEADER_SIZE + end_header_size)
end_header_index = len(_buf) - end_header_size
pixel_order = pixel_order
# Four empty bytes to start.
for i in range(START_HEADER_SIZE):
    _buf[i] = 0x00
# Mark the beginnings of each pixel.
for i in range(START_HEADER_SIZE, end_header_index, 4):
    _buf[i] = 0xff
# 0xff bytes at the end.
for i in range(end_header_index, len(_buf)):
    _buf[i] = 0xff

def randomVelocity(stoppedAllowed=False):
    min = 0

    if not stoppedAllowed:
        min = 1

    velocity = random.randint(min, 4)
    direction = random.random()
    print(" +++++", direction)

    if direction < 0.5:
        velocity *= -1

    return velocity

# return an integer between 0 and 31
#  -  0 being "off"
#  - 31 being "max"
def randomBrightness(allowOff, maxBrightness=defaultBrightnessMax):
    min = 1
    if allowOff:
        min = 0
    
    brightnessRatio = random.randint(min, 31)
    value = int(brightnessRatio * 31)

    if maxBrightness > 0 and value > maxBrightness:
        value = maxBrightness
        value = 15
    
    if value < min:
        value = min

    return value

def pixelOffByte():
    return 32 & 0b00011111

def pixelBrightnessByte(brightness):
    # LED startframe is three "1" bits, followed by 5 brightness bits
    # then 8 bits for each of R, G, and B. The order of those 3 are configurable and
    # vary based on hardware
    # same as math.ceil(brightness * 31) & 0b00011111
    # Idea from https://www.codeproject.com/Tips/700780/Fast-floor-ceiling-functions
    v = brightness & 0b00011111
    return v

def randomColor():
    return (random_color(), random_color(), random_color())

def resetStrip():
    for i in range(0, NUM_LEDS):
        setPixel(i, (0,0,0), 0)

def setPixel(i, rgb, brightness):
    offset = i * 4 + START_HEADER_SIZE
    brightness_byte = pixelBrightnessByte(brightness)

    _buf[offset] = brightness_byte | LED_START
    _buf[offset + 1] = rgb[pixel_order[0]]
    _buf[offset + 2] = rgb[pixel_order[1]]
    _buf[offset + 3] = rgb[pixel_order[2]]

class RGB:
  def __init__(self, red, green, blue):
    self.red = red
    self.green = green
    self.blue = blue

  def __str__(self):
    return f"({self.red}, {self.green}, {self.blue})"

class Pixel:
  def __init__(self, color, brightness):
    self.color = color
    self.brightness = brightness

  def __str__(self):
    return f"{self.color}, {self.brightness}"
  
  def setBrightness(self, brightness):
      self.brightness = brightness

class Wagon:
  def __init__(self, position, trainPixel, pixel, colorfull=0):
    self.position = position
    self.trainPixel = trainPixel
    self.pixel = pixel
    self.colorfull = colorfull

  def color(self):
    if self.colorfull == 0:
        return defaultColor
    
    if self.colorfull == 1:
        return self.trainPixel.color
    
    if self.colorfull == 2:
        return self.pixel.color
    
    return randomColor()

  def brightness(self):
    if self.colorfull == 0:
        return BRIGHTNESS
    
    if self.colorfull == 1:
        return self.trainPixel.brightness
    
    if self.colorfull == 2:
        return self.pixel.brightness
    
    return randomBrightness(False)

  def __str__(self):
    return f"  {self.position} => {self.pixel}"

class Train:
  def __init__(self, id, length=random.randint(1,8), velocity=randomVelocity(), position=random.randint(0,NUM_LEDS), colorfull=random.randint(0,3)):
    self.id = id
    self.length = length
    # velocity may be positive, negative or 0
    self.velocity = velocity
    self.position = position
    self.colorfull = colorfull
    self.pixel = Pixel(randomColor(), randomBrightness(False))

    self.wagons = [ Wagon(i, self.pixel, Pixel(randomColor(), randomBrightness(False)), colorfull) for i in range(length)]

  def __str__(self):
    wagons = ""
    for wagon in self.wagons:
        wagons += "\n     +" + str(wagon)
    return f"length: {self.length}, velocity: {self.velocity}, position: {self.position}, color: {self.colorfull}{wagons}"



##################################
##################################
##################################

def setUniformColor(rgb=defaultColor, ran=False):
    brightness = 1.0

    if ran:
        rgb = randomColor()
        brightness = randomBrightness(False)
    
    for i in range(0, NUM_LEDS):
        setPixel(i, rgb, defaultBrightnessMax)

def setRandomColors():
    for i in range(0, NUM_LEDS):
        rgb = randomColor()
        brightness = randomBrightness(True)
        setPixel(i, rgb, brightness)
    show()


trainCount = random.randint(1, 5)

trains = [ Train(
    i,
    random.randint(1, 8),
    randomVelocity(),
    random.randint(0,NUM_LEDS),
    random.randint(0,3)
) for i in range(trainCount)]
print("train count", trainCount)
for train in trains:
    print("-", train)


def rollPixelTrainFrame(circle):
    resetStrip()
    
    for train in trains:
        overLimit = False
        for wagon in train.wagons:
            pixelPosition = train.position + wagon.position
            oldpixelpos = pixelPosition

            if circle:
                if train.velocity > 0:
                    if pixelPosition >= NUM_LEDS:
                        pixelPosition = pixelPosition - NUM_LEDS
                elif train.velocity < 0:
                    oldPos = pixelPosition
                    if pixelPosition >= NUM_LEDS:
                        pixelPosition = pixelPosition - NUM_LEDS
                    elif pixelPosition < 0:
                        pixelPosition = NUM_LEDS + pixelPosition
                        if not overLimit:
                            print("----------")
                        overLimit = True
                        print("  train", train.id, train.length, train.velocity, " =>", wagon.position, ", oldpos:", oldPos, "newpos", pixelPosition)
            else:
                if pixelPosition >= NUM_LEDS:
                    break
                if pixelPosition < 0:
                    continue
            
            if pixelPosition > 143:
                print("--- pixel out of range -------")
                print("  train", train.id, train.length, train.velocity, train.position, " =>", wagon.position, ", oldpos:", oldpixelpos, "newpos", pixelPosition)
            
            setPixel(pixelPosition, wagon.color(), defaultBrightnessMax)
        
        oldpos = train.position
        train.position += train.velocity
        newpos = train.position


        if train.position > NUM_LEDS and circle:
            train.position = 0
        elif train.position > NUM_LEDS:
            train.position = 0 - train.length
        elif train.position < 0:
            train.position = NUM_LEDS + train.position
        
        if overLimit:
            print("---")
            print("  train", train.id, train.length, train.velocity, " => oldpos:", oldpos, "newpos", newpos, "aftrer", train.position)

        


def show():
    spi.write(_buf)

#                        (452)     (390)
# for "min" => max  1280 avg   828 min   432
#                        (108)     (548)
# for "max" => max 65535 avg 65427 min 64879
#
# step 2114
analog_value = machine.ADC(28)
dimmerStep = int(65535/31)
dimmerVariance = 600
lastBrightnessValue = 0
lastReadedValue = 0
lastReadedValueMax = 0
lastReadedValueMin = 0

def updateDimmer():
    global lastBrightnessValue
    global lastReadedValue
    global lastReadedValueMax
    global lastReadedValueMin

    reading = analog_value.read_u16()     
    value = int(reading/dimmerStep)

    if value != lastBrightnessValue and (reading > lastReadedValueMax or reading < lastReadedValueMin):
        print("ADC: ",reading)
        print("dimmerStep: ",dimmerStep)
        lastReadedValue = reading
        lastReadedValueMax = reading + dimmerVariance
        lastReadedValueMin = reading - dimmerVariance
        lastBrightnessValue = value
        print("dimmer", value)

    return value



print("###########################")

while True:
    defaultBrightnessMax = updateDimmer()
    
    #rollPixelTrainFrame(True)
    setUniformColor()

    show()


# counter = 0
# while True:
#     flip = counter % 2

#     if flip == 0:
#         setRandomColors()
#     else:
#         setUniformColor(defaultColor, True)
#     counter += 1

#     sleep(sleeptime)

# brightness = brightnessMin
# resetStrip()
# show()
# for i in range(0, NUM_LEDS):
#     active = i % 4

#     if active == 0:
#         #setPixel(i, defaultColor, 31)
#         if brightness > brightnessMax:
#             setPixel(i, (0,0,0), 0)
#             #print(i, "off")
#             break
#         else:
#             setPixel(i, defaultColor, brightness)
#             # brightness_byte = brightness & 0b00011111
#             print(i, "brightness", brightness, "=>", 32 - int(32 - brightness * 31))

#             # offset = i * 4 + START_HEADER_SIZE
#             # _buf[offset] = brightness_byte
#             # _buf[offset + 1] = defaultColor[pixel_order[0]]
#             # _buf[offset + 2] = defaultColor[pixel_order[1]]
#             # _buf[offset + 3] = defaultColor[pixel_order[2]]
#         brightness += brightnessIncrement
#     else:
#         setPixel(i, (0,0,0), 0)
#         #print(i, "off")
        
# show()
# sleep(30)
# resetStrip()
# show()



# resetStrip()
# show()

# print("#########################")
# print("#########################")
# loops = 10000
# results = [ [0.0]*2 for i in range(32)]
# #print(results)

# for i in range(0, loops):
#     brightness = randomBrightness(False)
#     result = 32 - int(32 - brightness * 31)
   
#     # store count
#     results[result][0] += 1
#     results[result][1] = brightness
#     #print(i, "brightness", brightness, "=>", result, "=>", results[result][0], ", ", results[result][1])
#     #sleep(0.001)

# print("------")
# #print(results)
# for i in range(0, 32):
#     print(i, "=>", results[i][0], ", ", results[i][1])
