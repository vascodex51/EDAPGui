# 6/24/2024 Update
 - Stumpii: Added undocking if necessary to start of supercruise assist.
 - Stumpii: Removed speed demands from the nav alignment code. Nav align should just do the alignment, the calling function determine what to do if alignment is successful or not. All but one of the calling routines sets the speed after calling the routine anyway.
 - Stumpii: sc_assist no longer spams 50% speed every iteration of its loop. So pilot is free to control the speed and just let AP do the alignment. Works great for manual 75% throttle at 0:07 from target and when using new SCO in SC.
 - Stumpii: sc_target_align now returns false if the target was found and now is lost and as no other cause was captured, then we went past the target.
 - Stumpii: While in SC, if we fly past the target, keep going for 5 secs, then slow to 50% and turn around using nav_align.

# 6/23/2024 Targetting update
- Stumpii provided change to Nav Offset to include Z axis where Z=+1 for target ahead and Z=-1 for target behind. Use the data to navigate to the target quicker when the target is behind us (pitch up or down depending if target is above/below us).

# 8/6/23 latest mss library causing crash
- if you are seeing:  AttributeError: '_thread._local' object has no attribute 'srcdc'   then you need to downgrade the mss library.  Updated the requirements.txt file accordingly
- pip install mss==8.0.3

# 6/25/2023 Update by EpicStuff
- Made it so that the state of Enable_CV_View is saved to configs/AP.json and loads previously loaded ship config on start.
also autoformatting (removed trailing whitespaces)

# 12/7/2022 Update
- Update to support ED 4.0 menu layout, so this AP works with both Odyssey and Horizon 4.0
- Waypoint processing, after adding System name in Galaxy Map had to add a Mouse click center screen so that keybindings would work when selecting Plot Route icon
- Robigo had to add a setSpeed50 after coming out of FSD in Sothis.  Still some issues with some users where the Robigo loop cannot find Siruis Atmos in the left menu
- No EDAPGui.exe in this update, if there is a demand for it then will make a formal released version

# 05/30/2022 Update
- V1.1.0 Release which includes EDAPGui.exe.  With the binary, one does not need to install all the python packages

# 05/17/2022 Update
- Added hotkey for starting Robigo as defined in config/AP.json file ("HotKey_StartRobigo": "pgup"). Added ability to only do single loop of Robigo run where user will complete and select missions (see config/AP.json "Robigo_Single_Loop": false)
- With single loop set to True, the Robigo Assist will work in Horizons.
  - CMDR would complete and select Missions, set Route to SOTHIS on GalaxyMap and then start the Robigo AP, which will undock, execute the loop and redock and terminate
  - Additional keybindings are required, see autopilot.log for missing keybindings (such as SelectTarget, Supercruise)

# 05/12/2022 Update
- Added a statemachine to Robigo Mines loop.  Will now determine where your ship is at in the loop and start from there.
  You can then stop the Robigo Assist to handle a Interiction and simply restart it to continue with the loop (it will 
  pick up where you left off).  No need to start at Robigo Mines.  See docs/Robigo.md for details

# 05/11/2022 Update
- For Waypoints, the completed state is now updated directly in the wp list.  New option to reset the waypoint completion state via button on the GUI.  The idea is to allow picking up where you left off in your waypoint list.  Also, the loading of a waypoint list has been separated from the activation of the waypoint assist.  (DopeEx is fine tuning the Waypoint system)

# 05/09/2022 Update
- Added the Robigo Mines Passenger Mission autopilot.   See docs/Robigo.md for further details

# 05/07/2022 Update
- Major Gui usability improvements
- Add bookmark as station destination option for waypoints
- If not close enough to the station during the first dock attempt, then another short throttle and reattempt docking request
- Fix missing waypoint assist in ap modes
- Add a new version check and discord and changelog links
- This effort brought to you buy DopeEx

# 05/06/2022 Update - Baselined codebase V1.0

