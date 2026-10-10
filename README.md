# LIPTIS USA SALs App
**Corporate Event & Dynamic Multi-Flight Trip Management Platform**

---

## 📌 Executive Summary

The **LIPTIS USA SALs App** is an enterprise-grade, responsive, full-stack travel and incentive event management platform engineered specifically for **LIPTIS USA**. Built to strictly adhere to official corporate event documents (Saudi Arabia 2026 Eminent Physicians Delegation) and corporate visual guidelines, it delivers a secure, persistent, multi-flight itinerary system with role-based access control.

### 🌟 Core Architectural Highlights

1. **Multi-Flight Group Itinerary Engine**: Supports distinct flight delegations (e.g., Flynas XY 566 early morning vs. Flynas XY 584 mid-morning). Participants select their flight group, dynamically switching their personalized airport arrivals, meet-and-assist times, and hotel transfer schedules, while seamlessly merging shared symposiums and meals.
2. **Strict Role-Based Access Control (RBAC)**: Backend server-enforced security. Viewers have strict read-only access to published event details. All write operations (event creation, flight group configuration, itinerary edits, section updates) require authenticated administrator sessions with cryptographic PBKDF2-HMAC-SHA256 password hashing.
3. **Faithful PDF Reference Preservation**: Exactly mirrors all 15 topics and visual ribbons from the authoritative event PDF, including Umrah guide with QR code, hotel details, 10 Guest Care contacts with 1-click WhatsApp/Call, live KSA time, weather forecasts, currency converter, plug diagrams, and VAT refund rules.
4. **Persistent, Reusable Event Templates**: Future incentive trips and corporate events can be created or cloned from existing templates with a single click, completely isolating new flights and itineraries without altering the protected structure.
5. **Progressive Web App (PWA) & Offline Caching**: Complete with Web App Manifest, Service Worker (`sw.js`), and cache-first offline support for participants traveling internationally with intermittent mobile data.
6. **Print & PDF Export Engine**: Pre-formatted corporate print stylesheet for instant physical printing or digital PDF export customized to the attendee's selected flight.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (CPython 3.12 verified)
- `uv` package manager (or standard `python -m pip`)

### Running the Application

1. **Navigate to the Project Directory:**
   ```powershell
   cd C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app
   ```

2. **Activate the Virtual Environment:**
   ```powershell
   .venv\Scripts\activate
   ```

3. **Start the Production Backend Server:**
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the Application:**
   - **Local Web Browser:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Mobile Device on Same Wi-Fi:** `http://<your-ip-address>:8000`

---

## 🔐 Administrator Access & Default Credentials

Click the **"🔒 Admin Access"** button in the top right corner of the header.

| Parameter | Value |
| :--- | :--- |
| **Default Username** | `admin` |
| **Default Password** | `AdminPassword2026!` |
| **Password Storage** | PBKDF2-HMAC-SHA256 (100,000 iterations + 32-byte salt) |
| **Session Model** | Cryptographic bearer token (stored in `localStorage`) |

*Admins can change their password directly in the application at any time.*

---

## 📱 Participant User Guide

### 1. Selecting Your Flight
- On the **"Itinerary & Flights"** tab, tap your assigned flight card:
  - **Flight Group 1**: Flynas XY 566 (Cairo dep: 09:25 AM ➔ Jeddah arr: 11:50 AM)
  - **Flight Group 2**: Flynas XY 584 (Cairo dep: 10:20 AM ➔ Jeddah arr: 12:45 PM)
- The application will automatically recalculate and display your personalized arrival day timeline (gathering time, airport meet & assist, and hotel check-in).

### 2. Viewing the Daily Schedule
- Activities are grouped by date (15, 16, 17, 18 October 2026).
- Badges clearly indicate:
  - `🌐 Shared Activity`: Events attended by the entire delegation (e.g., Symposium, high-speed train to Madinah, dinners).
  - `✈️ Group Specific`: Flight schedule and private transfer timings specifically for your flight.

### 3. Printing or Saving as PDF
- Tap the **"🖨️ Print / Save PDF"** button on the main trip card.
- A clean, branded document view will appear ready to send to your printer or save as a PDF file on your phone or laptop.

### 4. Navigating Event Topics (from PDF)
- **🕋 مناسك العمرة (Umrah Guide)**: View Arabic guidelines and scan/click the QR code linking to the official LIPTIS Umrah YouTube video.
- **🏨 Hotel & Airport Details**: Full addresses, phone numbers, facility checklists, and 1-click Google Maps navigation for Rotana Jabal Omar (Mecca) and Peninsula Worth (Madinah).
- **🕌 Attractions & Haram**: Walking distance to the Kaaba (400m / 5 min walk) and key religious landmarks.
- **📞 Guest Care Contacts**: Complete directory of 10 LIPTIS USA leaders and managers with 1-click **Call** and **WhatsApp** buttons.
- **🌤️ Weather, Currency & Plugs**: Real-time KSA clock (GMT+3), weather highs/lows, interactive USD/SAR/EGP currency calculator, and electrical plug illustrations (Type C / Type F).
- **🏷️ VAT Tax Refund**: Complete step-by-step instructions for tourists claiming the 15% VAT refund.

---

## 🛠️ Administrator Guide

### 1. Draft & Publish Workflow
- When an administrator modifies flights, dates, or itinerary items, the application marks the event with **"⚠️ Unpublished Changes Detected"**.
- Viewers only see published information. Once edits are finalized, click **"🚀 Publish Changes Now"** to push updates live to all participant devices.

### 2. Managing Multiple Flights
- Go to the **"✈️ Flight Groups"** tab.
- Click **"+ Add Flight Group"** to define a new flight number, airline, departure/arrival airports, times, and return details.
- Edit existing groups at any time. If flight arrival or departure times change, the application automatically flags dependent itinerary entries for review.

