# ED Autopilot - Gui
This Elite Dangerous (ED) Autopilot supports FSD Route assistance, Supercruise Assistance, Waypoint Assist and AFK Combat escape assistance.  For the FSD Route Assist, you select
your destination in the GalaxyMap and then enable this assistant and it will perform all the jumps to get you to your destination, AFK.  Furthermore while
executing route assistance it will perform detailed system scanning (honk) when jumping into a system and optionally perform FSS scanning
to determine if Earth, Water, or Ammonia type world is present.  The supercruise (SC) assistant (and not using ED's SC Assist which takes up a slot, for a piece of software?) 
will keep you on target and when PRESS [J] DISENGAGED is presented will autodrop out of SC and perform autodocking with the targetted Station.  With Waypoint Assist you 
define the route in a file and this assistance will jump to those waypoints.  If a Station is defined to dock at, the assistant will transition to SC Assist and
dock with the station.  A early version of a trading capability is also included.  If Voice enabled, the autopilot will inform you of its actions.   

This autopilot uses Computer Vision (grabs screens and performs template matching) and issues keystrokes.  It does not perform any runtime modifications 
of Elite Dangerous, it is an external-ED construct (similar to us commanders) 

  ```
  * See HOWTO-Calibration.md for details on how to calibrate EDAPGui for your system if required 
  * See HOWTO-Waypoint.md for details on how to generate a waypoint file 
  * See HOWTO-RollPitchYaw.md for details on how to tune the Pitch, Roll, Yaw values 
  ```

Note: this autopilot is based on https://github.com/skai2/EDAutopilot , some of the routines were used and turned into classes and tweaks were done on sequences
 and how image matching was performed.   Kudo's to skai2mail@gmail.com
 
Also Note: This repository is provided for educational purposes as a in depth programming example of interacting with file based data, computer vision processing, user feedback via voice, win32 integration using python, threading interaction, and python classes.  

# Constraints:
* Will only work with Windows (not Linux)
* Default HUD Values must be used, if you changed those colors, this autopilot will not work
* Borderless Elite Dangerous (ED) configuration required,  Windowed does not work due to how the screen is grabbed
* Screen Resolution/scale X, Y:  The templates were captured on a 3440x1440 resolution/game configuration.  These need to be scaled
  for different resolutions.  The _config-resolution.json_ file captures these resolutions with the corresponding ScaleX, Y values.  If a resolution is not defined
  for your monitor the code will attempt to divide /3440  and /1440 to get the scale factor (not likely to be correct)
  ```
  * See Calibration.md for details on how to calibrate EDAPGui for your system *
  ```
  * Field of View (Graphics->Display) setting plays here.  I run about 10-15% on the slider scale.  If you have a large FOV then the 
    template images will likely be too large
* Focus: ED must have focus when running, so you can't do other things on other windows if AP is active.
           If you change focus, then keyboard events will be sent to the focused window, can mess with the 
           window
* Control Rates: Must provide the roll, pitch, yaw rates for your ship. See HOWTO-RollPitchYaw.md, start with values from Outfitting for your ship 
* Autodocking: For the AP to recongize the "PRESS [J] TO DISENGAGE"  you should map "J" key for disengage so that that image matching will work. Or at minimum have
  it mapped to a single Key and not a set of keys such as "PRESS [CTR+ALT+5] TO DISENGAGE", as that is unlikely to meet the matching threshold of the image.  The following should be the keybing to ensure this works

    <HyperSuperCombination>
      <Primary Device="Keyboard" Key="Key_J" />
      <Secondary Device="{NoDevice}" Key="" />		
    </HyperSuperCombination>

* Routing: If using Economical Route setting, then may run into problems in jumping.  With Economical, the Stars may not be on the "other-side" of the 
  Sun as with Fastest routing.
  As such, when rolling toward the Target, the Sun may fade the console making Compass matching difficult.  Need to think through this one more.  The Sun shining on the 
  console kills the matching.  You can see that if you enable CV View
* The Left Panel (Navigation) must be on the Navigation tab as the script assumes so.  It will be reset after a FSD jump back to Nav,
  but if in SC Assist, need to ensure it is configured there to support docking request
* Must install needed packages:  pip install -r requirements.txt
* "Advanced Autodocking" module must be outfitted on ship to support autodock 
* The ELW Scanner may have issues for you, the screen region (defined in Screen_Region.py) isolates the region to where Earth, Water, and Ammonia
  signal would be present.  If using different resolution from 3440x1440 then this region will need to be adjusted for your resolution for
  proper detection
* Must have required keybinding set for proper autopilot behavior.  See autopilot.log for any Warnings on missing key bindings
* See https://github.com/skai2/EDAutopilot for other constraints that probably apply

# How to run:
* With Elite Dangerous (ED) running, start EDAPGui.py
  * python EDAPgui.py     
  * Note: the default Roll, Pitch, and Yaw rates are for my Diamondback Explorer, you need to enter the values
    for your ship, which can be found in Outfitting. 
* In ED, Use Left Panel to select your route
* Go to supercruise and go ahead and line up with Target
* In the autopilot enable FSD Assist or hit the 'Home' key.  When a assist starts it will set focus
      to the Elite Dangerous window.  
Note: the autopilot.log file will capture any required keybindings that are not set
  
# Autopilot Options:
* FSD Route Assist: will execute your route.  At each jump the sequence will perform some fuel scooping, however, if 
    fuel level goes down below a threshold  the sequence will stop at the Star until refueling is complete.  
    If refueling doesn't complete after 35 seconds it will abort and continue to next route point.  If fuel goes below 
    10% (configurable), the route assist will terminate
* Supercruise Assist: will keep your ship pointed to target, you target can only be a station for
    the autodocking to work.  If a settlement is targetted or target is obscured you will end up being kicked out of SC 
    via "Dropped Too Close" or "Dropping from Orbital Cruise" (however, no damage to ship), throttle will be set to
    Zero and exit SC Assist.  Otherwise, when the 'PRESS [J] DISENGAGE' appears the SC Assist will drop you out of SC
    and attempt request docking (after traveling closer to the Station), if docking granted it will.    
    put throttle to zero and the autodocking computer will take over. Once docked it will auto-refuel and go into StarPort Services.
    Note: while in SC, a interdictor response is included.   Also, as approaching the station, if it shows the Station is occluded
    this assistant will navigate around the planet and proceed with docking
* Waypoint Assist: When selected, will prompt for the waypoint file.  The waypoint file contains System names that will be 
    entered into Galaxy Map and route plotted.  If the last entry in the waypoint file is "REPEAT", it will start from the beginning.
    If the waypoint file entry has an associated Station/StationCoord entry, the assistant will route a course to that station
    upon entering that system.  The assistant will then autodock, refuel and repair.  If a trading sequence is define, it will then
    execute that trade.  See HOWTO-Waypoint.md
* ELW Scanner: will perform FSS scans while FSD Assist is traveling between stars.  If the FSS
    shows a signal in the region of Earth, Water or Ammonia type worlds, it will announce that discovery
    and log it into elw.txt file.  Note: it does not do the FSS scan, you would need to terminate FSD Assist
    and manually perform the detailed FSS scan to get credit.  Or come back later to the elw.txt file
    and go to those systems to perform additional detailed scanning. The elw.txt file looks like:<br>
      _Oochoss BL-M d8-3  %(dot,sig):   0.39,   0.79 Ammonia date: 2022-01-22 11:17:51.338134<br>
       Slegi BG-E c28-2  %(dot,sig):   0.36,   0.75 Water date: 2022-01-22 11:55:30.714843<br>
       Slegi TM-L c24-4  %(dot,sig):   0.31,   0.85 Earth date: 2022-01-22 12:04:47.527793<br>_
* AFK Combat Assist: used with a AFK Combat ship in a Rez Zone.  It will detect if shields have
    dropped and if so, will boost away and go into supercruise for ~10sec... then drop, put pips to
    system and weapons and deploy fighter, then terminate.  While in the Rez Zone, if your fighter has
    been destroyed it will deploy another figher (assumes you have two bays)
* Calibrate: will iterate through a set of scaling values getting the best match for your system.  See HOWTO-Calibrate.md
* Cap Mouse X, Y:  this will provide the StationCoord value of the Station in the SystemMap.  Selecting this button
    and then clicking on the Station in the SystemMap will return the x,y value that can be pasted in the waypoints file
* SunPitchUp+Time field are for ship that tend to overheat. Providing 1-2 more seconds of Pitch up when avoiding the Sun
    will overcome this problem.  This will be Ship unique and this value will be saved along with the Roll, Pitch, Yaw values 
* Menu
  * Open : read in a file with roll, pitch, yaw values for ship
  * Save : save the roll,pitch,yaw, and sunpitchup time values to a files
  * Enable Voice : Turns on/off voice
  * Enable CV View: Turn on/off debug images showing the image matching as it happens.  The numbers displayed
    indicate the % matched with the criteria for matching. Example:  0.55 > 0.5  means 55% match and the criteria
    is that it has to be > 50%, so in this case the match is true
    
## Hot Keys:
* Home - Start FSD Assist
* Ins  - Start SC Assist
* End  - Terminate any running assistants

Hot keys are now configurable in the config-AP.json file, so you can remap them. Be sure not to use any keys you have mapped in ED.  You can find the key names here:
https://pythonhosted.org/pynput/keyboard.html

## Config File: config-AP.json
  Note: the below is from the code, the real .json file will have the True/False values as lower case, as in true/false
        self.config = {  
            "DSSButton": "Primary",        # if anything other than "Primary", it will use the Secondary Fire button for DSS
            "JumpTries": 3,                # 
            "NavAlignTries": 3,            #
            "RefuelThreshold": 65,         # if fuel level get below this level, it will attempt refuel
            "FuelThreasholdAbortAP": 10,   # level at which AP will terminate, because we are not scooping well
            "WaitForAutoDockTimer": 120,   # After docking granted, wait this amount of time for us to get docked with autodocking
            "FuelScoopTimeOut": 35,       # number of second to wait for full tank, might mean we are not scooping well or got a small scooper
            "HotKey_StartFSD": "home",     # if going to use other keys, need to look at the python keyboard package
            "HotKey_StartSC": "ins",       # to determine other keynames, make sure these keys are not used in ED bindings
            "HotKey_StopAllAssists": "end",
            "EnableRandomness": False,     # add some additional random sleep times to avoid AP detection (0-3sec at specific locations)
            "OverlayTextEnable": False,    # Experimental at this stage
            "OverlayTextYOffset": 400,     # offset down the screen to start place overlay text
            "OverlayTextFontSize": 16, 
            "OverlayGraphicEnable": False, # not implemented yet
            "DiscordWebhook": False,       # discord not implemented yet
            "DiscordWebhookURL": "",
            "DiscordUserID": "",
            "VoiceID": 1,                  # my Windows only have 3 defined (0-2)
            "LogDEBUG": False,             # enable for debug messages
            "LogINFO": True
        }

## Setup:
_Requires **python 3** and **git**_
1. Clone this repository
```sh
> git clone https://github.com/sumzer0-git/EDAPGui
```
2. Install requirements
```sh
> cd EDAPGui
> pip install -r requirements.txt
```
3. Run script
```sh
> python EDAPGui.py
OR you may have to run
> python3 EDAPGui.py
if you have both python 2 and 3 installed.
```

If you encounter any issues during pip install, try running:
> python -m pip install -r requirements.txt
instead of > pip install -r requirements.txt


## Known Limitations
 * If you jump into a system with 2 suns next to each other, will likely over heat and drop from Supercruise.
 * Have seen a few cases where after doing refueling, depending on ship acceleration, we don't get away from Sun far enough before engaging FSD
   and can over heat
                                                               
## Elite Dangerous, Role Play and Autopilot
* I am a CMDR in the Elite Dangerous universe and I have a trusty Diamondback Explorer
* In my travels out into the black I have become frustrated with my flight computers abilities.  I don't want to stay
  up hours and hours manually performing Sun avoidance just to jump to the next system.  
* In a nutshell, Lakon Spaceways lacks vision.  Heck, they provide Autopilot for docking, undocking, and Supercruise but can't provide
  a simple route AP?   Geezzz
* Well, I have my trusty personal quantum-based computing device (roughly 10TeraHz CPU, 15 Petabyte RAM), which is the size of a credit-card, that has vision processing capability, has ability to inteface with my Diamondback Explorer Flight Computer 
  so I'm going to develop my own autopilot.   This falls under the "consumers right to enhance", signed into law in the year 3301 and ratified by all the Galatic powers
* So CMDRs, lets enhance our ships so we can get some sleep and do real work as opposed to hours of maneuvering around Suns

## WARNING:

Use at your own risk.  Have performed over 2000 FSD jumps with this autopilot and have aborted the FSD Assist
about 6 times due to jumping into a system that had 2 suns next to each other and pretty much the ship overheated
and dropped out of supercruise.   The ship did not get destroyed but had to use a heat sink to get out of the
situation

# Email Contact

sumzer0@yahoo.com


# Screen Shot
![Alt text](screen/screen_cap.png?raw=true "Screen")
                                                               
* Video of FSD Route Assist going between systems: https://www.youtube.com/watch?v=Ym90oVhwVzc
  
* Video where selected a Station as the target, then FSD Route Assist jumping into that System and auto-transitioning into SC Assist to the station. Perform target align with the Station (so it won't drift). Then detecting SC Disengage and doing the disengage SC, and requesting autodock.  Once docked, refuels and goes into the StarPort Services, then termiates SC Assist:
https://youtu.be/PtBYxWYX0so