# 05/02/2022 Update - thanks CMDRs for providing these updates
- Fix EDkeys.py to null key modifier if using Secondary binding used (see issue #2)
- Fix AP state to account for undocking from Outposts as opposed to Stations

# 04/28/2022 Update
The goal is to show in the overlay all the info that is needed without having to see the gui or have tts enabled.
The following things have been adjusted:
-	ap mode shows the mode in which the ap is currently running
-	ap status shows the same info as the statusline in the gui (align, maneuver, jump etc.)
-	ship status shows continuously the ship status (before partly in ap mode if no ap mode was active)
-	elw scanner shows if an elw was found

Also, the overlay was sometimes very hard to read, so the default font was changed and the option to change the font itself was added in the config.


# 03/07/2022 Update
- Minor update to the ELW image template to help with accuracy of detection
- Updated the AP.json file and added SunBrightThreshold (set to 125) use to detect Sun in front of ship when jumping into a system
- Updated the code to use the SunBrightThreshold configuration item

# 2/26/2022 Update
- Modified Sun low limit threshold to account for star density when close to core of galaxy
- Enlarged region that looks for Sun in support of sun avoidance
- Fixed jump count total on last jump
- Timing tweaks to account for accasional heating around Sun

# 2/24/2022 Update
- Update to Sun avoidance.  The Sun avoidance looks for brightness at the center of the display to go below 5% to know have pitched
  up sufficiently to go over the Sun.  If close to the core of the galaxy, the star density is high and thus the overall brightness
  of the center of the screen is higher so the ship may continue to pitch further up. Adjusted the brightness criteria to account for this.
  Also, if jumping into a non scoopable star, adjusted the brightness threshold to ensure pitching up/over the Sun works.

# 2/23/2022 Update
- Fixed sun avoidance for dark red/non-scoopable stars, will pitch up properly
- Use different screen grab package (mss) which is about 10x faster than ImageGrab.  New requirements.txt file.
  Must perform:  pip install mss
- The disengage popup "PRESS [J] TO DISENGAGE" image now only looks for "TO DISENGAGE" so user can have any key binding
  they want for that function
- Restructure folder.  Subdirectories now includes:  ships/  configs/  and waypoints/ 
- Fix issue when Saved Games has been moved out of C:
- Add more useful error for unrecognised key
- Add colour to debug images
- Allow for calibrating of larger screens
- Added Journal trap for interdiction, as well image matching from screen
- Waypoint, fixed undocking from Station


# 2/20/2022 Update
## HOWTO's added:
  - HOWTO-Calibration.md
  - HOWTO-RollPitchYaw.md
  - HOWTO-Waypoint.md

## Configurable Settings
  config-AP.json
    - Aded EnableRandomness flag to adjust sleep times
    - OverlayTextEnable flag to show overlay on ED, prototype
    - OverlayTextYOffset the Y location to put overlay (X hardcoded)
    - OverlayTextFontSize allows you to specify size
    - FuelScoopTimeOut how long to wait in fuel scooping before aborting
    - and others

## Autopilot
  - Added Waypoint Assist  (works both in Odyssey and Horisons)
    - Jumps to Systems defined in waypoints.json (or user selected) file
      - Can dock with a station that is defined in the file also (requires X, Y of mouse to select the 
        station from the System Map, this too is a little more complex so see separate HowTo)
        - Added GUI Button "Get X, Y Mouse" to help with determining the StationCoord 
      - Once docked can perform trades (somewhat complex to setup, will need separate HowTo), Sells first
        then Buys
      - Auto undock to take you to next waypoint system
      - If last line in the waypoint file is "REPEAT", it will loop to top and do it again, forever, otherwise
        Waypoint assist terminates at the end
  - GUI, in statusline, how shows: Distance Jumped, Jumps/Total Jumps, #Refuels, Sec/Jump
  - GUI, added text field for SunPitchUP+Time (in seconds) which adds this number of seconds after 
    sun avoidance to continue pitching up.  If your ship heats up easy (like my Cutter), then you will want
    to add a second or two to be pitch away from the Sun
  - While in SC, check for being interdicted, if so take action (submit, booster away), [initial approach]
  - Optimized number of seconds per jump.   Average just under 60 sec/jump, with fuel scooping once in a while at 70 s/j
  - Added Target Occlusion detection.  As you approach the Station it might suddenly show that
    it is behind the Planet.  This will now be detected and repositioning will occurs to go 
    around the planet
  - Tuned color ranges for masking the region for better image template matching.  If using anything other
    than default ED HUD color scheme, this AP will not work at all
  - Handled non FGB FOAM star avoidance when jumping into those Systems (for dim red suns), 
    so now won't crashed into those
  - Added journal catch to check if game odyssey, capture distance jumped, jumps remaining
  - Added Galaxy and System Map Open for key binding lookup
  - Added total light years traveled for FSD Route Assist and Waypoint Assit
  - Ship configurations provided that contain the values Roll, Pitch, and Yaw for various type ships
    (Only DBX, APSX, Cutter, and Sidewinder tested)

## Update requirements.txt file
  - One new packages is required to be installed, pynput==1.7.6, to support mouse click




