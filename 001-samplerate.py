#!/usr/bin/python3
# <xbar.title>CoreAudio Samplerate Display</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Anthony Lauzon</xbar.author>
# <xbar.author.github>anthonylauzon</xbar.author.github>
# <xbar.desc>Displays current samplerate for an audio device.</xbar.desc>
# <xbar.dependencies>bash</xbar.dependencies>
# <xbar.abouturl></xbar.abouturl>

import json
import os

gFileName = "/Users/mmora/audiodevice.txt"

itemsWalked = 0
indentCount = 0
logOutput = False
gInUSBDeviceNode = False
incAmt = 0
hasidProductNameString = False
hasidVendorNameString = False
hasIOAudioEngineGlobalUniqueID = False
hasAudioClassNum = False
hasIOAudioDeviceName = False
gInUSBDeviceNode = False
gInIOAudioDevice = False
gInIOAudioEngine = False
AMSCommand = '| param1="/System/Applications/Utilities/Audio\ MIDI\ Setup.app" '

def printFoundItem(in_item,in_str):
    print(f'{in_item}: {in_str}')
# ----------------------------------------------------------------------------------------------------------------
# function for looking for our USB Audio components and properties
# ----------------------------------------------------------------------------------------------------------------

def findOurComponents(item, key, node):
    global hasidProductNameString
    global hasidVendorNameString
    global hasIOAudioEngineGlobalUniqueID
    global hasAudioClassNum
    global hasIOAudioDeviceName
    global gInUSBDeviceNode
    global gInIOAudioDevice
    global gInIOAudioEngine

    if '_name' in key:  # logic is wrong here. It should look for a key that is only in a USB audio device node then iterate finding values.
        keyContents = item

        for usb_items, usb_value in node.items():
            if isinstance(usb_value, bytes):
                value_str = usb_value.decode('latin-1')
            else:
                value_str = str(usb_value)

            if '_name' == usb_items:

                if value_str != "coreaudio_device":
                    print("---")
                    value_str += "| shell=open " + AMSCommand

                    printFoundItem('Name', value_str )
                continue
                
            if '_properties' == usb_items:
                if value_str == "coreaudio_default_audio_system_device":
                    printFoundItem(":bell: Default System Alert Device", "Yes")
                else:
                    printFoundItem("Properties", value_str)

                continue
            if 'coreaudio_input_source' == usb_items:
                if value_str == "spaudio_default":
                    value_str = "Default"
                printFoundItem("Input Source", value_str)
                continue
            if 'coreaudio_output_source' == usb_items:
                if value_str == "spaudio_default":
                    value_str = "Default"
                printFoundItem("Output Source", value_str)
                continue
            if 'coreaudio_device_transport' == usb_items:
                tmpStr = ""
                if value_str == "coreaudio_device_type_AVB":
                    tmpStr = "AVB"
                if value_str == "coreaudio_device_type_firewire":
                    tmpStr = "Firewire"
                if value_str == "coreaudio_device_type_usb":
                    tmpStr = "USB"
                if value_str == "coreaudio_device_type_displayport":
                    tmpStr = "DisplayPort"
                if value_str == "coreaudio_device_type_builtin":
                    tmpStr = "Built-in"

                printFoundItem("Transport", tmpStr)

                continue
            if 'coreaudio_default_audio_output_device' == usb_items:

                if value_str == "spaudio_yes":
                    printFoundItem(":speaker: Default Output Device", "Yes")

                continue
            if 'coreaudio_default_audio_input_device' == usb_items:

                if value_str == "spaudio_yes":
                    printFoundItem(":microphone: Default Input Device", "Yes")

                continue
            if 'coreaudio_default_audio_system_device' == usb_items:
                if value_str == "spaudio_yes":
                    printFoundItem("Default System Output Device", "Yes")
                continue
            if 'coreaudio_device_manufacturer' == usb_items:
                printFoundItem("Manufacturer", value_str)

                continue
            if 'coreaudio_device_srate' == usb_items:
                printFoundItem("Current Sample Rate", value_str)
                continue
            if 'coreaudio_device_output' == usb_items:
                printFoundItem("Output Channels", value_str)
                continue
            if 'coreaudio_device_input' == usb_items:
                printFoundItem("Input Channels", value_str)
                continue

    return

# ----------------------------------------------------------------------------------------------------------------
# function for walking the plist and looking for USB audio
# components in a ioreg dump in plist format
# ----------------------------------------------------------------------------------------------------------------
def walk(node):
    global itemsWalked
    global indentCount
    global logOutput
    global gInUSBDeviceNode
    global incAmt

    try:
        pad = ' '

        indentCount += incAmt
        for key, item in node.items():
            # print(indentCount * pad + '%s :' % key) if logOutput else None
            keyStr = indentCount * pad + '%s' % key
            if isinstance(item, dict):
                print('%s {' % keyStr) if logOutput else None
                walk(item)
                print(indentCount * pad + '};') if logOutput else None
            if isinstance(item, list):
                printKeyStr = True
                for index, val in enumerate(item):
                    if isinstance(val, dict):
                        print('%s: {' % keyStr) if logOutput else None
                        walk(val)
                        print(indentCount * pad + '};') if logOutput else None

                    else:
                        if printKeyStr:
                            print('%s:' % keyStr) if logOutput else None
                            printKeyStr = False
                        if isinstance(val, bytes):
                            theLen = val.__len__()
                            if theLen < 9:
                                valStr = val.hex()
                                print(
                                    (indentCount + incAmt) * pad + '%d): 0x%s' % (index, valStr)) if logOutput else None
                            else:
                                if theLen > 64:
                                    valStr = val.hex()[0:63] + '…'
                                else:
                                    valStr = val.hex()

                                print((indentCount + incAmt) * pad + '%d): size = %d 0x%s' % (
                                index, theLen, valStr)) if logOutput else None
                        else:
                            print((indentCount + incAmt) * pad + '%d): %s' % (index, val)) if logOutput else None
            else:
                if isinstance(item, bytes):
                    theLen = item.__len__()
                    if theLen < 9:
                        itemStr = item.hex()
                        print(f'{keyStr}: 0x{itemStr}') if logOutput else None
                    else:
                        if theLen > 64:
                            itemStr = item.hex()[0:63] + '…'
                        else:
                            itemStr = item.hex()

                        print(f'{keyStr}: size = {theLen} [0x{itemStr}]') if logOutput else None
                else:
                    if not isinstance(item, dict):
                        print(f"{keyStr}: {item}") if logOutput else None

            # main function to check for our USB audio Components
            findOurComponents(item, key, node)

            itemsWalked += 1
    except UnboundLocalError:
        print(traceback.format_exc())
    except:
        print(traceback.format_exc())
        print('in Walk Oops!', sys.exc_info()[0], 'occurred.')
        print('exception in walk')
        pass
    if indentCount > 0:
        indentCount -= incAmt

    return

data = os.popen('/usr/sbin/system_profiler -json SPAudioDataType').read()
devices = json.loads(data)
#print(devices)
print(":microphone: :speaker:")
walk(devices)

# with open(gFileName) as f:
#     data = f.read()
#     devices = json.loads(data)
#     #print(devices)
# 
#     print(":microphone:")
# 
#     walk(devices)


