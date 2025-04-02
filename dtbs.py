from flask import Flask, render_template_string, request, jsonify, send_from_directory
from datetime import datetime
import random
import sqlite3
from contextlib import closing

app = Flask(__name__)


# SQLite Database Setup
def init_db():
    with closing(sqlite3.connect('../appliances.db')) as db:
        cursor = db.cursor()

        # Drop tables if they exist to start fresh
        cursor.execute('DROP TABLE IF EXISTS appliances')
        cursor.execute('DROP TABLE IF EXISTS subcategories')
        cursor.execute('DROP TABLE IF EXISTS categories')

        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subcategories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appliances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL,
            energy_rating TEXT NOT NULL,
            annual_consumption TEXT,
            features TEXT,
            image_url TEXT,
            category_id INTEGER NOT NULL,
            subcategory_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (subcategory_id) REFERENCES subcategories (id)
        )
        ''')

        # Insert sample data if tables are empty
        if not cursor.execute('SELECT COUNT(*) FROM categories').fetchone()[0]:
            # Insert categories
            categories = [
                ('Kitchen Appliances',),
                ('Laundry & Cleaning Appliances',),
                ('Heating, Cooling, & Air Quality',),
                ('Home Entertainment & Smart Devices',),
                ('Smart Home & Security',),
                ('Personal Care & Grooming',),
                ('Miscellaneous Home Appliances',)
            ]
            cursor.executemany('INSERT INTO categories (name) VALUES (?)', categories)

            # Insert subcategories
            subcategories = [
                # Kitchen Appliances (1)
                (1, 'Refrigerator'), (1, 'Microwave Oven'),
                (1, 'Electric Stove'), (1, 'Dishwasher'),
                (1, 'Blender'), (1, 'Coffee Maker'),
                (1, 'Rice Cooker'), (1, 'Pressure Cooker'),
                (1, 'Air Fryer'), (1, 'Water Purifier'),

                # Laundry & Cleaning (2)
                (2, 'Washing Machine (Top Load)'), (2, 'Vacuum Cleaner'),
                (2, 'Robotic Vacuum'), (2, 'Steam Iron'),

                # Heating/Cooling (3)
                (3, 'Air Conditioner (Split)'), (3, 'Ceiling Fan'),
                (3, 'Space Heater'), (3, 'Air Purifier'),
                (3, 'Water Heater'),

                # Entertainment (4)
                (4, 'Smart TV'), (4, 'Soundbar'),
                (4, 'Smart Speaker'), (4, 'Gaming Console'),

                # Smart Home (5)
                (5, 'Security Camera'), (5, 'Smart Lock'),
                (5, 'Smart Thermostat'), (5, 'Smoke Detector'),

                # Personal Care (6)
                (6, 'Hair Dryer'), (6, 'Electric Shaver'),
                (6, 'Electric Toothbrush'),

                # Miscellaneous (7)
                (7, 'Treadmill'), (7, 'Air Compressor'),
                (7, 'Water Softener')
            ]
            cursor.executemany('INSERT INTO subcategories (category_id, name) VALUES (?, ?)', subcategories)
            sample_appliances = [
                # Kitchen Appliances
                # refrigerators
                ('RF001', 'LG 260L Smart Inverter', 'LG', 28990, '5 Star', '180 kWh',
                 '["Smart Inverter", "Hygiene Fresh+"]', 'appliance_images/RF001.jpg', 1, 1),

                ('RF002', 'Samsung 253L Frost Free', 'Samsung', 31990, '4 Star', '210 kWh',
                 '["Digital Inverter", "Twin Cooling"]', 'appliance_images/RF002.jpg', 1, 1),

                ('RF003', 'Whirlpool 240L Frost Free', 'Whirlpool', 26990, '3 Star', '220 kWh',
                 '["IntelliSense Inverter"]', 'appliance_images/RF003.jpg', 1, 1),

                ('RF004', 'Haier 258L Bottom Freezer', 'Haier', 27990, '4 Star', '190 kWh',
                 '["Twin Inverter", "Fast Cooling"]', 'appliance_images/RF004.jpg', 1, 1),

                ('RF005', 'Godrej 210L Direct Cool', 'Godrej', 19990, '3 Star', '210 kWh', '["Aroma Lock"]',
                 'appliance_images/RF005.jpg', 1, 1),

                ('RF006', 'Panasonic 380L Side-by-Side', 'Panasonic', 58990, '5 Star', '250 kWh',
                 '["Econavi", "Jewel Box"]', 'appliance_images/RF006.jpg', 1, 1),

                ('RF007', 'Bosch 300L VitaFresh', 'Bosch', 45990, '5 Star', '200 kWh', '["MultiAirflow", "FreshSense"]',
                 'appliance_images/RF007.jpg', 1, 1),

                ('RF008', 'Voltas 185L Direct Cool', 'Voltas', 16990, '2 Star', '230 kWh', '["Stabilizer Free"]',
                 'appliance_images/RF008.jpg', 1, 1),

                ('RF009', 'IFB 265L Frost Free', 'IFB', 33990, '4 Star', '195 kWh', '["Smart Cooling"]',
                 'appliance_images/RF009.jpg', 1, 1),

                ('RF010', 'Hitachi 320L Glass Door', 'Hitachi', 52990, '5 Star', '210 kWh', '["Eco Thermo Sensor"]',
                 'appliance_images/RF010.jpg', 1, 1),


                # microwaves
                ('MW001', 'Samsung 28L Convection', 'Samsung', 14990, '4 Star', '200 kWh', '["HotBlast", "Slim Fry"]',
                 'appliance_images/MW001.jpg', 1, 2),

                ('MW002', 'LG 32L Smart Inverter', 'LG', 16990, '5 Star', '220 kWh',
                 '["Auto Cook", "Charcoal Lighting"]', 'appliance_images/MW002.jpg', 1, 2),

                ('MW003', 'IFB 30L Convection', 'IFB', 15990, '4 Star', '210 kWh', '["Steam Clean", "Multi-Stage"]',
                 'appliance_images/MW003.jpg', 1, 2),

                ('MW004', 'Panasonic 27L Solo', 'Panasonic', 10990, '3 Star', '180 kWh', '["Auto Reheat"]',
                 'appliance_images/MW004.jpg', 1, 2),

                ('MW005', 'Bajaj 20L Grill', 'Bajaj', 8990, 'NA', '170 kWh', '["Grill & Bake"]',
                 'appliance_images/MW005.jpg', 1, 2),

                (
                'MW006', 'Godrej 23L Convection', 'Godrej', 12990, '4 Star', '190 kWh', '["Healthy Fry", "Pizza Mode"]',
                'appliance_images/MW006.jpg', 1, 2),

                ('MW007', 'Haier 25L Solo', 'Haier', 9990, '3 Star', '175 kWh', '["Express Cooking"]',
                 'appliance_images/MW007.jpg', 1, 2),

                ('MW008', 'Whirlpool 30L Convection', 'Whirlpool', 15990, '5 Star', '210 kWh',
                 '["Magic Cook", "Rotisserie"]', 'appliance_images/MW008.jpg', 1, 2),

                ('MW009', 'Bosch 32L Grill', 'Bosch', 17990, '5 Star', '230 kWh', '["Auto Defrost", "Child Lock"]',
                 'appliance_images/MW009.jpg', 1, 2),

                ('MW010', 'Voltas 20L Solo', 'Voltas', 7990, 'NA', '160 kWh', '["Quick Start"]',
                 'appliance_images/MW010.jpg', 1, 2),


                # Electric Stoves
                ('ES001', 'Prestige 4-Burner Glass Top', 'Prestige', 15990, '5 star', '350 kWh', '["Auto Ignition"]',
                 'appliance_images/ES001.jpg', 1, 3),

                ('ES002', 'Bajaj 2-Burner', 'Bajaj', 11990, '5 star', '320 kWh', '["Ceramic Plates"]',
                 'appliance_images/ES002.jpg', 1, 3),

                ('ES003', 'Philips Induction Cooker', 'Philips', 8990, '5 Star', '300 kWh',
                 '["Feather Touch", "Preset Menu"]', 'appliance_images/ES003.jpg', 1, 3),

                ('ES004', 'Pigeon 2-Burner Glass Top', 'Pigeon', 10990, '4 Star', '310 kWh',
                 '["Toughened Glass", "Auto Ignition"]', 'appliance_images/ES004.jpg.jpg', 1, 3),

                ('ES005', 'Havells Infrared Cooker', 'Havells', 9490, '5 Star', '290 kWh',
                 '["Infrared Heating", "Digital Timer"]', 'appliance_images/ES005.jpg', 1, 3),

                ('ES006', 'Usha 3-Burner Gas Stove', 'Usha', 12990, '4 Star', '330 kWh',
                 '["Brass Burners", "Toughened Glass"]', 'appliance_images/ES006.jpg', 1, 3),

                ('ES007', 'Butterfly Smart Induction', 'Butterfly', 7990, '3 Star', '280 kWh',
                 '["7 Preset Modes", "Overheat Protection"]', 'appliance_images/ES007.jpg', 1, 3),

                ('ES008', 'Bosch 4-Burner Hob', 'Bosch', 19990, '4 Star', '360 kWh',
                 '["Auto Cut-Off", "Flame Failure Safety"]', 'appliance_images/ES008.jpg', 1, 3),

                ('ES009', 'Wonderchef Induction Cooktop', 'Wonderchef', 8590, '5 Star', '295 kWh',
                 '["Ceramic Plate", "Touch Panel"]', 'appliance_images/ES009.jpg', 1, 3),

                ('ES010', 'Surya 2-Burner Gas Stove', 'Surya', 9990, '4 Star', '310 kWh',
                 '["Heat Resistant Pan Supports"]', 'appliance_images/ES010.jpg', 1, 3),

            # Dishwashers
                ('DW001', 'Bosch 12 Place', 'Bosch', 36990, '5 Star', '280 kWh', '["Eco Silence"]',
                 'appliance_images/DW001.jpg', 1, 4),
                ('DW002', 'IFB 15 Place', 'IFB', 31990, '5 Star', '300 kWh', '["Auto Program"]',
                 'appliance_images/DW002.jpg',
                 1, 4),
                ('DW003', 'Samsung 13 Place', 'Samsung', 33990, '5 Star', '290 kWh', '["Hygiene Wash"]',
                 'appliance_images/DW003.jpg', 1, 4),
                ('DW004', 'Whirlpool 14 Place', 'Whirlpool', 29990, '4 Star', '310 kWh', '["Power Dry"]',
                 'appliance_images/DW004.jpg', 1, 4),
                ('DW005', 'Voltas Beko 12 Place', 'Voltas Beko', 27990, '4 Star', '295 kWh', '["Aqua Flex"]',
                 'appliance_images/DW005.jpg', 1, 4),
                ('DW006', 'Hafele 15 Place', 'Hafele', 34990, '5 Star', '280 kWh', '["Inverter Drive"]',
                 'appliance_images/DW006.jpg', 1, 4),
                ('DW007', 'Elica 12 Place', 'Elica', 25990, '4 Star', '300 kWh', '["Intensive Mode"]',
                 'appliance_images/DW007.jpg', 1, 4),
                ('DW008', 'Siemens 13 Place', 'Siemens', 35990, '5 Star', '285 kWh', '["Vario Speed Plus"]',
                 'appliance_images/DW008.jpg', 1, 4),
                ('DW009', 'Haier 14 Place', 'Haier', 27990, '4 Star', '310 kWh', '["Quick Wash"]',
                 'appliance_images/DW009.jpg', 1, 4),
                ('DW010', 'Godrej 12 Place', 'Godrej', 26990, '4 Star', '290 kWh', '["Auto Door Open"]',
                 'appliance_images/DW0010.jpg', 1, 4),

                # blenders
                (
                    'BL001', 'Philips 600W', 'Philips', 3990, '5 star', '60 kWh', '["Multi-Speed"]',
                    'appliance_images/BL001.jpg',
                    1, 5),
                ('BL002', 'Bajaj 500W', 'Bajaj', 2990, '4 star', '50 kWh', '["Overload Protection"]',
                 'appliance_images/BL002.jpg', 1, 5),
                ('BL003', 'Prestige 750W', 'Prestige', 4490, '3 star', '65 kWh', '["Stainless Steel Blades"]',
                 'appliance_images/BL003.jpg', 1, 5),
                ('BL004', 'Panasonic 600W', 'Panasonic', 3790, '5 star', '55 kWh', '["2 Jars Included"]',
                 'appliance_images/BL004.jpg', 1, 5),
                ('BL005', 'Bosch 800W', 'Bosch', 5290, '4 star', '70 kWh', '["Ice Crushing"]',
                 'appliance_images/BL005.jpg', 1,
                 5),
                ('BL006', 'Usha 700W', 'Usha', 4190, '3 star', '60 kWh', '["Variable Speed"]',
                 'appliance_images/BL006.jpg', 1,
                 5),
                ('BL007', 'Kent 600W', 'Kent', 3690, '5 star', '58 kWh', '["Compact Design"]',
                 'appliance_images/BL007.jpg', 1,
                 5),
                ('BL008', 'Havells 900W', 'Havells', 5590, '4 star', '75 kWh', '["Digital Display"]',
                 'appliance_images/BL008.jpg', 1, 5),
                ('BL009', 'Wonderchef 500W', 'Wonderchef', 2990, '5 star', '50 kWh', '["1.5L Jar"]',
                 'appliance_images/BL009.jpg', 1, 5),
                ('BL010', 'Sujata 1000W', 'Sujata', 5990, '3 star', '80 kWh', '["Heavy-Duty Motor"]',
                 'appliance_images/BL010.jpg', 1, 5),

            # Coffee Makers
            ('CM001', 'Philips 1200W', 'Philips', 4490, '5 star', '90 kWh', '["Auto Shutoff"]',
             'appliance_images/CM001.jpg', 1, 6),
            ('CM002', 'Bajaj 800W', 'Bajaj', 2990, '5 star', '70 kWh', '["Anti-Drip"]', 'appliance_images/CM002.jpg', 1, 6),
            ('CM003', 'Morphy Richards 900W', 'Morphy Richards', 3690, '5 star', '80 kWh', '["Milk Frother"]',
             'appliance_images/CM003.jpg', 1, 6),
            (
            'CM004', 'Prestige 750W', 'Prestige', 3290, '5 star', '75 kWh', '["Keep Warm"]', 'appliance_images/CM004.jpg',
            1, 6),
            ('CM005', 'Panasonic 1000W', 'Panasonic', 4990, '5 star', '100 kWh', '["Digital Timer"]',
             'appliance_images/CM005.jpg', 1, 6),
            ('CM006', 'Havells 850W', 'Havells', 3490, '5 star', '78 kWh', '["Adjustable Strength"]',
             'appliance_images/CM006.jpg', 1, 6),
            (
            'CM007', 'Usha 700W', 'Usha', 2790, '4 star', '68 kWh', '["Thermal Carafe"]', 'appliance_images/CM007.jpg', 1, 6),
            ('CM008', 'Kent 950W', 'Kent', 3990, '5 star', '85 kWh', '["Auto Clean"]', 'appliance_images/CM008.jpg', 1, 6),
            ('CM009', 'Wonderchef 800W', 'Wonderchef', 3190, '5 star', '72 kWh', '["Stainless Steel Filter"]',
             'appliance_images/CM009.jpg', 1, 6),
            ('CM010', 'Bosch 1100W', 'Bosch', 5490, '5 star', '110 kWh', '["Aroma Control"]', 'appliance_images/CM010.jpg',
             1, 6),


                # Rice Cookers
            ('RC001', 'Prestige 2L', 'Prestige', 2490, '5 star', '70 kWh', '["Auto Cooking"]', 'appliance_images/RC001.jpg',
             1, 5),
            ('RC002', 'Panasonic 1.8L', 'Panasonic', 3290, '3 star', '80 kWh', '["Keep Warm"]',
             'appliance_images/RC002.jpg', 1, 3),
            (
            'RC003', 'Bajaj 1.5L', 'Bajaj', 2790, '4 star', '75 kWh', '["Non-Stick Pot"]', 'appliance_images/RC003.jpg', 1, 4),
            ('RC004', 'Philips 2.2L', 'Philips', 3490, '4 star', '85 kWh', '["One-Touch Operation"]',
             'appliance_images/RC004.jpg', 1, 4),
            ('RC005', 'Havells 2L', 'Havells', 2890, '5 star', '78 kWh', '["Auto Shutoff"]', 'appliance_images/RC005.jpg', 1,
             5),
            ('RC006', 'Usha 1.8L', 'Usha', 3190, '3 star', '80 kWh', '["Multi-Function"]', 'appliance_images/RC006.jpg', 1, 3),
            ('RC007', 'Kent 2.5L', 'Kent', 3690, '4 star', '90 kWh', '["Stainless Steel Inner Pot"]',
             'appliance_images/RC007.jpg', 1, 4),
            ('RC008', 'Wonderchef 1.8L', 'Wonderchef', 2990, '4 star', '76 kWh', '["Auto Steam Release"]',
             'appliance_images/RC008.jpg', 1, 4),
            ('RC009', 'Butterfly 2L', 'Butterfly', 2890, '5 star', '72 kWh', '["Energy Efficient"]',
             'appliance_images/RC009.jpg', 1, 5),
            ('RC010', 'Orient 1.5L', 'Orient', 2590, '2 star', '65 kWh', '["Cool Touch Handle"]',
             'appliance_images/RC010.jpg', 1, 2),

                # Pressure Cookers
                ('PC001', 'Prestige 5L', 'Prestige', 2990, '4 star', '90 kWh', '["Multi-Safety"]',
                 'appliance_images/PC001.jpg', 1, 8),
                ('PC002', 'Hawkins 3L', 'Hawkins', 1990, '4 star', '80 kWh', '["Hard Anodized"]',
                 'appliance_images/PC002.jpg', 1, 8),
                ('PC003', 'Bajaj 5L', 'Bajaj', 2590, '5 Star', '90 kWh', '["Pressure Indicator"]',
                 'appliance_images/PC003.jpg', 1, 8),
                ('PC004', 'Prestige 3L', 'Prestige', 2490, '4 Star', '80 kWh', '["Whistle Control"]',
                 'appliance_images/PC004.jpg', 1, 8),
                ('PC005', 'Philips 6L', 'Philips', 3190, '5 Star', '100 kWh', '["Auto Locking"]',
                 'appliance_images/PC005.jpg', 1, 8),
                ('PC006', 'Pigeon 3L', 'Pigeon', 1790, '3 Star', '70 kWh', '["Cool Touch Handles"]',
                 'appliance_images/PC006.jpg', 1, 8),
                ('PC007', 'Hawkins 4L', 'Hawkins', 2390, '4 Star', '85 kWh', '["Heavy Gauge Aluminum"]',
                 'appliance_images/PC007.jpg', 1, 8),
                ('PC008', 'Prestige 2L', 'Prestige', 1990, '3 Star', '60 kWh', '["Pressure Regulator"]',
                 'appliance_images/PC008.jpg', 1, 8),
                ('PC009', 'Tefal 5L', 'Tefal', 3590, '5 Star', '110 kWh', '["Induction Compatible"]',
                 'appliance_images/PC009.jpg', 1, 8),
                ('PC010', 'Borosil 3L', 'Borosil', 2790, '4 Star', '90 kWh', '["Auto Pressure Control"]',
                 'appliance_images/PC010.jpg', 1, 8),


                # Air Fryers
                ('AF001', 'Philips HD9252', 'Philips', 9990, '3 Star', '80 kWh', '["Rapid Air"]',
                 'appliance_images/AF001.jpg', 1, 9),
                ('AF002', 'Instant Pot Vortex', 'Instant Pot', 11990, '4 Star', '85 kWh', '["7-in-1"]',
                 'appliance_images/AF002.jpg', 1, 9),
                ('AF003', 'Ninja Air Fryer', 'Ninja', 8490, '4 Star', '75 kWh', '["Wide Temperature Range"]',
                 'appliance_images/AF003.jpg', 1, 9),
                ('AF004', 'Tefal ActiFry', 'Tefal', 9490, '5 Star', '80 kWh', '["Easy to Clean"]',
                 'appliance_images/AF004.jpg', 1, 9),
                ('AF005', 'Black+Decker Air Fryer', 'Black+Decker', 7990, '3 Star', '70 kWh', '["Fast Cooking"]',
                 'appliance_images/AF005.jpg', 1, 9),
                ('AF006', 'GoWISE USA 5.8QT', 'GoWISE USA', 8490, '4 Star', '78 kWh', '["Touchscreen Controls"]',
                 'appliance_images/AF006.jpg', 1, 9),
                ('AF007', 'Cuisinart Air Fryer', 'Cuisinart', 10990, '4 Star', '85 kWh', '["Preheat Function"]',
                 'appliance_images/AF007.jpg', 1, 9),
                ('AF008', 'Cosori Smart Air Fryer', 'Cosori', 12990, '5 Star', '90 kWh', '["Wi-Fi Enabled"]',
                 'appliance_images/AF008.jpg', 1, 9),
                ('AF009', 'Breville Smart Oven Air', 'Breville', 24990, '4 Star', '95 kWh',
                 '["Multiple Cooking Functions"]',
                 'appliance_images/AF009.jpg', 1, 9),
                ('AF010', 'Chefman TurboFry', 'Chefman', 6490, '3 Star', '60 kWh', '["Compact Size"]',
                 'appliance_images/AF010.jpg', 1, 9),



                # Water Purifiers
                ('WP001', 'Kent Supreme Plus', 'Kent', 18990, '5 star', '50 kWh', '["UV+UF+RO"]',
                 'appliance_images/WP001.jpg', 1, 10),
                ('WP002', 'Aquaguard Geneus', 'Aquaguard', 21990, '4 star', '45 kWh', '["TDS Controller"]',
                 'appliance_images/WP002.jpg', 1, 10),
                ('WP003', 'Pureit Ultima', 'Pureit', 24990, '5 star', '60 kWh', '["UV+RO"]',
                 'appliance_images/WP003.jpg', 1, 10),
                ('WP004', 'Eureka Forbes Aquasure', 'Eureka Forbes', 10990, '4 star', '50 kWh', '["UV+UF"]',
                 'appliance_images/WP004.jpg', 1, 10),
                ('WP005', 'HUL Pureit Marvella', 'HUL', 13990, '4 star', '55 kWh', '["TDS Adjuster"]',
                 'appliance_images/WP005.jpg', 1, 10),
                (
                'WP006', 'Kent Ace', 'Kent', 12990, '4 star', '50 kWh', '["RO+UV+UF"]', 'appliance_images/WP006.jpg', 1,
                10),
                ('WP007', 'Livpure Glo', 'Livpure', 15990, '5 star', '60 kWh', '["UV+UF+RO"]',
                 'appliance_images/WP007.jpg', 1, 10),
                ('WP008', 'Blue Star Aristo', 'Blue Star', 17990, '4 star', '55 kWh', '["RO+UV"]',
                 'appliance_images/WP008.jpg', 1, 10),
                ('WP009', 'Tata Swach Smart', 'Tata', 7990, '3 star', '40 kWh', '["UV"]', 'appliance_images/WP009.jpg',
                 1, 10),
                ('WP010', 'AquaSure from Aquaguard', 'Eureka Forbes', 9990, '3 star', '45 kWh', '["UV+UF"]',
                 'appliance_images/WP010.jpg', 1, 10),

                ########################################################################################################3
                # Laundry & Cleaning
                # washing machine
                ('WM001', 'Samsung 6.5kg Top Load', 'Samsung', 18990, '4 Star', '280 kWh', '["Diamond Drum"]',
                 'appliance_images/WM001.jpg', 2, 1),
                ('WM002', 'LG 7kg Front Load', 'LG', 32990, '5 Star', '240 kWh', '["Inverter Direct Drive"]',
                 'appliance_images/WM002.jpg', 2, 1),
                ('WM003', 'Whirlpool 8kg Semi-Auto', 'Whirlpool', 12990, '3 Star', '320 kWh', '["Power Scrub"]',
                 'appliance_images/WM003.jpg', 2, 1),
                ('WM004', 'Bosch 7.5kg Front Load', 'Bosch', 34990, '5 Star', '230 kWh', '["EcoSilence Drive"]',
                 'appliance_images/WM004.jpg', 2, 1),
                ('WM005', 'IFB 6kg Front Load', 'IFB', 28990, '5 Star', '250 kWh', '["Aqua Energie"]',
                 'appliance_images/WM005.jpg', 2, 1),
                ('WM006', 'Panasonic 6.2kg Top Load', 'Panasonic', 19990, '4 Star', '270 kWh', '["Active Foam System"]',
                 'appliance_images/WM006.jpg', 2, 1),
                ('WM007', 'Haier 6.5kg Fully Auto', 'Haier', 21990, '4 Star', '260 kWh', '["Near Zero Pressure"]',
                 'appliance_images/WM007.jpg', 2, 1),
                ('WM008', 'Godrej 7kg Top Load', 'Godrej', 20990, '4 Star', '290 kWh', '["Turbo 6 Pulsator"]',
                 'appliance_images/WM008.jpg', 2, 1),
                ('WM009', 'Onida 6kg Fully Auto', 'Onida', 17990, '3 Star', '300 kWh', '["Hexa Crystal Drum"]',
                 'appliance_images/WM009.jpg', 2, 1),
                ('WM010', 'Samsung 8kg Front Load', 'Samsung', 39990, '5 Star', '220 kWh', '["Bubble Soak"]',
                 'appliance_images/WM010.jpg', 2, 1),

                # vacuum cleaner
                ('VC001', 'Eureka Forbes Trendy', 'Eureka Forbes', 5990, '5 star', '120 kWh', '["Bagless"]',
                 'appliance_images/VC001.jpg', 2, 2),
                ('VC002', 'Dyson V8 Absolute', 'Dyson', 34990, '4 star', '50 kWh', '["Cordless"]',
                 'appliance_images/VC002.jpg', 2, 2),
                ('VC003', 'Philips PowerPro', 'Philips', 10990, '4 star', '110 kWh', '["Cyclone Filter"]',
                 'appliance_images/VC003.jpg', 2, 2),
                ('VC004', 'Karcher VC4', 'Karcher', 15990, '3 star', '130 kWh', '["HEPA Filter"]',
                 'appliance_images/VC004.jpg', 2, 2),
                ('VC005', 'Bosch GAS 15', 'Bosch', 19990, '4 star', '140 kWh', '["Blower Function"]',
                 'appliance_images/VC005.jpg', 2, 2),
                ('VC006', 'Kent Zoom', 'Kent', 7990, '5 star', '90 kWh', '["Rechargeable"]',
                 'appliance_images/VC006.jpg', 2, 2),
                ('VC007', 'LG CordZero', 'LG', 32990, '4 star', '55 kWh', '["Dual Battery"]',
                 'appliance_images/VC007.jpg', 2, 2),
                ('VC008', 'Inalsa Spruce', 'Inalsa', 3990, '3 star', '125 kWh', '["Wet & Dry"]',
                 'appliance_images/VC008.jpg', 2, 2),
                ('VC009', 'Prestige Typhoon', 'Prestige', 5990, '4 star', '115 kWh', '["High Suction"]',
                 'appliance_images/VC009.jpg', 2, 2),
                ('VC010', 'Panasonic MC-CL571', 'Panasonic', 11990, '3 star', '135 kWh', '["Cyclone System"]',
                 'appliance_images/VC010.jpg', 2, 2),

                # robotic vacuum cleaners
                ('RV001', 'Xiaomi Mi Robot', 'Xiaomi', 24990, '4 star', '100 kWh', '["LIDAR"]',
                 'appliance_images/RV001.jpg', 2, 3),
                ('RV002', 'iRobot Roomba i3', 'iRobot', 39990, '5 star', '80 kWh', '["Auto Empty"]',
                 'appliance_images/RV002.jpg', 2, 3),
                ('RV003', 'Ecovacs Deebot N8', 'Ecovacs', 29990, '4 star', '85 kWh', '["Mopping"]',
                 'appliance_images/RV003.jpg', 2, 3),
                ('RV004', 'Roborock S7', 'Roborock', 44990, '5 star', '75 kWh', '["Sonic Mopping"]',
                 'appliance_images/RV004.jpg', 2, 3),
                ('RV005', 'ILIFE V5s Pro', 'ILIFE', 16990, '3 star', '90 kWh', '["Water Tank"]',
                 'appliance_images/RV005.jpg', 2, 3),
                ('RV006', 'iRobot Roomba 694', 'iRobot', 29990, '4 star', '78 kWh', '["WiFi Enabled"]',
                 'appliance_images/RV006.jpg', 2, 3),
                ('RV007', 'Eufy RoboVac X8', 'Eufy', 34990, '5 star', '70 kWh', '["Twin Turbine"]',
                 'appliance_images/RV007.jpg', 2, 3),
                ('RV008', 'Dreame D9 Max', 'Dreame', 25990, '4 star', '95 kWh', '["LIDAR Navigation"]',
                 'appliance_images/RV008.jpg', 2, 3),
                ('RV009', 'Samsung Jet Bot+', 'Samsung', 49990, '5 star', '65 kWh', '["SmartThings"]',
                 'appliance_images/RV009.jpg', 2, 3),
                ('RV010', 'Viomi SE', 'Viomi', 28990, '4 star', '88 kWh', '["Multi-Floor Mapping"]',
                 'appliance_images/RV010.jpg', 2, 3),

                # Steam Irons
                ('SI001', 'Philips GC1905', 'Philips', 1990, '4 star', '60 kWh', '["Anti-Calc"]',
                 'appliance_images/SI001.jpg', 2, 4),
                ('SI002', 'Bajaj Majesty DX-7', 'Bajaj', 1290, '4 star', '50 kWh', '["Ceramic Soleplate"]',
                 'appliance_images/SI002.jpg', 2, 4),
                ('SI003', 'Usha EI 1602', 'Usha', 1090, '3 star', '45 kWh', '["Non-Stick Soleplate"]',
                 'appliance_images/SI003.jpg', 2, 4),
                ('SI004', 'Morphy Richards Super Glide', 'Morphy Richards', 2790, '4 star', '65 kWh', '["Turbo Steam"]',
                 'appliance_images/SI004.jpg', 2, 4),
                ('SI005', 'Havells Magnum', 'Havells', 2290, '4 star', '58 kWh', '["Precision Tip"]',
                 'appliance_images/SI005.jpg', 2, 4),
                ('SI006', 'Orient FabriGlow', 'Orient', 1390, '3 star', '52 kWh', '["Dry & Steam"]',
                 'appliance_images/SI006.jpg', 2, 4),
                ('SI007', 'Panasonic NI-100DX', 'Panasonic', 1690, '3 star', '55 kWh', '["Temperature Control"]',
                 'appliance_images/SI007.jpg', 2, 4),
                ('SI008', 'Singer Style Steam', 'Singer', 1490, '4 star', '53 kWh', '["Spray Function"]',
                 'appliance_images/SI008.jpg', 2, 4),
                ('SI009', 'Inalsa Optra', 'Inalsa', 1299, '3 star', '48 kWh', '["Variable Steam"]',
                 'appliance_images/SI009.jpg', 2, 4),
                ('SI010', 'Kent Smart 1600W', 'Kent', 1999, '4 star', '60 kWh', '["Fast Heat Up"]',
                 'appliance_images/SI010.jpg', 2, 4),

                ###############################################################################################################
                # Heating/Cooling
                # Air Conditioners
                ('AC001', 'Daikin 1.5 Ton 5-Star Inverter', 'Daikin', 42990, '5 Star', '950 kWh',
                 '["Copper Condenser", "PM 2.5 Filter"]', 'appliance_images/AC001.jpg', 3, 1),
                ('AC002', 'LG 1.5 Ton 3-Star Window', 'LG', 32990, '3 Star', '1200 kWh',
                 '["Ocean Black", "Auto Clean"]', 'appliance_images/AC002.jpg', 3, 1),
                ('AC003', 'Voltas 1.5 Ton 3-Star Split', 'Voltas', 34990, '3 Star', '1100 kWh',
                 '["Turbo Cool", "Dehumidifier"]', 'appliance_images/AC003.jpg', 3, 1),
                ('AC004', 'Blue Star 2 Ton 5-Star Inverter', 'Blue Star', 55990, '5 Star', '1000 kWh',
                 '["iFeel Technology", "Self-Diagnosis"]', 'appliance_images/AC004.jpg', 3, 1),
                ('AC005', 'Carrier 1 Ton 3-Star Split', 'Carrier', 28990, '3 Star', '900 kWh',
                 '["Flexicool", "Dust Filter"]', 'appliance_images/AC005.jpg', 3, 1),
                ('AC006', 'Hitachi 1.5 Ton 5-Star Inverter', 'Hitachi', 46990, '5 Star', '850 kWh',
                 '["Kaze Filter", "Eco Mode"]', 'appliance_images/AC006.jpg', 3, 1),
                ('AC007', 'Samsung 1.5 Ton 3-Star Wind-Free', 'Samsung', 49990, '3 Star', '1050 kWh',
                 '["Digital Inverter", "Triple Protection"]', 'appliance_images/AC007.jpg', 3, 1),
                ('AC008', 'Whirlpool 1.5 Ton 3-Star Split', 'Whirlpool', 31990, '3 Star', '1150 kWh',
                 '["6th Sense", "Stabilizer Free"]', 'appliance_images/AC008.jpg', 3, 1),
                ('AC009', 'Godrej 1 Ton 5-Star Inverter', 'Godrej', 38990, '5 Star', '800 kWh',
                 '["R32 Refrigerant", "Golden Fin"]', 'appliance_images/AC009.jpg', 3, 1),
                ('AC010', 'Panasonic 2 Ton 3-Star Split', 'Panasonic', 45990, '3 Star', '1250 kWh',
                 '["Econavi", "Nanoe-G"]', 'appliance_images/AC010.jpg', 3, 1),

                # Ceiling Fans
                ('CF001', 'Crompton Energion HS 1200mm', 'Crompton', 2990, '5 Star', '60 kWh',
                 '["BLDC Motor", "Remote Control"]', 'appliance_images/CF001.jpg', 3, 2),
                ('CF002', 'Havells Leganza 1200mm', 'Havells', 3490, '5 Star', '55 kWh', '["Decorative", "3-Speed"]',
                 'appliance_images/CF002.jpg', 3, 2),
                ('CF003', 'Bajaj Frore 1200mm', 'Bajaj', 2790, '4 Star', '65 kWh', '["Anti-Dust", "High Air Delivery"]',
                 'appliance_images/CF003.jpg', 3, 2),
                ('CF004', 'Orient Electric Apex-FX 1200mm', 'Orient', 3290, '5 Star', '58 kWh',
                 '["Wet/Dry", "Decorative"]', 'appliance_images/CF004.jpg', 3, 2),
                ('CF005', 'Usha Bloom 1200mm', 'Usha', 2590, '4 Star', '70 kWh', '["ABS Blades", "3-Speed"]',
                 'appliance_images/CF005.jpg', 3, 2),
                ('CF006', 'Luminous Dhoom 1200mm', 'Luminous', 2390, '3 Star', '75 kWh',
                 '["High Speed", "Balanced Blades"]', 'appliance_images/CF006.jpg', 3, 2),
                ('CF007', 'Atomberg Renesa 1200mm', 'Atomberg', 3990, '5 Star', '50 kWh', '["BLDC", "Smart Control"]',
                 'appliance_images/CF007.jpg', 3, 2),
                ('CF008', 'Khaitan Elegance 1200mm', 'Khaitan', 2190, '3 Star', '80 kWh',
                 '["Decorative", "High Air Throw"]', 'appliance_images/CF008.jpg', 3, 2),
                ('CF009', 'Surya Neo 1200mm', 'Surya', 2690, '4 Star', '68 kWh', '["Anti-Rust", "3-Speed"]',
                 'appliance_images/CF009.jpg', 3, 2),
                ('CF010', 'Polar Hunter 1200mm', 'Polar', 2490, '3 Star', '72 kWh', '["ABS Blades", "Decorative"]',
                 'appliance_images/CF010.jpg', 3, 2),

                # Space Heaters
                ('SH001', 'Bajaj Flashy 1000W', 'Bajaj', 2490, 'NA', '500 kWh',
                 '["Overheat Protection", "Tip-Over Switch"]', 'appliance_images/SH001.jpg', 3, 3),
                ('SH002', 'Usha FH1212 2000W', 'Usha', 1990, 'NA', '450 kWh',
                 '["Adjustable Thermostat", "Carry Handle"]', 'appliance_images/SH002.jpg', 3, 3),
                ('SH003', 'Morphy Richards Oyster 1200W', 'Morphy Richards', 3490, 'NA', '480 kWh',
                 '["Ceramic Heating", "Oscillation"]', 'appliance_images/SH003.jpg', 3, 3),
                ('SH004', 'Havells Cozio 2000W', 'Havells', 2990, 'NA', '520 kWh', '["PTC Ceramic", "Remote Control"]',
                 'appliance_images/SH004.jpg', 3, 3),
                ('SH005', 'Orient Electric Areva 1500W', 'Orient', 2290, 'NA', '490 kWh',
                 '["Fan Heater", "2 Heat Settings"]', 'appliance_images/SH005.jpg', 3, 3),
                ('SH006', 'Crompton Greaves Amica 2000W', 'Crompton', 2790, 'NA', '510 kWh',
                 '["Radiant Heating", "Overheat Cut-off"]', 'appliance_images/SH006.jpg', 3, 3),
                ('SH007', 'Kenstar Halo 2000W', 'Kenstar', 2590, 'NA', '530 kWh',
                 '["PTC Technology", "Adjustable Thermostat"]', 'appliance_images/SH007.jpg', 3, 3),
                ('SH008', 'Orpat OEH-1260 2000W', 'Orpat', 1790, 'NA', '550 kWh',
                 '["Fan Heater", "Overload Protection"]', 'appliance_images/SH008.jpg', 3, 3),
                ('SH009', 'V-Guard Sunny 2000W', 'V-Guard', 2690, 'NA', '540 kWh',
                 '["Ceramic Plate", "Thermostat Control"]', 'appliance_images/SH009.jpg', 3, 3),
                ('SH010', 'Eveready QH800 800W', 'Eveready', 1290, 'NA', '400 kWh', '["Compact", "Portable"]',
                 'appliance_images/SH010.jpg', 3, 3),

                # Air Purifiers
                ('AP001', 'Dyson Pure Cool TP07', 'Dyson', 34990, 'NA', '80 kWh',
                 '["HEPA+Activated Carbon", "Air Multiplier"]', 'appliance_images/AP001.jpg', 3, 4),
                ('AP002', 'Philips AC2887/20', 'Philips', 24990, 'NA', '70 kWh', '["AeraSense", "3-Stage Filtration"]',
                 'appliance_images/AP002.jpg', 3, 4),
                ('AP003', 'Honeywell Air Touch i8', 'Honeywell', 18990, 'NA', '90 kWh', '["HEPA", "Ionizer"]',
                 'appliance_images/AP003.jpg', 3, 4),
                ('AP004', 'Sharp FP-J40M-W', 'Sharp', 15990, 'NA', '85 kWh', '["Plasmacluster", "Humidifying"]',
                 'appliance_images/AP004.jpg', 3, 4),
                ('AP005', 'Mi Air Purifier 3', 'Xiaomi', 8990, 'NA', '75 kWh', '["True HEPA", "OLED Display"]',
                 'appliance_images/AP005.jpg', 3, 4),
                ('AP006', 'Blueair Blue 411', 'Blueair', 12990, 'NA', '82 kWh', '["HEPASilent", "Washable Pre-filter"]',
                 'appliance_images/AP006.jpg', 3, 4),
                ('AP007', 'Coway AP-1009CH', 'Coway', 29990, 'NA', '78 kWh', '["Green True HEPA", "Eco Mode"]',
                 'appliance_images/AP007.jpg', 3, 4),
                ('AP008', 'Eureka Forbes Aeroguard AP700', 'Eureka Forbes', 14990, 'NA', '88 kWh',
                 '["5-Stage Purification", "UV LED"]', 'appliance_images/AP008.jpg', 3, 4),
                ('AP009', 'LG PuriCare 360°', 'LG', 27990, 'NA', '83 kWh', '["Dual Inverter", "Circular Airflow"]',
                 'appliance_images/AP009.jpg', 3, 4),
                ('AP010', 'KENT Alps Plus', 'KENT', 16990, 'NA', '87 kWh', '["HEPA+UV", "Smart Sensors"]',
                 'appliance_images/AP010.jpg', 3, 4),


                # Water Heaters
                ('WH001', 'AO Smith HSE-VAS-X-015', 'AO Smith', 12990, '5 Star', '1200 kWh',
                 '["Blue Diamond Tank", "Rust-Free"]', 'appliance_images/WH001.jpg', 3, 5),
                ('WH002', 'Bajaj New Shakti 15L', 'Bajaj', 8990, '4 Star', '1500 kWh',
                 '["PUF Insulation", "Thermostat"]', 'appliance_images/WH002.jpg', 3, 5),
                ('WH003', 'Racold Eterno Pro 15L', 'Racold', 15990, '5 Star', '1100 kWh',
                 '["Glass Lined Tank", "Corrosion-Free"]', 'appliance_images/WH003.jpg', 3, 5),
                ('WH004', 'Havells Instanio 3L', 'Havells', 5990, 'NA', '800 kWh',
                 '["Instant Heating", "Chrome Tank"]', 'appliance_images/WH004.jpg', 3, 5),
                ('WH005', 'V-Guard Victo 15L', 'V-Guard', 10990, '4 Star', '1300 kWh',
                 '["Thermoplastic Inner", "Auto Cut-off"]', 'appliance_images/WH005.jpg', 3, 5),
                ('WH006', 'Crompton Bliss 15L', 'Crompton', 11990, '5 Star', '1150 kWh',
                 '["Advanced Polymer Tank", "Sword Element"]', 'appliance_images/WH006.jpg', 3, 5),
                ('WH007', 'Kenstar Flora 10L', 'Kenstar', 7990, '3 Star', '1400 kWh',
                 '["ABS Body", "Thermostat"]', 'appliance_images/WH007.jpg', 3, 5),
                ('WH008', 'Usha Mist 25L', 'Usha', 14990, '5 Star', '1250 kWh',
                 '["SS Tank", "Auto Thermal Cut-off"]', 'appliance_images/WH008.jpg', 3, 5),
                ('WH009', 'Orient Electric Pronto 10L', 'Orient', 6990, '3 Star', '1350 kWh',
                 '["Corrosion-Resistant", "Thermostat"]', 'appliance_images/WH009.jpg', 3, 5),
                ('WH010', 'Kenmore 15L', 'Kenmore', 16990, '5 Star', '1050 kWh',
                 '["Magnesium Anode", "Auto Cut-off"]', 'appliance_images/WH010.jpg', 3, 5),

                ###################################################################################################################
                # Entertainment
                # Smart TVs
                ('TV001', 'Sony X80K 55" 4K LED', 'Sony', 59990, '3 Star', '150 kWh',
                 '["Android TV", "Dolby Vision"]', 'appliance_images/TV001.jpg', 4, 1),
                ('TV002', 'Samsung CU7000 50" Crystal UHD', 'Samsung', 49990, '2 Star', '180 kWh',
                 '["Smart Hub", "HDR"]', 'appliance_images/TV002.jpg', 4, 1),
                ('TV003', 'LG A2 48" OLED', 'LG', 69990, '4 Star', '120 kWh',
                 '["AI ThinQ", "Dolby Atmos"]', 'appliance_images/TV003.jpg', 4, 1),
                ('TV004', 'OnePlus U1S 55" QLED', 'OnePlus', 44990, '3 Star', '160 kWh',
                 '["Google TV", "HDR10+"]', 'appliance_images/TV004.jpg', 4, 1),
                ('TV005', 'Mi Q1 55" QLED', 'Xiaomi', 39990, '2 Star', '170 kWh',
                 '["PatchWall", "Dolby Vision"]', 'appliance_images/TV005.jpg', 4, 1),
                ('TV006', 'TCL C635 55" QLED', 'TCL', 46990, '3 Star', '155 kWh',
                 '["Google TV", "144Hz"]', 'appliance_images/TV006.jpg', 4, 1),
                ('TV007', 'Vu Masterpiece 55" OLED', 'Vu', 54990, '3 Star', '140 kWh',
                 '["Android TV", "Dolby Vision"]', 'appliance_images/TV007.jpg', 4, 1),
                ('TV008', 'Hisense A6H 50" 4K', 'Hisense', 37990, '2 Star', '165 kWh',
                 '["Vidaa OS", "HDR"]', 'appliance_images/TV008.jpg', 4, 1),
                ('TV009', 'Nokia Stream TV 43"', 'Nokia', 29990, '2 Star', '130 kWh',
                 '["Android TV", "HDR10"]', 'appliance_images/TV009.jpg', 4, 1),
                ('TV010', 'Realme 4K SLED 55"', 'Realme', 42990, '3 Star', '145 kWh',
                 '["Google TV", "Dolby Atmos"]', 'appliance_images/TV010.jpg', 4, 1),

                # Soundbars
                ('SB001', 'Bose 900 Dolby Atmos', 'Bose', 79990, '5 star', '90 kWh',
                 '["Adaptive EQ", "Wi-Fi"]', 'appliance_images/SB001.jpg', 4, 2),
                ('SB002', 'Sony HT-S40R 5.1ch', 'Sony', 24990, '4 star', '60 kWh',
                 '["Dolby Digital", "Bluetooth"]', 'appliance_images/SB002.jpg', 4, 2),
                ('SB003', 'JBL Bar 2.1 Deep Bass', 'JBL', 19990, '4 star', '70 kWh',
                 '["Wireless Subwoofer", "HDMI"]', 'appliance_images/SB003.jpg', 4, 2),
                ('SB004', 'LG SP8YA 3.1.2ch', 'LG', 49990, '5 star', '80 kWh',
                 '["MeriDian", "Dolby Atmos"]', 'appliance_images/SB004.jpg', 4, 2),
                ('SB005', 'Samsung HW-Q600A 3.1.2ch', 'Samsung', 34990, '4 star', '75 kWh',
                 '["DTS:X", "Adaptive Sound"]', 'appliance_images/SB005.jpg', 4, 2),
                ('SB006', 'Philips TAB5305 2.1ch', 'Philips', 12990, '4 star', '50 kWh',
                 '["DTS Sound", "Bluetooth"]', 'appliance_images/SB006.jpg', 4, 2),
                ('SB007', 'Zebronics Zeb-Juke Bar 2.1', 'Zebronics', 5990, '4 star', '45 kWh',
                 '["USB Playback", "Remote"]', 'appliance_images/SB007.jpg', 4, 2),
                ('SB008', 'Boat Aavante 1200D', 'Boat', 9990, '4 star', '55 kWh',
                 '["Dolby Audio", "HDMI ARC"]', 'appliance_images/SB008.jpg', 4, 2),
                ('SB009', 'Mivi Thunder 80W', 'Mivi', 7990, '4 star', '40 kWh',
                 '["Bluetooth 5.0", "Bass Boost"]', 'appliance_images/SB009.jpg', 4, 2),
                ('SB010', 'pTron Boom 2.1', 'pTron', 4990, 'NA', '35 kWh',
                 '["USB/SD", "FM Radio"]', 'appliance_images/SB010.jpg', 4, 2),

                # Smart Speakers
                ('SS001', 'Amazon Echo Dot (4th Gen)', 'Amazon', 4990, '4 star', '15 kWh',
                 '["Alexa", "Bluetooth"]', 'appliance_images/SS001.jpg', 4, 3),
                ('SS002', 'Google Nest Mini (2nd Gen)', 'Google', 4490, '4 star', '12 kWh',
                 '["Google Assistant", "Voice Match"]', 'appliance_images/SS002.jpg', 4, 3),
                ('SS003', 'Apple HomePod mini', 'Apple', 9990, 'NA', '20 kWh',
                 '["Siri", "U1 Chip"]', 'appliance_images/SS003.jpg', 4, 3),
                ('SS004', 'JBL Link 20', 'JBL', 12990, '4 star', '25 kWh',
                 '["Google Assistant", "Portable"]', 'appliance_images/SS004.jpg', 4, 3),
                ('SS005', 'Bose Home Speaker 300', 'Bose', 24990, '5 star', '30 kWh',
                 '["Alexa", "Wi-Fi"]', 'appliance_images/SS005.jpg', 4, 3),
                ('SS006', 'Sony SRS-XB23', 'Sony', 8990, '4 star', '18 kWh',
                 '["Extra Bass", "IP67"]', 'appliance_images/SS006.jpg', 4, 3),
                ('SS007', 'Mi Smart Speaker', 'Xiaomi', 3990, 'NA', '14 kWh',
                 '["Google Assistant", "Bluetooth"]', 'appliance_images/SS007.jpg', 4, 3),
                ('SS008', 'Boat Stone 650', 'Boat', 2990, 'NA', '22 kWh',
                 '["40W RMS", "IPX7"]', 'appliance_images/SS008.jpg', 4, 3),
                ('SS009', 'Realme Smart Speaker', 'Realme', 3490, '4 star', '16 kWh',
                 '["Google Assistant", "Chroma Lights"]', 'appliance_images/SS009.jpg', 4, 3),
                ('SS010', 'iBall Musi Play', 'iBall', 1990, 'NA', '10 kWh',
                 '["Bluetooth", "AUX"]', 'appliance_images/SS010.jpg', 4, 3),

                # Gaming Consoles
                ('GC001', 'Sony PlayStation 5 Digital', 'Sony', 39990, '4 star', '200 kWh',
                 '["825GB SSD", "4K/120Hz"]', 'appliance_images/GC001.jpg', 4, 4),
                ('GC002', 'Microsoft Xbox Series X', 'Microsoft', 49990, '5 star', '180 kWh',
                 '["1TB SSD", "4K/120Hz"]', 'appliance_images/GC002.jpg', 4, 4),
                ('GC003', 'Nintendo Switch OLED', 'Nintendo', 32990, '4 star', '40 kWh',
                 '["7" OLED", "64GB"]', 'appliance_images/GC003.jpg', 4, 4),
                ('GC004', 'Sony PlayStation 4 Slim', 'Sony', 29990, 'NA', '150 kWh',
                 '["1TB HDD", "1080p"]', 'appliance_images/GC004.jpg', 4, 4),
                ('GC005', 'Microsoft Xbox Series S', 'Microsoft', 34990, '4 star', '120 kWh',
                 '["512GB SSD", "1440p"]', 'appliance_images/GC005.jpg', 4, 4),
                ('GC006', 'Nintendo Switch Lite', 'Nintendo', 19990, 'NA', '30 kWh',
                 '["5.5" LCD", "32GB"]', 'appliance_images/GC006.jpg', 4, 4),
                ('GC007', 'Atari VCS 800', 'Atari', 24990, 'NA', '90 kWh',
                 '["AMD Ryzen", "4K"]', 'appliance_images/GC007.jpg', 4, 4),
                ('GC008', 'Steam Deck 64GB', 'Valve', 49990, '4 star', '100 kWh',
                 '["7" Touchscreen", "Zen 2 CPU"]', 'appliance_images/GC008.jpg', 4, 4),
                ('GC009', 'Oculus Quest 2 128GB', 'Meta', 29990, 'NA', '60 kWh',
                 '["VR Headset", "Snapdragon XR2"]', 'appliance_images/GC009.jpg', 4, 4),
                ('GC010', 'RetroN 5 HD', 'Hyperkin', 12990, 'NA', '50 kWh',
                 '["Plays Cartridges", "HDMI"]', 'appliance_images/GC010.jpg', 4, 4),

                ############################################################################################################3
                # Smart Home
                # Security Cameras
                ('SC001', 'TP-Link Tapo C210', 'TP-Link', 3490, '4 star', '10 kWh',
                 '["3MP", "Color Night Vision"]', 'appliance_images/SC001.jpg', 5, 1),
                ('SC002', 'Ezviz C3X', 'Ezviz', 5990, 'NA', '12 kWh',
                 '["360°", "AI Detection"]', 'appliance_images/SC002.jpg', 5, 1),
                ('SC003', 'Mi 360° 2K', 'Xiaomi', 4990, 'NA', '11 kWh',
                 '["2K Resolution", "Starlight Sensor"]', 'appliance_images/SC003.jpg', 5, 1),
                ('SC004', 'Dahua IPC-HDW1239', 'Dahua', 8990, '4 star', '15 kWh',
                 '["PoE", "IP67"]', 'appliance_images/SC004.jpg', 5, 1),
                ('SC005', 'Hikvision DS-2CD2043G0-I', 'Hikvision', 7490, '5 star', '14 kWh',
                 '["4MP", "WDR"]', 'appliance_images/SC005.jpg', 5, 1),
                ('SC006', 'Godrej Security Cam', 'Godrej', 6490, '5 star', '13 kWh',
                 '["1080p", "Motion Detection"]', 'appliance_images/SC006.jpg', 5, 1),
                ('SC007', 'CP Plus 3MP', 'CP Plus', 5490, '4 star', '16 kWh',
                 '["IP66", "Audio Support"]', 'appliance_images/SC007.jpg', 5, 1),
                ('SC008', 'Realme Smart Cam 360', 'Realme', 3990, 'NA', '9 kWh',
                 '["360°", "AI Recognition"]', 'appliance_images/SC008.jpg', 5, 1),
                ('SC009', 'Imou Ranger 2', 'Imou', 4990, '4 star', '10 kWh',
                 '["2K", "Spotlight"]', 'appliance_images/SC009.jpg', 5, 1),
                ('SC010', 'Qubo Smart Cam 360', 'Qubo', 2990, 'NA', '8 kWh',
                 '["1080p", "2-Way Audio"]', 'appliance_images/SC010.jpg', 5, 1),

                # Smart Locks
                ('SL001', 'Yale YDM 7116', 'Yale', 12990, '5 star', '5 kWh',
                 '["Fingerprint", "Bluetooth"]', 'appliance_images/SL001.jpg', 5, 2),
                ('SL002', 'Godrej Locks Secure', 'Godrej', 8990, '4 star', '4 kWh',
                 '["Keypad", "Auto-Lock"]', 'appliance_images/SL002.jpg', 5, 2),
                ('SL003', 'Philips EasyKey', 'Philips', 15990, '5 star', '6 kWh',
                 '["Face Recognition", "App Control"]', 'appliance_images/SL003.jpg', 5, 2),
                ('SL004', 'Havells Solitaire', 'Havells', 11990, '4 star', '5 kWh',
                 '["RFID", "Anti-Panic"]', 'appliance_images/SL004.jpg', 5, 2),
                ('SL005', 'Danalock V3', 'Danalock', 9990, 'NA', '3 kWh',
                 '["Z-Wave", "Auto-Unlock"]', 'appliance_images/SL005.jpg', 5, 2),
                ('SL006', 'August Wi-Fi Smart Lock', 'August', 17990, '4 star', '7 kWh',
                 '["Wi-Fi", "Auto-Lock"]', 'appliance_images/SL006.jpg', 5, 2),
                ('SL007', 'Mi Smart Door Lock', 'Xiaomi', 14990, 'NA', '6 kWh',
                 '["7-in-1 Unlock", "Anti-Peep"]', 'appliance_images/SL007.jpg', 5, 2),
                ('SL008', 'Samsung SHS-P718', 'Samsung', 19990, '4 star', '8 kWh',
                 '["RFID", "Emergency Power"]', 'appliance_images/SL008.jpg', 5, 2),
                ('SL009', 'Ultraloq U-Bolt Pro', 'Ultraloq', 16990, '4 star', '5 kWh',
                 '["Fingerprint", "App Control"]', 'appliance_images/SL009.jpg', 5, 2),
                ('SL010', 'Qubo Smart Lock', 'Qubo', 7990, 'NA', '4 kWh',
                 '["Bluetooth", "Auto-Lock"]', 'appliance_images/SL010.jpg', 5, 2),


                # Smart Thermostats
                ('ST001', 'Google Nest Learning', 'Google', 15990, '4 star', '15 kWh',
                 '["Auto-Schedule", "Farsight"]', 'appliance_images/ST001.jpg', 5, 3),
                ('ST002', 'Honeywell T6 Pro', 'Honeywell', 12990, 'NA', '12 kWh',
                 '["Geofencing", "OpenTherm"]', 'appliance_images/ST002.jpg', 5, 3),
                ('ST003', 'Ecobee SmartThermostat', 'Ecobee', 17990, '5 star', '10 kWh',
                 '["Alexa Built-in", "Room Sensors"]', 'appliance_images/ST003.jpg', 5, 3),
                ('ST004', 'Tado Smart Thermostat', 'Tado', 14990, 'NA', '14 kWh',
                 '["Geofencing", "Weather Adaptation"]', 'appliance_images/ST004.jpg', 5, 3),
                ('ST005', 'Hive Active Heating', 'Hive', 11990, 'NA', '13 kWh',
                 '["App Control", "Boiler Control"]', 'appliance_images/ST005.jpg', 5, 3),
                ('ST006', 'Drayton Wiser', 'Drayton', 9990, 'NA', '11 kWh',
                 '["Multi-Zone", "Smart Scheduling"]', 'appliance_images/ST006.jpg', 5, 3),
                ('ST007', 'Netatmo Smart Thermostat', 'Netatmo', 13990, 'NA', '12 kWh',
                 '["Weather Compensation", "Auto-Assist"]', 'appliance_images/ST007.jpg', 5, 3),
                ('ST008', 'Honeywell Lyric T6', 'Honeywell', 10990, '5 star', '10 kWh',
                 '["Geofencing", "Touchscreen"]', 'appliance_images/ST008.jpg', 5, 3),
                ('ST009', 'Siemens RDE100', 'Siemens', 8990, 'NA', '9 kWh',
                 '["OpenTherm", "Weather Comp"]', 'appliance_images/ST009.jpg', 5, 3),
                ('ST010', 'Salus iT500', 'Salus', 7990, 'NA', '8 kWh',
                 '["Smart Scheduling", "App Control"]', 'appliance_images/ST010.jpg', 5, 3),

                # Smoke Detectors
                ('SD001', 'FireAngel ST-622', 'FireAngel', 2990, '4 star', '2 kWh',
                 '["Wi-Fi", "10-Year Battery"]', 'appliance_images/SD001.jpg', 5, 4),
                ('SD002', 'Kidde KN-COSM-B', 'Kidde', 1990, 'NA', '1.5 kWh',
                 '["CO Detection", "Voice Alarm"]', 'appliance_images/SD002.jpg', 5, 4),
                ('SD003', 'First Alert SCO5CN', 'First Alert', 2490, 'NA', '2.5 kWh',
                 '["Combination Sensor", "Battery Backup"]', 'appliance_images/SD003.jpg', 5, 4),
                ('SD004', 'Nest Protect', 'Google', 5990, '5 star', '3 kWh',
                 '["Split-Spectrum Sensor", "App Alerts"]', 'appliance_images/SD004.jpg', 5, 4),
                ('SD005', 'X-Sense SD03', 'X-Sense', 1790, 'NA', '1.8 kWh',
                 '["Photoelectric", "10-Year Battery"]', 'appliance_images/SD005.jpg', 5, 4),
                ('SD006', 'Ei Electronics Ei650', 'Ei', 3490, 'NA', '2.2 kWh',
                 '["Radio Interconnect", "Hush Button"]', 'appliance_images/SD006.jpg', 5, 4),
                ('SD007', 'Honeywell X-Series', 'Honeywell', 2790, 'NA', '2 kWh',
                 '["Photoelectric", "Test Button"]', 'appliance_images/SD007.jpg', 5, 4),
                ('SD008', 'Aico Ei141', 'Aico', 3990, '5 star', '2.8 kWh',
                 '["RadioLINK", "Optical Sensor"]', 'appliance_images/SD008.jpg', 5, 4),
                ('SD009', 'Heiman HS1SA', 'Heiman', 2290, 'NA', '1.7 kWh',
                 '["Zigbee", "LED Indicator"]', 'appliance_images/SD009.jpg', 5, 4),
                ('SD010', 'Smartwares RM370', 'Smartwares', 1590, 'NA', '1.5 kWh',
                 '["Photoelectric", "10-Year Battery"]', 'appliance_images/SD010.jpg', 5, 4),

                #############################################################################################################33
                # Personal Care
                # Hair Dryers
                ('HD001', 'Dyson Supersonic', 'Dyson', 29900, '5 star', '50 kWh',
                 '["Fast Drying", "Heat Control"]', 'appliance_images/HD001.jpg', 6, 1),
                ('HD002', 'Philips HP8100', 'Philips', 1990, '3 star', '40 kWh',
                 '["Ionic", "Foldable"]', 'appliance_images/HD002.jpg', 6, 1),
                ('HD003', 'Wahl Super Dry', 'Wahl', 2490, '4 star', '45 kWh',
                 '["Ceramic", "2 Speed"]', 'appliance_images/HD003.jpg', 6, 1),
                ('HD004', 'Babyliss Pro 230', 'Babyliss', 3490, '5 star', '55 kWh',
                 '["2000W", "Cold Shot"]', 'appliance_images/HD004.jpg', 6, 1),
                ('HD005', 'Remington D3190', 'Remington', 1790, '3 star', '42 kWh',
                 '["Ceramic", "Diffuser"]', 'appliance_images/HD005.jpg', 6, 1),
                ('HD006', 'Vega Bloom 1000W', 'Vega', 1290, '2 star', '38 kWh',
                 '["Ionic", "Compact"]', 'appliance_images/HD006.jpg', 6, 1),
                ('HD007', 'Nova NHP 1500', 'Nova', 1590, '4 star', '48 kWh',
                 '["Tourmaline", "2 Heat"]', 'appliance_images/HD007.jpg', 6, 1),
                ('HD008', 'Agaro 33000', 'Agaro', 2290, '5 star', '52 kWh',
                 '["Ceramic", "Cool Air"]', 'appliance_images/HD008.jpg', 6, 1),
                ('HD009', 'Panasonic EH-NA65', 'Panasonic', 4990, '4 star', '46 kWh',
                 '["Nanoe", "Dual Voltage"]', 'appliance_images/HD009.jpg', 6, 1),
                ('HD010', 'Havells HD3151', 'Havells', 1890, '3 star', '44 kWh',
                 '["2000W", "Foldable"]', 'appliance_images/HD010.jpg', 6, 1),

                # Electric Shavers
                ('ES0011', 'Philips S9000', 'Philips', 14990, '5 star', '20 kWh',
                 '["Wet&Dry", "Self-Sharpening"]', 'appliance_images/ES0011.jpg', 6, 2),
                ('ES0021', 'Braun Series 7', 'Braun', 12990, '4 star', '18 kWh',
                 '["AutoClean", "5-in-1"]', 'appliance_images/ES0021.jpg', 6, 2),
                ('ES0031', 'Panasonic ES-LT67', 'Panasonic', 8990, '3 star', '15 kWh',
                 '["Multi-Flex", "Linear Motor"]', 'appliance_images/ES0031.jpg', 6, 2),
                ('ES0041', 'Philips OneBlade', 'Philips', 4990, '4 star', '10 kWh',
                 '["Hybrid", "3-in-1"]', 'appliance_images/ES0041.jpg', 6, 2),
                ('ES0051', 'Nova NG-1000', 'Nova', 1990, '2 star', '12 kWh',
                 '["Foil Shaver", "Trimmer"]', 'appliance_images/ES0051.jpg', 6, 2),
                ('ES0061', 'Wahl Lifeproof', 'Wahl', 7990, '5 star', '14 kWh',
                 '["Waterproof", "Self-Sharpening"]', 'appliance_images/ES0061.jpg', 6, 2),
                ('ES0071', 'Remington F5-5800', 'Remington', 5990, '3 star', '16 kWh',
                 '["Flexible Head", "Precision Trimmer"]', 'appliance_images/ES0071.jpg', 6, 2),
                ('ES0081', 'Kemei KM-5018', 'Kemei', 1490, '2 star', '8 kWh',
                 '["3D Floating", "USB Charge"]', 'appliance_images/ES0081.jpg', 6, 2),
                ('ES0091', 'Syska SS101', 'Syska', 2490, '4 star', '11 kWh',
                 '["Foil Shaver", "LED Display"]', 'appliance_images/ES0091.jpg', 6, 2),
                ('ES0101', 'Agaro 37013', 'Agaro', 1790, '3 star', '9 kWh',
                 '["3D Floating", "Washable"]', 'appliance_images/ES0101.jpg', 6, 2),

                # Electric Toothbrushes
                ('ET001', 'Oral-B iO8', 'Oral-B', 12990, '5 star', '10 kWh',
                 '["AI Coaching", "Smart Display"]', 'appliance_images/ET001.jpg', 6, 3),
                ('ET002', 'Philips Sonicare 9900', 'Philips', 14990, '4 star', '12 kWh',
                 '["Pressure Sensor", "3 Modes"]', 'appliance_images/ET002.jpg', 6, 3),
                ('ET003', 'Colgate Hum', 'Colgate', 3990, '3 star', '8 kWh',
                 '["App Connected", "Smart Timer"]', 'appliance_images/ET003.jpg', 6, 3),
                ('ET004', 'Oral-B Pro 1000', 'Oral-B', 2990, '4 star', '7 kWh',
                 '["CrossAction", "2 Min Timer"]', 'appliance_images/ET004.jpg', 6, 3),
                ('ET005', 'Philips Sonicare 4100', 'Philips', 3490, '3 star', '9 kWh',
                 '["2 Modes", "Pressure Sensor"]', 'appliance_images/ET005.jpg', 6, 3),
                ('ET006', 'Foreo Issa 2', 'Foreo', 9990, '5 star', '6 kWh',
                 '["Silicone Bristles", "12 Modes"]', 'appliance_images/ET006.jpg', 6, 3),
                ('ET007', 'Waterpik Sonic-Fusion', 'Waterpik', 8990, '4 star', '11 kWh',
                 '["Flosser+Brush", "2 Modes"]', 'appliance_images/ET007.jpg', 6, 3),
                ('ET008', 'Burst Sonic', 'Burst', 4990, '3 star', '5 kWh',
                 '["Charcoal Bristles", "Whitening"]', 'appliance_images/ET008.jpg', 6, 3),
                ('ET009', 'Quip Electric Toothbrush', 'Quip', 2490, '2 star', '4 kWh',
                 '["Slim Design", "Subscription"]', 'appliance_images/ET009.jpg', 6, 3),
                ('ET010', 'Himalaya Herbals', 'Himalaya', 1790, '4 star', '5 kWh',
                 '["Soft Bristles", "2 Modes"]', 'appliance_images/ET010.jpg', 6, 3),

                #########################################################################################################################3
                # Miscellaneous
                # Treadmills
                ('TM001', 'Cult Sport', 'Cult', 34990, '5 star', '200 kWh',
                 '["2HP Motor", "12 Programs"]', 'appliance_images/TM001.jpg', 7, 1),
                ('TM002', 'PowerMax TDM-100', 'PowerMax', 24990, '4 star', '250 kWh',
                 '["3HP Peak", "Auto Incline"]', 'appliance_images/TM002.jpg', 7, 1),
                ('TM003', 'Sparnod Fitness TR-450', 'Sparnod', 29990, '3 star', '220 kWh',
                 '["16 Programs", "300kg Capacity"]', 'appliance_images/TM003.jpg', 7, 1),
                ('TM004', 'Fitkit FT-440', 'Fitkit', 19990, '4 star', '180 kWh',
                 '["2.5HP", "12 Programs"]', 'appliance_images/TM004.jpg', 7, 1),
                ('TM005', 'Healthgenie 4112', 'Healthgenie', 17990, '3 star', '210 kWh',
                 '["2HP", "Manual Incline"]', 'appliance_images/TM005.jpg', 7, 1),
                ('TM006', 'Proline PTM-100', 'Proline', 22990, '5 star', '230 kWh',
                 '["3HP Peak", "15 Programs"]', 'appliance_images/TM006.jpg', 7, 1),
                ('TM007', 'Kobo TM-09', 'Kobo', 15990, '3 star', '190 kWh',
                 '["2.25HP", "Foldable"]', 'appliance_images/TM007.jpg', 7, 1),
                ('TM008', 'Avon Actium', 'Avon', 27990, '4 star', '240 kWh',
                 '["3.5HP", "Auto Incline"]', 'appliance_images/TM008.jpg', 7, 1),
                ('TM009', 'Tunturi Jog F40', 'Tunturi', 39990, '5 star', '260 kWh',
                 '["4HP", "22 Programs"]', 'appliance_images/TM009.jpg', 7, 1),
                ('TM010', 'NordicTrack T6.5S', 'NordicTrack', 49990, '5 star', '280 kWh',
                 '["3.6CHP", "iFit Compatible"]', 'appliance_images/TM010.jpg', 7, 1),

                # Air Compressors
                ('AC0011', 'Elgi 2HP', 'Elgi', 14990, '5 star', '300 kWh',
                 '["50L Tank", "Oil-Free"]', 'appliance_images/AC0011.jpg', 7, 2),
                ('AC0021', 'Hitachi EC28M', 'Hitachi', 12990, '4 star', '280 kWh',
                 '["1HP", "Direct Drive"]', 'appliance_images/AC0021.jpg', 7, 2),
                ('AC0031', 'Bosch GAS 18V-2', 'Bosch', 17990, '3 star', '250 kWh',
                 '["Portable", "2 Gallon"]', 'appliance_images/AC0031.jpg', 7, 2),
                ('AC0041', 'Ingersoll Rand SS3', 'Ingersoll Rand', 29990, '5 star', '350 kWh',
                 '["3HP", "60L Tank"]', 'appliance_images/AC0041.jpg', 7, 2),
                ('AC0051', 'Black+Decker BDPC200', 'Black+Decker', 9990, '3 star', '220 kWh',
                 '["2HP", "6L Tank"]', 'appliance_images/AC0051.jpg', 7, 2),
                ('AC0061', 'Makita MAC700', 'Makita', 24990, '5 star', '320 kWh',
                 '["2HP", "Oil Lubricated"]', 'appliance_images/AC0061.jpg', 7, 2),
                ('AC0071', 'Rolair VT25BIG', 'Rolair', 19990, '4 star', '290 kWh',
                 '["2.5HP", "Portable"]', 'appliance_images/AC0071.jpg', 7, 2),
                ('AC0081', 'Campbell Hausfeld DC080500', 'Campbell Hausfeld', 11990, '4 star', '270 kWh',
                 '["1HP", "8 Gallon"]', 'appliance_images/AC0081.jpg', 7, 2),
                ('AC0091', 'Porter-Cable C2002', 'Porter-Cable', 13990, '3 star', '310 kWh',
                 '["1.5HP", "6 Gallon"]', 'appliance_images/AC0091.jpg', 7, 2),
                ('AC0101', 'DeWalt DWFP55126', 'DeWalt', 16990, '5 star', '330 kWh',
                 '["2HP", "6 Gallon"]', 'appliance_images/AC0101.jpg', 7, 2),

                # Water Softeners
                ('WS001', 'Kent Supreme Plus', 'Kent', 24990, '5 star', '50 kWh',
                 '["Ion Exchange", "25L Capacity"]', 'appliance_images/WS001.jpg', 7, 3),
                ('WS002', 'Aquaguard Protect+', 'Aquaguard', 27990, '4 star', '45 kWh',
                 '["Smart Alert", "30L Capacity"]', 'appliance_images/WS002.jpg', 7, 3),
                ('WS003', 'Pureit Advanced', 'Pureit', 22990, '4 star', '55 kWh',
                 '["Auto Flush", "20L Capacity"]', 'appliance_images/WS003.jpg', 7, 3),
                ('WS004', 'HUL Pureit Ultima', 'HUL', 19990, '3 star', '60 kWh',
                 '["UV+UF", "15L Capacity"]', 'appliance_images/WS004.jpg', 7, 3),
                ('WS005', 'Livpure Glo', 'Livpure', 25990, '4 star', '48 kWh',
                 '["RO+UV", "8L Storage"]', 'appliance_images/WS005.jpg', 7, 3),
                ('WS006', 'AO Smith Z8', 'AO Smith', 29990, '5 star', '42 kWh',
                 '["Digital Display", "Side Stream"]', 'appliance_images/WS006.jpg', 7, 3),
                ('WS007', 'Eureka Forbes Aquasure', 'Eureka Forbes', 21990, '3 star', '52 kWh',
                 '["TDS Controller", "10L Storage"]', 'appliance_images/WS007.jpg', 7, 3),
                ('WS008', 'Whirlpool Marvel', 'Whirlpool', 26990, '4 star', '47 kWh',
                 '["6-Stage Purification", "7L Storage"]', 'appliance_images/WS008.jpg', 7, 3),
                ('WS009', 'LG PuriCare', 'LG', 23990, '4 star', '53 kWh',
                 '["UV Nano", "8L Storage"]', 'appliance_images/WS009.jpg', 7, 3),
                ('WS010', 'KENT Grand Plus', 'KENT', 28990, '5 star', '44 kWh',
                 '["RO+UV+UF", "12L Storage"]', 'appliance_images/WS010.jpg', 7, 3),

            ]
            # Insert sample appliances for each subcategory
            cursor.executemany('''
                        INSERT OR IGNORE INTO appliances 
                        (id, name, brand, price, energy_rating, annual_consumption, features, image_url, category_id, subcategory_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', sample_appliances)

            db.commit()


# Initialize database
init_db()

# Energy data
ENERGY_DATA = {
    "price_per_kwh": 7.50,
    "carbon_intensity": 280,
    "last_updated": datetime.now().strftime("%Y-%m-%d")
}


# Recommendation algorithm
def recommend_appliances(category_id=None, subcategory_id=None, budget=50000, eco_priority=0.5):
    """AI recommendation engine using database"""
    with closing(sqlite3.connect('../appliances.db')) as db:
        cursor = db.cursor()

        # Base query with proper filtering logic
        query = '''
        SELECT a.*, c.name as category_name, s.name as subcategory_name 
        FROM appliances a
        JOIN categories c ON a.category_id = c.id
        JOIN subcategories s ON a.subcategory_id = s.id
        WHERE a.price <= ?
        '''
        params = [budget]

        # Add filters if provided
        if subcategory_id:
            # If subcategory is specified, only filter by that
            query += ' AND a.subcategory_id = ?'
            params.append(subcategory_id)
        elif category_id:
            # If only category is specified, filter by category
            query += ' AND a.category_id = ?'
            params.append(category_id)

        # Execute query
        cursor.execute(query, params)
        products = []
        for row in cursor.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "brand": row[2],
                "price": row[3],
                "energy_rating": row[4],
                "annual_consumption": row[5],
                "features": eval(row[6]),
                "image_url": row[7],
                "category_id": row[8],
                "subcategory_id": row[9],
                "category_name": row[10],
                "subcategory_name": row[11]
            })

        # Score products
        for product in products:
            rating = product['energy_rating']
            if '5 Star' in rating:
                energy_score = 5
            elif '4 Star' in rating:
                energy_score = 4
            elif '3 Star' in rating:
                energy_score = 3
            elif 'NA' in rating:
                energy_score = 2  # Default score for NA ratings
            else:
                energy_score = 1

            price_score = 1 - min(product['price'] / budget, 1)
            product['score'] = (energy_score * eco_priority) + (price_score * (1 - eco_priority))

        products.sort(key=lambda x: x['score'], reverse=True)

        # Eco picks include highly efficient appliances or those with low consumption
        eco_picks = [
            p for p in products
            if ('5 Star' in p['energy_rating'] or
               (p.get('annual_consumption') and
                float(p['annual_consumption'].replace(' kWh', '')) < 200))
        ][:3]

        return {
            "recommendations": products[:50],
            "eco_picks": eco_picks
        }