### 3. Itinerary Assignment (Shared vs. Flight-Specific)
- Click **"+ Add Activity / Entry"**.
- Set **Target Audience**:
  - `🌐 Shared by ALL Flight Groups`: For general lectures, meals, checkouts.
  - `✈️ Only for [Group Name]`: For group-specific airport transfers and flights.
- Select category (`flight`, `transfer`, `hotel`, `symposium`, `meal`, `prayer`, `culture`).

### 4. Editing PDF Topic Content
- Go to the **"📄 Content & PDF Topics"** tab.
- The 15 fixed topics from the PDF are protected against accidental structural deletion.
- Click **"✏️ Edit"** on any topic (e.g., Hotel Details, Weather, VAT Refund) to update variables via structured, validated JSON fields.

### 5. Managing Guest Care Contacts
- Go to the **"👥 Guest Care Team"** tab.
- Add or update manager names, phone numbers, titles, and departments.

### 6. Duplicating Events for Future Trips
- Click **"📑 Duplicate as New Trip"**.
- The entire event template—including flights, schedules, and topic structures—is cloned into a new isolated draft event, leaving the original intact.

### 7. Audit History & Disaster Recovery
- Go to the **"📜 Audit History & Backups"** tab.
- Inspect timestamps and administrator usernames for all changes.
- Click **"💾 Download Event Backup (JSON)"** to save a complete standalone offline archive.

---

## 🧪 Acceptance Test Suite

An automated test suite (`backend/tests/test_acceptance.py`) validates all 10 prompt requirements:

```powershell
& .venv\Scripts\python.exe -u tests\test_acceptance.py
```

### Test Results
- `[PASS] [TEST 0] Server Health`: Verified API status and endpoint availability.
- `[PASS] [TEST 1] PDF Topics and Structure`: Verified 14 sections strictly match PDF topics.
- `[PASS] [TEST 2] Admin Authentication & Draft/Publish`: Salted PBKDF2 login, edits, unpublished flag, and publish cycle verified.
- `[PASS] [TEST 3] Multi-Flight Group Isolation`: Group 1 sees Flynas XY 566; Group 2 sees Flynas XY 584 without cross-group leakage.
- `[PASS] [TEST 4] Shared Activity Merging`: Friday symposium & dinner chronologically merged across both groups without duplicates.
- `[PASS] [TEST 5] Conflict Detection Engine`: Verified schedule auditing.
- `[PASS] [TEST 6] Strict Viewer-Only RBAC`: Rejected unauthenticated POST/PUT/DELETE requests with HTTP 401/403/405.
- `[PASS] [TEST 7] PWA Assets`: Verified `manifest.json` and `sw.js` offline capabilities.
- `[PASS] [TEST 8] Event Template Duplication`: Verified full data isolation between cloned and parent events.
- `[PASS] [TEST 9] 10 Guest Care Contacts`: Verified exact names and phone numbers from PDF Page 5.
- `[PASS] [TEST 10] Disaster Recovery JSON Export`: Verified bundle export.

---

## 🌐 Production Deployment Guide

### Option A: Windows Server (Service via NSSM or PowerShell)
1. Install NSSM (Non-Sucking Service Manager) or create a Task Scheduler task:
   ```cmd
   nssm install LiptisSALsApp "C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app\.venv\Scripts\python.exe" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
   nssm start LiptisSALsApp
   ```

### Option B: Linux / Cloud Hosting (Ubuntu / GCP / AWS)
1. Create a `systemd` service unit `/etc/systemd/system/liptis-sals.service`:
   ```ini
   [Unit]
   Description=LIPTIS USA SALs App Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/liptis-sals-app/backend
   ExecStart=/var/www/liptis-sals-app/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
2. Configure Nginx with SSL (Let's Encrypt):
   ```nginx
   server {
       listen 80;
       server_name travel.liptisusa.com;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name travel.liptisusa.com;

       ssl_certificate /etc/letsencrypt/live/travel.liptisusa.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/travel.liptisusa.com/privkey.pem;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

---

## 📋 PDF Content Source Mapping

| PDF Page | Content Section | Implementation in Application |
| :--- | :--- | :--- |
| **Page 1** | Welcome Badge, Mecca Ribbon, LIPTIS Logo | Header ribbons, Hero badge, and branding |
| **Page 2** | Umrah Rituals (Arabic) & QR code / YouTube | `umrah_rituals` tab with interactive QR code & video launcher |
| **Page 3** | Welcome Letter, Airport Meet & Assist, Rotana Hotel | `welcome_letter`, `airport_arrival`, `hotel_details` |
| **Page 4** | Distance from Haram, Transport, Finance Policy, Attractions | `distance_haram`, `transportation`, `finance_policy`, `key_attractions` |
| **Page 5** | 10 Guest Care Contacts, Weather, Time, Currency, Plugs | `contacts` tab (1-click WhatsApp/Call), `weather`, `local_time`, `foreign_exchange`, `electric_appliances` |
| **Page 6 (Var 1)** | Flight Flynas XY 566 Itinerary & Friday Symposium | `flight_groups` Group 1 + Day 1 & Day 2 Itinerary entries |
| **Page 6 (Var 2)** | Flight Flynas XY 584 Itinerary & Friday Symposium | `flight_groups` Group 2 + Day 1 & Day 2 Itinerary entries |
| **Page 7** | Haramain Train to Madinah, Peninsula Worth, Return Flight XY 576 | Day 3 & Day 4 Itinerary entries (Shared transfer & return flight) |
| **Page 8** | VAT 15% Refund Guide & JointGuard / Xyrkux Showcase | `vat_refund` tab & Global Product Portfolio Footer |
