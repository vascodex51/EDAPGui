from __future__ import annotations
import json
import os
from copy import copy

from MarketParser import MarketParser
from StatusParser import StatusParser
from time import sleep
from EDlogger import logger
from Screen_Regions import Quad, scale_region

"""
File:StationServicesInShip.py    

Description:
  TBD 

Author: Stumpii
"""


class EDStationServicesInShip:
    """ Handles Station Services In Ship. """
    def __init__(self, ed_ap, screen, keys, cb):
        self.ap = ed_ap
        self.ocr = ed_ap.ocr
        self.locale = self.ap.locale
        self.screen = screen
        self.keys = keys
        self.ap_ckb = cb
        self.passenger_lounge = PassengerLounge(self, self.ap, self.ocr, self.keys, self.screen, self.ap_ckb)
        self.commodities_market = CommoditiesMarket(self, self.ap, self.ocr, self.keys, self.screen, self.ap_ckb)
        self.status_parser = StatusParser()
        self.market_parser = MarketParser()
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        self.reg = {'commodities_market': {'rect': [0.0, 0.0, 0.25, 0.25]},
                    'station_services': {'rect': [0.10, 0.10, 0.90, 0.85]},
                    'connected_to': {'rect': [0.0, 0.0, 0.25, 0.1]},
                    'market_header': {'rect': [0.0, 0.0, 0.25, 0.1]}}
        self.sub_reg = {'connected_to': {'rect': [0.0, 0.0, 0.25, 0.1]},
                        'market_header': {'rect': [0.0, 0.0, 0.25, 0.1]}}

        self.load_calibrated_regions()

    def load_calibrated_regions(self):
        calibration_file = 'configs/ocr_calibration.json'
        if os.path.exists(calibration_file):
            with open(calibration_file, 'r') as f:
                calibrated_regions = json.load(f)

            for key, value in self.reg.items():
                calibrated_key = f"EDStationServicesInShip.{key}"
                if calibrated_key in calibrated_regions:
                    self.reg[key]['rect'] = calibrated_regions[calibrated_key]['rect']

            # Scale the regions based on the sub-region.
            self.reg['connected_to']['rect'] = scale_region(self.reg['station_services']['rect'],
                                                            self.sub_reg['connected_to']['rect'])
            self.reg['market_header']['rect'] = scale_region(self.reg['commodities_market']['rect'],
                                                             self.sub_reg['market_header']['rect'])

    def goto_station_services(self) -> bool:
        """ Goto Station Services. """
        # Go to cockpit view
        self.ap.ship_control.goto_cockpit_view()

        self.keys.send("UI_Up", repeat=3)  # go to very top (refuel line)
        self.keys.send("UI_Down")  # station services
        self.keys.send("UI_Select")  # station services

        if self.ap.debug_overlay:
            stn_svcs = Quad.from_rect(self.reg['station_services']['rect'])
            self.ap.overlay.overlay_quad_pct('stn_svcs', stn_svcs, (0, 255, 0), 2, 5)
            self.ap.overlay.overlay_paint()

        # Wait for screen to appear
        res = self.ocr.wait_for_text(self.ap, [self.locale["STN_SVCS_CONNECTED_TO"]], self.reg['connected_to'])

        # Store image
        # image = self.screen.get_screen_rect_pct(scl_reg['rect'])
        # cv2.imwrite(f'test/station-services/station-services.png', image)

        # Return OCR result.
        return res

    def goto_construction_services(self) -> bool:
        """ Goto Construction Services. This is for an Orbital Construction Site. """
        # Go to cockpit view
        self.ap.ship_control.goto_cockpit_view()

        self.keys.send("UI_Up", repeat=3)  # go to very top (refuel line)
        self.keys.send("UI_Down")  # station services
        self.keys.send("UI_Select")  # station services

        # TODO - replace with OCR from OCR branch?
        sleep(3)  # wait for new menu to finish rendering

        return True

    def determine_commodities_location(self) -> str:
        """ Get the services layout as the layout may be different per station.
        There is probably a better way to do this!
        @return: The string of the positions (i.e. RRD for Right-Right-Down).
        """
        fleet_carrier = self.ap.jn.ship_state()['cur_station_type'].upper() == "FleetCarrier".upper()
        outpost = self.ap.jn.ship_state()['cur_station_type'].upper() == "Outpost".upper()
        # CONNECTED TO menu is different between stations and fleet carriers
        if fleet_carrier:
            # Fleet Carrier COMMODITIES MARKET location top right, with:
            # uni cart, redemption, tritium depot, shipyard, crew lounge
            return "RR"

        elif outpost:
            # Outpost COMMODITIES MARKET location in middle column
            return "R"

        else:
            # Orbital station COMMODITIES MARKET location bottom left
            return "D"

    def goto_commodities_market(self) -> bool:
        """ Go to the COMMODITIES market. """
        # Go down to station services
        res = self.goto_station_services()
        if not res:
            return False

        # Try to determine commodities button on the services screen. Have seen it below Mission Board and too
        # right of the mission board.
        res = self.determine_commodities_location()
        if res == "":
            logger.warning("Unable to find COMMODITIES MARKET button on Station Services screen.")
            return False

        self.ap_ckb('log+vce', "Connecting to commodities market.")

        # Select Mission Board
        if res == "RR":
            # Fleet Carrier COMMODITIES MARKET location top right, with:
            # uni cart, redemption, tritium depot, shipyard, crew lounge
            self.keys.send('UI_Right', repeat=2)
            self.keys.send('UI_Select')  # Select Commodities

        elif res == "R":
            # Outpost COMMODITIES MARKET location in middle column
            self.keys.send('UI_Right')
            self.keys.send('UI_Select')  # Select Commodities

        elif res == "D":
            # Orbital station COMMODITIES MARKET location bottom left
            self.keys.send('UI_Down')
            self.keys.send('UI_Select')  # Select Commodities

        if self.ap.debug_overlay:
            mkt = Quad.from_rect(self.reg['commodities_market']['rect'])
            self.ap.overlay.overlay_quad_pct('commodities_market', mkt, (0, 255, 0), 2, 5)
            self.ap.overlay.overlay_paint()

        # Wait for screen to appear
        res = self.ocr.wait_for_text(self.ap, [self.locale["COMMODITIES_MARKET"]], self.reg['market_header'])
        return res

    @staticmethod
    def sell_to_colonisation_ship(ap):
        """ Sell all cargo to a colonisation/construction ship.
        """
        ap.keys.send('UI_Left', repeat=3)  # Go to table
        ap.keys.send('UI_Down', hold=2)  # Go to bottom
        ap.keys.send('UI_Up')  # Select RESET/CONFIRM TRANSFER/TRANSFER ALL
        ap.keys.send('UI_Left', repeat=2)  # Go to RESET
        ap.keys.send('UI_Right', repeat=2)  # Go to TRANSFER ALL
        ap.keys.send('UI_Select')  # Select TRANSFER ALL
        sleep(0.5)

        ap.keys.send('UI_Left')  # Go to CONFIRM TRANSFER
        ap.keys.send('UI_Select')  # Select CONFIRM TRANSFER
        sleep(2)

        ap.keys.send('UI_Down')  # Go to EXIT
        ap.keys.send('UI_Select')  # Select EXIT

        sleep(2)  # give time to popdown menu