# Routes



@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
@app.route('/appliance_images/<filename>')
def serve_appliance_image(filename):
    return send_from_directory('appliance_images', filename)


@app.route('/api/categories')
def get_categories():
    with closing(sqlite3.connect('../appliances.db')) as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, name FROM categories')
        categories = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        return jsonify(categories)


@app.route('/api/subcategories/<int:category_id>')
def get_subcategories(category_id):
    with closing(sqlite3.connect('../appliances.db')) as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, name FROM subcategories WHERE category_id = ?', (category_id,))
        subcategories = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        return jsonify(subcategories)


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    preferences = request.json
    results = recommend_appliances(
        preferences.get('category_id'),
        preferences.get('subcategory_id'),
        float(preferences.get('budget', 50000)),
        float(preferences.get('eco_priority', 0.5))
    )

    for product in results['recommendations'] + results['eco_picks']:
        if product.get('annual_consumption'):
            product['annual_cost'] = calculate_annual_cost(
                product['annual_consumption'],
                ENERGY_DATA['price_per_kwh']
            )

    return jsonify({
        **results,
        "energy_data": ENERGY_DATA
    })


def calculate_annual_cost(consumption, price_per_kwh):
    try:
        kwh = float(consumption.replace(' kWh', ''))
        return f"₹{(kwh * price_per_kwh):.2f}"
    except:
        return "N/A"


