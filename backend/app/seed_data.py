import json
import uuid
from datetime import datetime, timezone
from app.database import get_db, init_db
from app.auth import hash_password

def seed_database():
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT id FROM admin_users WHERE username = 'admin'")
        if not cursor.fetchone():
            now = datetime.now(timezone.utc).isoformat()
            p_hash, salt = hash_password("AdminPassword2026!")
            cursor.execute("""
                INSERT INTO admin_users (id, username, password_hash, salt, full_name, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), "admin", p_hash, salt, "LIPTIS Travel Administrator", "admin", now))
            print("Default admin created: username='admin', password='AdminPassword2026!'")

        # Check if event already exists
        cursor.execute("SELECT id FROM events WHERE id = 'liptis-saudi-2026'")
        if cursor.fetchone():
            print("Database already contains the authoritative LIPTIS event data.")
            return

        now = datetime.now(timezone.utc).isoformat()
        event_id = "liptis-saudi-2026"

        # 1. Insert Main Event
        cursor.execute("""
            INSERT INTO events (id, title, subtitle, destination, start_date, end_date, date_display, status, has_unpublished_changes, is_active, created_at, updated_at, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'published', 0, 1, ?, ?, ?)
        """, (
            event_id,
            "Exclusive Event for Eminent Physicians",
            "Welcome to Saudi Arabia",
            "Rotana Jabal Omar Hotel, Mecca & Peninsula Worth Hotel Madinah",
            "2026-10-15",
            "2026-10-18",
            "15-18 October 2026",
            now, now, now
        ))

        # 2. Insert 2 Flight Groups (authoritative from PDF Page 6 variations)
        fg1_id = "flight-group-xy566"
        fg2_id = "flight-group-xy584"

        cursor.execute("""
            INSERT INTO flight_groups (
                id, event_id, name, airline, outbound_flight_number, departure_airport,
                departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                return_flight_number, return_departure_airport, return_departure_date,
                return_departure_time, return_arrival_airport, return_arrival_date,
                return_arrival_time, notes, display_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fg1_id, event_id,
            "Flight Group 1 (Flynas XY 566)",
            "Flynas", "XY 566",
            "Cairo International Airport, Terminal 1",
            "2026-10-15", "09:25 AM",
            "King Abdulaziz International Airport, Jeddah",
            "2026-10-15", "11:50 AM",
            "XY 576",
            "Prince Mohammad Bin Abdulaziz International Airport, Madinah",
            "2026-10-18", "09:15 PM",
            "Cairo International Airport, Terminal 1",
            "2026-10-18", "11:45 PM",
            "Early morning flight. Gathering at Cairo Terminal 1 at 06:00 AM.",
            1, now, now
        ))

        cursor.execute("""
            INSERT INTO flight_groups (
                id, event_id, name, airline, outbound_flight_number, departure_airport,
                departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                return_flight_number, return_departure_airport, return_departure_date,
                return_departure_time, return_arrival_airport, return_arrival_date,
                return_arrival_time, notes, display_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fg2_id, event_id,
            "Flight Group 2 (Flynas XY 584)",
            "Flynas", "XY 584",
            "Cairo International Airport, Terminal 1",
            "2026-10-15", "10:20 AM",
            "King Abdulaziz International Airport, Jeddah",
            "2026-10-15", "12:45 PM",
            "XY 576",
            "Prince Mohammad Bin Abdulaziz International Airport, Madinah",
            "2026-10-18", "09:15 PM",
            "Cairo International Airport, Terminal 1",
            "2026-10-18", "11:45 PM",
            "Mid-morning flight. Gathering at Cairo Terminal 1 at 07:00 AM.",
            2, now, now
        ))

        # 3. Insert Itineraries
        # Day 1: Thursday, 15 Oct. 2026
        # --- Group 1 specific ---
        d1_g1_entries = [
            ("6:00 AM", None, "Gathering at Cairo International Airport, Terminal 1", "Cairo Airport Terminal 1", "Meeting at Terminal 1 departures hall; flight to Jeddah at 09:25 AM", "flight", "LIPTIS departure assistance desk", 1, fg1_id),
            ("9:25 AM", "11:50 AM", "Departure time of Flight, (Flynas XY 566), to Jeddah", "Airspace / En Route", "Direct flight from Cairo to Jeddah King Abdulaziz International Airport", "flight", None, 2, fg1_id),
            ("11:50 AM", None, "Arrival at Jeddah King Abdulaziz International Airport", "King Abdulaziz Int. Airport, Jeddah", "Landing and baggage claim at Jeddah", "flight", None, 3, fg1_id),
            ("12:00 PM", "2:00 PM", "Meet and assist at Jeddah King Abdulaziz International Airport", "Arrival Hall", "A representative holding a LIPTIS welcome sign will be waiting at the arrival hall to assist with the transfer to the hotel in Mecca.", "transfer", "Arrival Hall - LIPTIS Sign", 4, fg1_id),
            ("2:00 PM", "4:00 PM", "Transfer to Makkah and check in at Rotana Jabal Omar Hotel", "Rotana Jabal Omar Hotel, Mecca", "Transfer time is approximately 90 minutes by bus. Check in and room keys distribution (stay until 17/10/2026).", "hotel", "Hotel Lobby", 5, fg1_id),
        ]

        # --- Group 2 specific ---
        d1_g2_entries = [
            ("7:00 AM", None, "Gathering at Cairo International Airport, Terminal 1", "Cairo Airport Terminal 1", "Meeting at Terminal 1 departures hall; flight to Jeddah at 10:20 AM", "flight", "LIPTIS departure assistance desk", 1, fg2_id),
            ("10:20 AM", "12:45 PM", "Departure time of Flight, (Flynas XY 584), to Jeddah", "Airspace / En Route", "Direct flight from Cairo to Jeddah King Abdulaziz International Airport", "flight", None, 2, fg2_id),
            ("12:45 PM", None, "Arrival at Jeddah King Abdulaziz International Airport", "King Abdulaziz Int. Airport, Jeddah", "Landing and baggage claim at Jeddah", "flight", None, 3, fg2_id),
            ("12:45 PM", "3:00 PM", "Meet and assist at Jeddah King Abdulaziz International Airport", "Arrival Hall", "A representative holding a LIPTIS welcome sign will be waiting at the arrival hall to assist with the transfer to the hotel in Mecca.", "transfer", "Arrival Hall - LIPTIS Sign", 4, fg2_id),
            ("3:00 PM", "5:00 PM", "Transfer to Makkah and check in at Rotana Jabal Omar Hotel", "Rotana Jabal Omar Hotel, Mecca", "Transfer time is approximately 90 minutes by bus. Check in and room keys distribution (stay until 17/10/2026).", "hotel", "Hotel Lobby", 5, fg2_id),
        ]

        # Day 1 Shared
        d1_shared_entries = [
            ("6:30 PM", "10:30 PM", "Dinner at Rotana Jabal Omar Hotel", "Rotana Jabal Omar Hotel, El-Rayan Restaurant", "Welcome dinner for all delegates at El-Rayan Restaurant on the 1st floor", "meal", "El-Rayan Restaurant, 1st Floor", 10, None),
        ]

        # Day 2: Friday, 16 Oct. 2026 (Shared)
        d2_entries = [
            ("6:30 AM", "9:30 AM", "Breakfast at Rotana Jabal Omar Hotel", "El-Rayan Restaurant, 1st Floor", "Buffet breakfast", "meal", "El-Rayan Restaurant", 1, None),
            ("9:30 AM", "11:00 AM", "LIPTIS Symposium", "Al Farouk Hall, Ground Floor", "LIPTIS exclusive symposium for eminent physicians", "symposium", "Al Farouk Hall entrance", 2, None),
            ("11:00 AM", "6:30 PM", "Free time (Umrah & Prayers)", "Masjid al-Haram, Mecca", "Personal worship, Umrah rituals, Friday prayer, and leisure", "prayer", None, 3, None),
            ("6:30 PM", "10:30 PM", "Dinner at Rotana Jabal Omar Hotel", "El-Rayan Restaurant, 1st Floor", "Evening dinner", "meal", "El-Rayan Restaurant", 4, None),
        ]

        # Day 3: Saturday, 17 Oct. 2026 (Shared)
        d3_entries = [
            ("6:30 AM", "10:30 AM", "Breakfast at Rotana Jabal Omar Hotel", "El-Rayan Restaurant, 1st Floor", "Buffet breakfast", "meal", "El-Rayan Restaurant", 1, None),
            ("10:30 AM", "12:00 PM", "Check-out", "Rotana Jabal Omar Hotel Lobby", "Hotel check-out and luggage collection", "hotel", "Hotel Lobby", 2, None),
            ("12:00 PM", None, "Buses transfer to Haramain High-Speed Railway Station", "Makkah Railway Station", "Luggage loading and private bus transfer to Makkah Station", "transfer", "Hotel Main Gate", 3, None),
            ("2:20 PM", "4:35 PM", "Haramain High-Speed Train No. 03142 to Madinah", "Haramain High-Speed Railway", "Train No. 03142 scheduled to depart at 2:20 PM, arriving at Al-Madinah Al-Munawwarah at 4:35 PM", "transfer", "Makkah Station Train Platform", 4, None),
            ("4:35 PM", "5:00 PM", "Meet and assist at Haramain Railway Station", "Madinah Railway Station", "Meet and assist upon arrival at Madinah Station", "transfer", "Station Arrival Concourse", 5, None),
            ("5:00 PM", "5:30 PM", "Transfer and check-in at Peninsula Worth Hotel", "Peninsula Worth Hotel, Madinah", "Bus transfer and check-in at Peninsula Worth Hotel Madinah", "hotel", "Hotel Front Desk", 6, None),
            ("6:30 PM", "10:30 PM", "Dinner at Peninsula Worth Hotel", "Main Restaurant, R Floor", "Dinner at Peninsula Worth Hotel Main Restaurant on the R floor", "meal", "Main Restaurant (R Floor)", 7, None),
        ]

        # Day 4: Sunday, 18 Oct. 2026 (Shared)
        d4_entries = [
            ("6:30 AM", "10:30 AM", "Breakfast at Peninsula Worth Hotel", "Main Restaurant, R Floor", "Buffet breakfast", "meal", "Main Restaurant (R Floor)", 1, None),
            ("10:30 AM", "1:00 PM", "Free Time and Dhuhr Prayer", "Al-Masjid an-Nabawi", "Prayers at the Prophet's Mosque and personal time", "prayer", None, 2, None),
            ("1:00 PM", "1:30 PM", "Check-out", "Peninsula Worth Hotel Lobby", "Hotel check-out and luggage loading into transfer coaches", "hotel", "Hotel Lobby", 3, None),
            ("1:30 PM", "3:30 PM", "Visiting International Fairs & Museums of the Prophet's Biography", "Madinah Cultural Center", "Guided cultural visit to the International Fairs and Museums of the Prophet’s Biography and Islamic Civilization", "culture", "Museum Entrance", 4, None),
            ("3:30 PM", None, "Buses depart to Prince Mohammad Bin Abdulaziz International Airport", "Madinah Airport (MED)", "Luggage loading and departure to airport for return flight Flynas XY 576", "transfer", "Museum Parking / Buses", 5, None),
            ("7:40 PM", None, "Boarding & Departure Gathering at Madinah Airport", "Prince Mohammad Bin Abdulaziz International Airport", "Airport check-in, baggage drop, and immigration procedures", "flight", "Departure Terminal Desk", 6, None),
            ("9:15 PM", "11:45 PM", "Departure Time to Cairo (Flight Flynas XY 576)", "En Route to Cairo", "Return flight to Cairo International Airport; approximate arrival 11:45 PM", "flight", "Boarding Gate", 7, None),
        ]

        for item in d1_g1_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-15', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        for item in d1_g2_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-15', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        for item in d1_shared_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-15', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        for item in d2_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-16', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        for item in d3_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-17', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        for item in d4_entries:
            cursor.execute("""
                INSERT INTO itinerary_entries (id, event_id, flight_group_id, date, start_time, end_time, title, location, description, category, meeting_point, display_order, created_at, updated_at)
                VALUES (?, ?, ?, '2026-10-18', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, item[8], item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], now, now))

        # 4. Insert Content Sections (Authoritative PDF Topics)
        sections = [
            ("welcome_letter", "Welcome Letter", {
                "recipient": "Dear Doctor,",
                "body": "It is our pleasure to welcome you to LIPTIS exclusive event for the eminent physicians being held in Mecca from 15-18 October. Below, you will find the itinerary along with other pertinent information regarding your trip. We wish you a pleasant journey.",
                "dates": "15-18 October 2026",
                "hotels": "Rotana Jabal Omar Hotel, Mecca & Peninsula Worth Hotel Madinah",
                "banner_text": "Welcome to Saudi Arabia"
            }, 1),
            ("umrah_rituals", "Umrah Rituals & Guide", {
                "title_ar": "لمعرفة مناسك العمرة ومعلومات هامة عنها",
                "instruction_ar": "يرجى مسح رمز الاستجابة السريعة (QR Code) أو الضغط على الرابط أسفل الصورة",
                "youtube_url": "https://www.youtube.com/watch?v=IUjFKJGa9Jw",
                "description": "Comprehensive video guide explaining the essential steps, rulings, and spiritual supplications for performing Umrah in the Holy Mosque of Mecca."
            }, 2),
            ("airport_arrival", "Arrival at King Abdulaziz International Airport", {
                "airport_name": "King Abdulaziz International Airport, Jeddah",
                "instructions": "Delegate is expected to arrive at King Abdulaziz International Airport, Jeddah. A representative holding a LIPTIS welcome sign will be waiting at the arrival hall to assist with the transfer to the hotel in Mecca. Please make yourselves known to this representative.",
                "transfer_time": "Approximately 90 minutes by bus to Rotana Jabal Omar Hotel",
                "sign_label": "LIPTIS USA Welcome Sign"
            }, 3),
            ("hotel_details", "Hotel Details", {
                "mecca_hotel": {
                    "name": "Rotana Jabal Omar Hotel",
                    "city": "Mecca",
                    "address": "Jarham District 3045, Jarham Northern 1196978",
                    "phone": "+966 12 553 8400",
                    "facilities": [
                        "Free WiFi",
                        "24-Hours reception",
                        "Restaurant (Caravan Stop & El-Rayan)",
                        "Business centre",
                        "Fitness centre",
                        "Air conditioning",
                        "Minibar",
                        "Marble bathrooms",
                        "Safe deposit box",
                        "Laundry/dry cleaning",
                        "Currency exchange",
                        "Express check-in/out"
                    ]
                },
                "madinah_hotel": {
                    "name": "Peninsula Worth Hotel",
                    "city": "Madinah",
                    "address": "Central Northern Area, Al-Madinah Al-Munawwarah",
                    "dining": "Main Restaurant on the R floor",
                    "stay_period": "17-18 October 2026"
                }
            }, 4),
            ("distance_haram", "Distance from Masjid al-Haram", {
                "distance": "400 Meters",
                "walking_time": "5 Minutes Walk",
                "details": "Direct covered and paved pedestrian access to Masjid al-Haram courtyard from Rotana Jabal Omar."
            }, 5),
            ("transportation", "Transportation", {
                "items": [
                    "Taxis and private drivers are common.",
                    "Haramain High Speed Railway connects Jeddah, Madina and Mecca.",
                    "Walking access to Masjid al-Haram from most city center hotels."
                ]
            }, 6),
            ("finance_policy", "Finance & Congress Policy", {
                "policy_title": "Global LIPTIS Congress Policy",
                "personal_expenses": "In accordance with the Global LIPTIS Congress Policy, we kindly ask you to settle your own Telephone, Laundry and Room Service bills upon checkout.",
                "covered_expenses": "LIPTIS will cover all transportation, hotel accommodation and all meals included in the program."
            }, 7),
            ("key_attractions", "Key Attractions in Mecca and Madinah", {
                "attractions": [
                    {"name": "Masjid al-Haram", "city": "Mecca", "description": "The Great Mosque of Mecca containing the Holy Kaaba."},
                    {"name": "Masjid-El-Nabawi", "city": "Madinah", "description": "The Prophet's Mosque in Medina, the second holiest site in Islam."},
                    {"name": "Masjid Quba", "city": "Madinah", "description": "The first mosque built in the history of Islam."},
                    {"name": "Abraj Al-Bait Towers (Clock Tower)", "city": "Mecca", "description": "Iconic complex overlooking the Grand Mosque with observation deck and shopping galleria."}
                ]
            }, 8),
            ("weather", "Weather", {
                "summary": "During our trip the average temperature is expected to be:",
                "avg_high": "38° C",
                "avg_low": "22° C",
                "clothing": "Recommended clothing: light, breathable cotton, and a hat."
            }, 9),
            ("local_time", "Local Time", {
                "zone_name": "KSA Local Time Zone (Arabia Standard Time)",
                "offset": "GMT+3 hours",
                "comparison": "The same Cairo Local Time."
            }, 10),
            ("foreign_exchange", "Foreign Exchange & Currency", {
                "currency": "Saudi Riyal (SAR)",
                "rates": [
                    {"pair": "1 USD", "value": "≈ 3.75 SAR"},
                    {"pair": "1 SAR", "value": "13.90 EGP"}
                ],
                "notes": "ATMs available at hotels and malls",
                "language": "Arabic"
            }, 11),
            ("electric_appliances", "Electric Appliances", {
                "voltage": "220 V",
                "frequency": "60 Hz",
                "plug_types": ["Type C", "Type F"],
                "notes": "Europlug (Type C) and Schuko (Type F) two-round-pin plugs standard in hotel rooms."
            }, 12),
            ("vat_refund", "VAT (Value Added Tax) Refund Information", {
                "rate": "15%",
                "min_spend": "SAR 500 (about USD 133) in a single transaction or combined receipts from the same store on the same day",
                "eligibility": "Non-resident tourist or GCC national aged 18 or older. Goods must be physical, unused, personal use, and exported within 90 days.",
                "process": [
                    "Shopping at approved stores displaying 'Tax Free' signs and presenting a passport or GCC ID to receive a VAT refund form and original tax invoice.",
                    "Before departing Saudi Arabia, visitors must present the completed VAT refund form, original invoices, passport, and proof of departure (boarding pass) at VAT refund counters in major airports like Riyadh, Jeddah, and Dammam for verification.",
                    "The refund can be received in cash (with daily limits) or credited to a credit card."
                ],
                "excluded_items": "Services (hotels, dining), food and beverages, tobacco, fuel, vehicles, boats, and large-ticket items.",
                "validity": "Valid within six months of purchase; designed to encourage tourism and shopping in Saudi Arabia."
            }, 13),
            ("product_portfolio", "LIPTIS Healthcare Portfolio", {
                "closing_wish": "LIPTIS USA Wishes you a nice time",
                "products": [
                    {"name": "JointGuard", "indication": "Glucosamine + Chondroitin Complex"},
                    {"name": "JointGuard Plus", "indication": "Advanced Joint Cartilage Support"},
                    {"name": "JointGuard Ultra", "indication": "Maximum Strength Joint Flexibility"},
                    {"name": "Xyrkux", "indication": "Etoricoxib 60mg, 90mg, 120mg"}
                ]
            }, 14)
        ]

        for sec in sections:
            cursor.execute("""
                INSERT INTO content_sections (id, event_id, section_key, title, content_json, display_order, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, sec[0], sec[1], json.dumps(sec[2]), sec[3], now))

        # 5. Insert Guest Care Contacts (Exact 10 doctors/managers from PDF Page 5)
        contacts_data = [
            ("Dr. Ahmed Abd El-Mohsen", "Country Manager", "+201028297898", "Country Leadership", 1),
            ("Dr. Mohamed Otaify", "Africa Group Product Manager", "+201065545231", "Marketing & Product", 2),
            ("Dr. Mohamed Ali", "Africa Senior Product Manager", "+201009691464", "Marketing & Product", 3),
            ("Mr. Amr Ahmed", "Public Relations Supervisor", "+201068928287", "Public Relations", 4),
            ("Dr. Mohamed Abdelmoniem", "Senior District Manager", "+201015444706", "District Operations", 5),
            ("Dr. Ahmed Khalil", "Regional Manager", "+201015020524", "Regional Management", 6),
            ("Dr. Mahmoud Anas", "Regional Manager", "+201003505378", "Regional Management", 7),
            ("Dr. Mohamed Yehia", "Executive Medical Representative", "+201016022595", "Medical Delegation", 8),
            ("Dr. Mohamed Ayman", "District Manager", "+201020825094", "District Operations", 9),
            ("Dr. Omar Samy", "District Manager", "+201060191597", "District Operations", 10),
        ]

        for c in contacts_data:
            cursor.execute("""
                INSERT INTO contacts (id, event_id, name, title, phone, whatsapp, category, display_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, c[0], c[1], c[2], c[2], c[3], c[4], now))

        # 6. Insert initial audit log
        cursor.execute("""
            INSERT INTO audit_logs (id, event_id, action, admin_user, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), event_id, "INITIAL_SEED", "system",
            "Initial setup completed from official LIPTIS USA Saudi Arabia 2026 event materials.",
            now
        ))

        print(f"Successfully seeded event '{event_id}' with 2 flight groups, complete PDF sections, and 10 contacts.")

if __name__ == "__main__":
    seed_database()