class PassengerLounge:
    def __init__(self, station_services_in_ship: EDStationServicesInShip, ed_ap, ocr, keys, screen, cb):
        self.parent = station_services_in_ship
        self.ap = ed_ap
        self.ocr = ocr
        self.keys = keys
        self.screen = screen
        self.ap_ckb = cb

        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        # Nav Panel region covers the entire navigation panel.
        self.reg = {'no_cmpl_missions': {'rect': [0.47, 0.77, 0.675, 0.85]},
                    'mission_dest_col': {'rect': [0.47, 0.41, 0.64, 0.85]},
                    'complete_mission_col': {'rect': [0.47, 0.22, 0.675, 0.85]}}

        self.no_cmpl_missions_row_width = 384  # Buy/sell item width in pixels at 1920x1080
        self.no_cmpl_missions_row_height = 70  # Buy/sell item height in pixels at 1920x1080
        self.mission_dest_row_width = 326  # Buy/sell item width in pixels at 1920x1080
        self.mission_dest_row_height = 70  # Buy/sell item height in pixels at 1920x1080
        self.complete_mission_row_width = 384  # Buy/sell item width in pixels at 1920x1080
        self.complete_mission_row_height = 70  # Buy/sell item height in pixels at 1920x1080


class CommoditiesMarket:
    def __init__(self, station_services_in_ship: EDStationServicesInShip, ed_ap, ocr, keys, screen, cb):
        self.parent = station_services_in_ship
        self.ap = ed_ap
        self.ocr = ocr
        self.keys = keys
        self.screen = screen
        self.ap_ckb = cb

        self.market_parser = MarketParser()
        # The reg rect is top left x, y, and bottom right x, y in fraction of screen resolution at 1920x1080
        self.reg = {'cargo_col': {'rect': [0.13, 0.227, 0.19, 0.90]},
                    'commodity_name_col': {'rect': [0.19, 0.227, 0.41, 0.90]},
                    'supply_demand_col': {'rect': [0.42, 0.227, 0.49, 0.90]}}
        self.commodity_row_width = 422  # Buy/sell item width in pixels at 1920x1080
        self.commodity_row_height = 35  # Buy/sell item height in pixels at 1920x1080

    def select_buy(self, keys) -> bool:
        """ Select Buy. Assumes on Commodities Market screen. """

        # Select Buy
        keys.send("UI_Left", repeat=2)
        keys.send("UI_Up", repeat=4)

        keys.send("UI_Select")  # Select Buy

        sleep(0.5)  # give time to bring up list
        keys.send('UI_Right')  # Go to top of commodities list
        return True

    def select_sell(self, keys) -> bool:
        """ Select Buy. Assumes on Commodities Market screen. """

        # Select Buy
        keys.send("UI_Left", repeat=2)
        keys.send("UI_Up", repeat=4)

        keys.send("UI_Down")
        keys.send("UI_Select")  # Select Sell

        sleep(0.5)  # give time to bring up list
        keys.send('UI_Right')  # Go to top of commodities list
        return True

    def buy_commodity(self, keys, name: str, qty: int, free_cargo: int) -> tuple[bool, int]:
        """ Buy qty of commodity. If qty >= 9999 then buy as much as possible.
        Assumed to be in the commodities buy screen in the list. """

        # If we are updating requirement count, me might have all the qty we need
        if qty <= 0:
            return False, 0

        # Determine if station sells the commodity!
        self.market_parser.get_market_data()
        if not self.market_parser.can_buy_item(name):
            self.ap_ckb('log+vce', f"'{name}' is not sold or has no stock at {self.market_parser.get_market_name()}.")
            logger.debug(f"Item '{name}' is not sold or has no stock at {self.market_parser.get_market_name()}.")
            return False, 0

        # Find commodity in mar
        # ket and return the index
        index = -1
        stock = 0
        buyable_items = self.market_parser.get_buyable_items()
        if buyable_items is not None:
            for i, value in enumerate(buyable_items):
                if value['Name_Localised'].upper() == name.upper():
                    index = i
                    stock = value['Stock']
                    logger.debug(f"Execute trade: Buy {name} (want {qty} of {stock} avail.) at position {index + 1}.")
                    break

        # Actual qty we can sell
        act_qty = min(qty, stock, free_cargo)

        # See if we buy all and if so, remove the item to update the list, as the item will be removed
        # from the commodities screen, but the market.json will not be updated.
        buy_all = act_qty == stock
        if buy_all:
            for i, value in enumerate(self.market_parser.current_data['Items']):
                if value['Name_Localised'].upper() == name.upper():
                    # Set the stock bracket to 0, so it does not get included in available commodities list.
                    self.market_parser.current_data['Items'][i]['StockBracket'] = 0

        if index > -1:
            keys.send('UI_Up', hold=3.0)  # go up to top of list
            keys.send('UI_Down', hold=0.05, repeat=index)  # go down # of times user specified
            sleep(0.5)
            keys.send('UI_Select')  # Select that commodity

            sleep(0.5)  # give time to popup
            keys.send('UI_Up', repeat=2)  # go up to quantity to buy (may not default to this)
            # Log the planned quantity
            self.ap_ckb('log+vce', f"Buying {act_qty} units of {name}.")
            logger.info(f"Attempting to buy {act_qty} units of {name}")
            # Increment count
            if qty >= 9999 or qty >= stock or qty >= free_cargo:
                keys.send("UI_Right", hold=4)
            else:
                keys.send("UI_Right", hold=0.04, repeat=act_qty)
            keys.send('UI_Down')
            keys.send('UI_Select')  # Select Buy
            sleep(0.5)
            # keys.send('UI_Back')  # Back to commodities list

        return True, act_qty

    def sell_commodity(self, keys, name: str, qty: int, cargo_parser) -> tuple[bool, int]:
        """ Sell qty of commodity. If qty >= 9999 then sell as much as possible.
        Assumed to be in the commodities sell screen in the list.
        @param keys: Keys class for sending keystrokes.
        @param name: Name of the commodity.
        @param qty: Quantity to sell.
        @param cargo_parser: Current cargo to check if rare or demand=1 items exist in hold.
        @return: Sale successful (T/F) and Qty.
        """

        # If we are updating requirement count, me might have sold all we have
        if qty <= 0:
            return False, 0

        # Determine if station buys the commodity!
        self.market_parser.get_market_data()
        if not self.market_parser.can_sell_item(name):
            self.ap_ckb('log+vce', f"'{name}' is not bought at {self.market_parser.get_market_name()}.")
            logger.debug(f"Item '{name}' is not bought at {self.market_parser.get_market_name()}.")
            return False, 0

        # Find commodity in market and return the index
        index = -1
        demand = 0
        sellable_items = self.market_parser.get_sellable_items(cargo_parser)
        if sellable_items is not None:
            for i, value in enumerate(sellable_items):
                if value['Name_Localised'].upper() == name.upper():
                    index = i
                    demand = value['Demand']
                    logger.debug(f"Execute trade: Sell {name} ({qty} of {demand} demanded) at position {index + 1}.")
                    break

        # Qty we can sell. Unlike buying, we can sell more than the demand
        # But maybe not at all stations!
        act_qty = qty

        if index > -1:
            keys.send('UI_Up', hold=3.0)  # go up to top of list
            keys.send('UI_Down', hold=0.05, repeat=index)  # go down # of times user specified
            sleep(0.5)
            keys.send('UI_Select')  # Select that commodity

            sleep(0.5)  # give time for popup
            keys.send('UI_Up', repeat=2)  # make sure at top

            # Log the planned quantity
            if qty >= 9999:
                self.ap_ckb('log+vce', f"Selling all our units of {name}.")
                logger.info(f"Attempting to sell all our units of {name}")
                keys.send("UI_Right", hold=4)
            else:
                self.ap_ckb('log+vce', f"Selling {act_qty} units of {name}.")
                logger.info(f"Attempting to sell {act_qty} units of {name}")
                keys.send('UI_Left', hold=4.0)  # Clear quantity to 0
                keys.send("UI_Right", hold=0.04, repeat=act_qty)

            keys.send('UI_Down')  # Down to the Sell button (already assume sell all)
            keys.send('UI_Select')  # Select to Sell all
            sleep(0.5)
            # keys.send('UI_Back')  # Back to commodities list

        return True, act_qty


def dummy_cb(msg, body=None):
    pass


# Usage Example
if __name__ == "__main__":
    from ED_AP import EDAutopilot
    test_ed_ap = EDAutopilot(cb=dummy_cb)
    test_ed_ap.keys.activate_window = True
    svcs = EDStationServicesInShip(test_ed_ap, test_ed_ap.scr, test_ed_ap.keys, test_ed_ap.ap_ckb)
    #svcs.goto_station_services()
    svcs.goto_commodities_market()