# HTML Template remains the same
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EcoSmart Appliance Finder</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    <style>
        :root {
            --primary-green: #27ae60;
            --secondary-green: #2ecc71;
            --dark-green: #16a085;
            --light-bg: #f8f9fa;
        }
        
        body {
            background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
                        url('https://images.unsplash.com/photo-1476231682828-37e571bc172f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="%2327ae60" d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10-4.48,10-10S17.52,2,12,2z M12,20c-4.42,0-8-3.58-8-8s3.58-8,8-8s8,3.58,8,8S16.42,20,12,20z"/></svg>'), auto;
            overflow-x: hidden;
        }
        
        /* Leaf animation elements */
        .leaf {
            position: absolute;
            width: 30px;
            height: 30px;
            background-size: contain;
            background-repeat: no-repeat;
            pointer-events: none;
            z-index: 1000;
            animation: fall linear forwards;
        }
        
        @keyframes fall {
            to {
                transform: translate(var(--end-x), var(--end-y)) rotate(var(--end-rot));
                opacity: 0;
            }
        }
        
        /* Rest of your existing styles... */
        .container {
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }
        
        .energy-badge {
            background: var(--primary-green); 
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
            position: absolute;
            top: 15px;
            left: 15px;
            z-index: 2;
            font-weight: 600;
            font-size: 0.85rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .appliance-card { 
            transition: all 0.3s ease; 
            border: none;
            overflow: hidden;
            border-radius: 12px !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            background: rgba(255,255,255,0.95);
        }
        
        .appliance-card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 12px 25px rgba(46, 204, 113, 0.15);
        }
        
        .appliance-img { 
            height: 180px; 
            object-fit: contain;
            padding: 30px;
            background-color: rgba(255,255,255,0.9);
            mix-blend-mode: multiply;
        }
        
        h1, h2, h3, h4, h5 {
            color: #2c3e50;
            font-weight: 700;
        }
        
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            background: rgba(255,255,255,0.95);
            overflow: hidden;
        }
        
        .card-body {
            padding: 1.5rem;
        }
        
        .btn-primary {
            background-color: var(--primary-green);
            border-color: var(--primary-green);
            padding: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .btn-primary:hover {
            background-color: var(--dark-green);
            border-color: var(--dark-green);
            transform: translateY(-2px);
        }
        
        .text-primary {
            color: var(--primary-green) !important;
        }
        
        .form-range::-webkit-slider-thumb {
            background: var(--primary-green);
            width: 20px;
            height: 20px;
        }
        
        .form-range::-moz-range-thumb {
            background: var(--primary-green);
        }
        
        .form-control, .form-select {
            border-radius: 8px;
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--secondary-green);
            box-shadow: 0 0 0 0.25rem rgba(46, 204, 113, 0.25);
        }
        
        .form-range {
            height: 8px;
        }
        
        .form-range::-webkit-slider-runnable-track {
            background: #e0e0e0;
            height: 6px;
            border-radius: 3px;
        }
        
        .form-range::-moz-range-track {
            background: #e0e0e0;
            height: 6px;
            border-radius: 3px;
        }
        
        .header-icon {
            color: var(--primary-green);
            margin-right: 10px;
        }
        
        .feature-list li {
            margin-bottom: 0.5rem;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .feature-list li:before {
            content: "\f00c";
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            position: absolute;
            left: 0;
            color: var(--secondary-green);
        }
        
        .text-success {
            color: var(--primary-green) !important;
        }
        
        .loading-spinner {
            color: var(--primary-green);
        }
        
        .no-results-icon {
            color: var(--primary-green);
        }
        
        .error-icon {
            color: #e74c3c;
        }
        
        .price-display {
            font-weight: 700;
            margin: 1rem 0;
        }
        
        .brand-text {
            color: #7f8c8d;
            font-weight: 500;
        }
        
        .annual-cost {
            background: #e8f8f0;
            padding: 0.5rem;
            border-radius: 6px;
            display: inline-block;
            font-weight: 600;
        }
        
        .subcategory-badge {
            background: #ecf0f1;
            color: #7f8c8d;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.75rem;
            margin-bottom: 1rem;
        }
        
        @media (max-width: 768px) {
            .appliance-img {
                height: 150px;
                padding: 20px;
            }
            
            .energy-badge {
                top: 10px;
                left: 10px;
                font-size: 0.75rem;
                padding: 0.2rem 0.6rem;
            }
        }
    </style>
</head>
<body>
    <div class="container py-4">
        <h1 class="text-center mb-4">
            <i class="fas fa-leaf header-icon"></i> EcoSmart Appliance Finder
        </h1>

        <!-- Search Form -->
        <div class="card mb-4">
            <div class="card-body">
                <h2 class="h4 mb-4"><i class="fas fa-search header-icon"></i> Find Your Perfect Appliance</h2>
                <form id="search-form">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Category</label>
                            <select id="category" class="form-select">
                                <option value="">All Categories</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Subcategory</label>
                            <select id="subcategory" class="form-select" disabled>
                                <option value="">All Subcategories</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Max Budget (₹)</label>
                            <input type="number" id="budget" class="form-control" value="30000">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Eco Priority</label>
                            <input type="range" class="form-range" id="eco-priority" min="0" max="100" value="50">
                            <div class="d-flex justify-content-between">
                                <small>Price Focus</small>
                                <small id="eco-value">Balanced</small>
                                <small>Eco Focus</small>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary mt-3 w-100">
                        <i class="fas fa-search"></i> Find Recommendations
                    </button>
                </form>
            </div>
        </div>

        <!-- Energy Info -->
        <div class="card mb-4">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h3><i class="fas fa-bolt header-icon"></i> Energy Information</h3>
                        <p>Current electricity rate: <strong id="energy-price">₹7.50/kWh</strong></p>
                        <p>Carbon intensity: <span id="carbon-value">280</span> gCO₂/kWh</p>
                    </div>
                    <div class="col-md-6">
                        <h3><i class="fas fa-lightbulb header-icon"></i> Did You Know?</h3>
                        <p id="energy-tip">5-star appliances can save 30% energy compared to 3-star models</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Top Eco Picks -->
        <div class="card mb-4">
            <div class="card-body">
                <h2 class="card-title"><i class="fas fa-leaf header-icon"></i> Top Eco Picks</h2>
                <p class="text-muted mb-4">Our highest rated energy-efficient appliances</p>
                <div id="eco-picks" class="row row-cols-1 row-cols-md-3 g-4"></div>
            </div>
        </div>

        <!-- Recommendations -->
        <div class="card">
            <div class="card-body">
                <h2 class="card-title"><i class="fas fa-star header-icon"></i> Recommended Appliances</h2>
                <p class="text-muted mb-4">Personalized recommendations based on your preferences</p>
                <div id="results" class="row row-cols-1 row-cols-md-3 g-4">
                    <div class="col-12 text-center py-5 text-muted">
                        <i class="fas fa-search fa-3x mb-3 no-results-icon"></i>
                        <h4>Find Your Perfect Appliance</h4>
                        <p>Use the search form above to get recommendations</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Leaf images (using emoji as background images)
        const leafImages = [
            '🌿', '🍃', '🍀', '🌱', '🌲', '🌳', '🌴', '🌵', '🌾', '🌿', '🍂', '🍁', '🌻', '🌼', '🌸', '🌺', '💐', '🪴', '🌍'
        ];
        
        // Create leaf elements
        function createLeaves(x, y) {
            const leafCount = 12 + Math.floor(Math.random() * 10);
            
            for (let i = 0; i < leafCount; i++) {
                const leaf = document.createElement('div');
                leaf.className = 'leaf';
                leaf.innerHTML = leafImages[Math.floor(Math.random() * leafImages.length)];
                
                // Random size
                const size = 20 + Math.random() * 20;
                leaf.style.fontSize = `${size}px`;
                
                // Starting position (click position)
                leaf.style.left = `${x}px`;
                leaf.style.top = `${y}px`;
                
                // Random animation end position
                const angle = Math.random() * Math.PI * 2;
                const distance = 100 + Math.random() * 150;
                const endX = Math.cos(angle) * distance;
                const endY = Math.sin(angle) * distance + 100;
                
                // Random rotation
                const startRot = Math.random() * 360;
                const endRot = startRot + (Math.random() * 360 - 180);
                
                // Set CSS variables for animation
                leaf.style.setProperty('--end-x', `${endX}px`);
                leaf.style.setProperty('--end-y', `${endY}px`);
                leaf.style.setProperty('--end-rot', `${endRot}deg`);
                
                // Random animation duration
                const duration = 1 + Math.random() * 2;
                leaf.style.animationDuration = `${duration}s`;
                
                document.body.appendChild(leaf);
                
                // Remove leaf after animation completes
                setTimeout(() => {
                    leaf.remove();
                }, duration * 1000);
            }
        }
        
        // Click event listener for leaf effect
        document.addEventListener('click', function(e) {
            createLeaves(e.clientX, e.clientY);
        });

        // Energy tips
        const tips = [
            "5-star ACs use 30% less power than 3-star models",
            "Front-load washers save 50% more water than top-load",
            "LED TVs consume 50% less energy than plasma TVs",
            "Inverter refrigerators save 20-30% more energy",
            "Energy Star certified appliances meet strict efficiency guidelines",
            "Smart thermostats can save 10-12% on heating and cooling costs",
            "Using cold water for laundry saves 90% of the energy used for heating water",
            "Unplugging electronics when not in use can save 5-10% on your electricity bill"
        ];

        document.addEventListener('DOMContentLoaded', function() {
            // Set random tip
            document.getElementById('energy-tip').textContent =
                tips[Math.floor(Math.random() * tips.length)];

            // Load categories
            fetch('/api/categories')
                .then(response => response.json())
                .then(categories => {
                    const select = document.getElementById('category');
                    categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category.id;
                        option.textContent = category.name;
                        select.appendChild(option);
                    });
                });

            // When category changes, load subcategories
document.getElementById('category').addEventListener('change', function() {
    const categoryId = this.value;
    const subcategorySelect = document.getElementById('subcategory');

    // Reset subcategory dropdown
    subcategorySelect.innerHTML = '<option value="">All Subcategories</option>';
    subcategorySelect.disabled = true;

    if (categoryId) {
        subcategorySelect.disabled = false;
        fetch(`/api/subcategories/${categoryId}`)
            .then(response => response.json())
            .then(subcategories => {
                // Add new options only for defined subcategories
                subcategories.forEach(subcategory => {
                    const option = document.createElement('option');
                    option.value = subcategory.id;
                    option.textContent = subcategory.name;
                    subcategorySelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading subcategories:', error);
            });
    }
});

            // Update eco priority display
            document.getElementById('eco-priority').addEventListener('input', function() {
                const value = parseInt(this.value);
                const display = document.getElementById('eco-value');

                if (value < 30) {
                    display.textContent = 'Price Focus';
                    display.style.color = '#3498db';
                } else if (value > 70) {
                    display.textContent = 'Eco Focus';
                    display.style.color = '#27ae60';
                } else {
                    display.textContent = 'Balanced';
                    display.style.color = '#9b59b6';
                }
            });

            // Form submission
            document.getElementById('search-form').addEventListener('submit', function(e) {
                e.preventDefault();

                const categoryId = document.getElementById('category').value || null;
                const subcategoryId = document.getElementById('subcategory').value || null;
                const budget = document.getElementById('budget').value;
                const ecoPriority = document.getElementById('eco-priority').value / 100;

                // Show loading state
                document.getElementById('results').innerHTML = `
                    <div class="col-12 text-center py-5">
                        <div class="spinner-border loading-spinner" style="width: 3rem; height: 3rem;"></div>
                        <p class="mt-3">Finding energy-efficient options...</p>
                    </div>
                `;

                fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        category_id: categoryId,
                        subcategory_id: subcategoryId,
                        budget: parseFloat(budget),
                        eco_priority: parseFloat(ecoPriority)
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // Update energy info
                    document.getElementById('energy-price').textContent =
                        `₹${data.energy_data.price_per_kwh}/kWh`;
                    document.getElementById('carbon-value').textContent =
                        data.energy_data.carbon_intensity;

                    // Display eco picks
                    let ecoHtml = '';
                    if (data.eco_picks && data.eco_picks.length > 0) {
                        data.eco_picks.forEach(product => {
                            ecoHtml += `
                                <div class="col">
                                    <div class="card h-100 appliance-card">
                                        <div class="position-relative">
                                            <div class="energy-badge">${product.energy_rating}</div>
                                            <img src="${product.image_url}" class="card-img-top appliance-img">
                                        </div>
                                        <div class="card-body">
                                            <h5 class="mb-2">${product.name}</h5>
                                            <p class="brand-text mb-2">${product.brand}</p>
                                            <div class="price-display text-primary">₹${product.price.toLocaleString('en-IN')}</div>
                                            ${product.annual_cost ? `<p class="annual-cost"><i class="fas fa-rupee-sign"></i> ${product.annual_cost}/year</p>` : ''}
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                    } else {
                        ecoHtml = '<div class="col-12 text-center py-5 text-muted"><i class="fas fa-leaf fa-3x mb-3 no-results-icon"></i><h4>No eco picks found</h4><p>Try adjusting your filters</p></div>';
                    }
                    document.getElementById('eco-picks').innerHTML = ecoHtml;

                    // Display recommendations
                    let resultsHtml = '';
                    if (data.recommendations && data.recommendations.length > 0) {
                        data.recommendations.forEach(product => {
                            resultsHtml += `
                                <div class="col">
                                    <div class="card h-100 appliance-card">
                                        <div class="position-relative">
                                            <div class="energy-badge">${product.energy_rating}</div>
                                            <img src="${product.image_url}" class="card-img-top appliance-img">
                                        </div>
                                        <div class="card-body">
                                            <h5 class="mb-2">${product.name}</h5>
                                            <p class="brand-text mb-2">${product.brand}</p>
                                            <div class="price-display text-primary">₹${product.price.toLocaleString('en-IN')}</div>
                                            ${product.annual_cost ? `<p class="annual-cost mb-3"><i class="fas fa-rupee-sign"></i> ${product.annual_cost}/year</p>` : ''}
                                            <span class="subcategory-badge">${product.subcategory_name}</span>
                                            <ul class="feature-list mt-3 ps-0">
                                                ${product.features.map(f => `<li>${f}</li>`).join('')}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                    } else {
                        resultsHtml = `
                            <div class="col-12 text-center py-5">
                                <i class="fas fa-exclamation-triangle fa-3x no-results-icon mb-3"></i>
                                <h4 class="mt-3">No appliances found</h4>
                                <p>Try adjusting your budget or filters</p>
                            </div>
                        `;
                    }
                    document.getElementById('results').innerHTML = resultsHtml;
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = `
                        <div class="col-12 text-center py-5">
                            <i class="fas fa-exclamation-circle fa-3x error-icon mb-3"></i>
                            <h4 class="mt-3">Error loading recommendations</h4>
                            <p>Please try again later</p>
                        </div>
                    `;
                    console.error('Error:', error);
                });
            });
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5000)