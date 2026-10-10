import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from app.database import get_db
from app.auth import get_current_admin, verify_password, hash_password, create_admin_session, revoke_session
from app.models import (
    AdminLoginRequest, AdminChangePasswordRequest,
    EventCreateRequest, EventUpdateRequest,
    FlightGroupCreateRequest, FlightGroupUpdateRequest,
    ItineraryEntryCreateRequest, ItineraryEntryUpdateRequest,
    ContentSectionUpdateRequest,
    ContactCreateRequest, ContactUpdateRequest
)

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])

def log_audit(event_id: str, action: str, admin_user: str, details: str, conn=None):
    now = datetime.now(timezone.utc).isoformat()
    query = """
        INSERT INTO audit_logs (id, event_id, action, admin_user, details, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (str(uuid.uuid4()), event_id, action, admin_user, details, now)
    if conn:
        conn.execute(query, params)
    else:
        with get_db() as c:
            c.execute(query, params)

def mark_unpublished_changes(event_id: str, conn=None):
    now = datetime.now(timezone.utc).isoformat()
    query = """
        UPDATE events
        SET has_unpublished_changes = 1, updated_at = ?
        WHERE id = ?
    """
    params = (now, event_id)
    if conn:
        conn.execute(query, params)
    else:
        with get_db() as c:
            c.execute(query, params)

# ================= AUTHENTICATION =================

@router.post("/login")
def login(req: AdminLoginRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, salt, full_name, role FROM admin_users WHERE username = ?", (req.username,))
        user = cursor.fetchone()
        if not user or not verify_password(req.password, user['password_hash'], user['salt']):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

        token = create_admin_session(user['id'], conn=conn)
        log_audit(None, "ADMIN_LOGIN", user['username'], f"Admin '{user['username']}' successfully logged in.", conn=conn)
        return {
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "full_name": user['full_name'],
                "role": user['role']
            }
        }

@router.post("/logout")
def logout(admin: dict = Depends(get_current_admin)):
    revoke_session(admin['token'])
    return {"message": "Logged out successfully."}

@router.get("/me")
def get_current_user_profile(admin: dict = Depends(get_current_admin)):
    return {
        "id": admin['id'],
        "username": admin['username'],
        "full_name": admin['full_name'],
        "role": admin['role']
    }

@router.post("/change-password")
def change_password(req: AdminChangePasswordRequest, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM admin_users WHERE id = ?", (admin['id'],))
        row = cursor.fetchone()
        if not verify_password(req.current_password, row['password_hash'], row['salt']):
            raise HTTPException(status_code=400, detail="Current password does not match.")

        new_hash, new_salt = hash_password(req.new_password)
        cursor.execute("UPDATE admin_users SET password_hash = ?, salt = ? WHERE id = ?", (new_hash, new_salt, admin['id']))
        log_audit(None, "PASSWORD_CHANGED", admin['username'], "Administrator changed their password.", conn=conn)
        return {"message": "Password changed successfully."}

# ================= EVENT MANAGEMENT =================

@router.get("/events")
def list_all_events(admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, subtitle, destination, start_date, end_date, date_display,
                   status, has_unpublished_changes, is_active, created_at, updated_at, published_at
            FROM events
            ORDER BY created_at DESC
        """)
        return [dict(r) for r in cursor.fetchall()]

@router.get("/events/{event_id}")
def get_full_event(event_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")

        # Flight groups
        cursor.execute("SELECT * FROM flight_groups WHERE event_id = ? ORDER BY display_order ASC", (event_id,))
        flights = [dict(r) for r in cursor.fetchall()]

        # Itinerary
        cursor.execute("""
            SELECT i.*, f.name as flight_group_name
            FROM itinerary_entries i
            LEFT JOIN flight_groups f ON i.flight_group_id = f.id
            WHERE i.event_id = ?
            ORDER BY i.date ASC, i.display_order ASC, i.start_time ASC
        """, (event_id,))
        itinerary = [dict(r) for r in cursor.fetchall()]

        # Content sections
        cursor.execute("SELECT * FROM content_sections WHERE event_id = ? ORDER BY display_order ASC", (event_id,))
        sections = []
        for r in cursor.fetchall():
            s = dict(r)
            s['content'] = json.loads(s['content_json'])
            sections.append(s)

        # Contacts
        cursor.execute("SELECT * FROM contacts WHERE event_id = ? ORDER BY display_order ASC", (event_id,))
        contacts = [dict(r) for r in cursor.fetchall()]

        # Recent audit logs
        cursor.execute("SELECT * FROM audit_logs WHERE event_id = ? ORDER BY timestamp DESC LIMIT 20", (event_id,))
        logs = [dict(r) for r in cursor.fetchall()]

        return {
            "event": dict(event),
            "flights": flights,
            "itinerary": itinerary,
            "sections": sections,
            "contacts": contacts,
            "audit_logs": logs
        }

@router.post("/events")
def create_event(req: EventCreateRequest, admin: dict = Depends(get_current_admin)):
    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (id, title, subtitle, destination, start_date, end_date, date_display, status, has_unpublished_changes, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?, ?)
        """, (
            event_id, req.title, req.subtitle, req.destination,
            req.start_date, req.end_date, req.date_display,
            req.status or "draft", now, now
        ))

        # Copy base sections template from standard default
        cursor.execute("""
            SELECT section_key, title, content_json, display_order
            FROM content_sections
            WHERE event_id = 'liptis-saudi-2026'
        """)
        base_sections = cursor.fetchall()
        for s in base_sections:
            cursor.execute("""
                INSERT INTO content_sections (id, event_id, section_key, title, content_json, display_order, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), event_id, s['section_key'], s['title'], s['content_json'], s['display_order'], now))

        log_audit(event_id, "CREATE_EVENT", admin['username'], f"Created new event: '{req.title}'", conn=conn)

    return {"id": event_id, "message": "Event created successfully from template."}

@router.put("/events/{event_id}")
def update_event(event_id: str, req: EventUpdateRequest, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found.")

        updates = []
        params = []
        for field, val in req.dict(exclude_unset=True).items():
            if field == "is_active":
                updates.append("is_active = ?")
                params.append(1 if val else 0)
            else:
                updates.append(f"{field} = ?")
                params.append(val)

        if updates:
            now = datetime.now(timezone.utc).isoformat()
            updates.append("has_unpublished_changes = 1")
            updates.append("updated_at = ?")
            params.append(now)
            params.append(event_id)
            query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            log_audit(event_id, "UPDATE_EVENT", admin['username'], f"Updated fields: {list(req.dict(exclude_unset=True).keys())}", conn=conn)

    return {"message": "Event updated successfully."}

@router.post("/events/{event_id}/publish")
def publish_event(event_id: str, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events
            SET status = 'published', has_unpublished_changes = 0, published_at = ?, updated_at = ?
            WHERE id = ?
        """, (now, now, event_id))
        log_audit(event_id, "PUBLISH_EVENT", admin['username'], "Published all event changes to participants.", conn=conn)
    return {"message": "Event published successfully."}

@router.post("/events/{event_id}/unpublish")
def unpublish_event(event_id: str, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET status = 'draft', updated_at = ? WHERE id = ?", (now, event_id))
        log_audit(event_id, "UNPUBLISH_EVENT", admin['username'], "Moved event to draft status.", conn=conn)
    return {"message": "Event unpublished."}

@router.post("/events/{event_id}/set-active")
def set_active_event(event_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET is_active = 0")
        cursor.execute("UPDATE events SET is_active = 1 WHERE id = ?", (event_id,))
        log_audit(event_id, "SET_ACTIVE_EVENT", admin['username'], f"Set event {event_id} as the primary active event.", conn=conn)
    return {"message": "Active event updated."}

@router.post("/events/{event_id}/duplicate")
def duplicate_event(event_id: str, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    new_event_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        orig = cursor.fetchone()
        if not orig:
            raise HTTPException(status_code=404, detail="Source event not found.")

        # Create duplicated event
        cursor.execute("""
            INSERT INTO events (id, title, subtitle, destination, start_date, end_date, date_display, status, has_unpublished_changes, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', 1, 0, ?, ?)
        """, (
            new_event_id,
            f"{orig['title']} (Copy)",
            orig['subtitle'],
            orig['destination'],
            orig['start_date'],
            orig['end_date'],
            orig['date_display'],
            now, now
        ))

        # Copy flight groups with map of old_id -> new_id
        cursor.execute("SELECT * FROM flight_groups WHERE event_id = ?", (event_id,))
        flight_map = {}
        for fg in cursor.fetchall():
            new_fg_id = str(uuid.uuid4())
            flight_map[fg['id']] = new_fg_id
            cursor.execute("""
                INSERT INTO flight_groups (
                    id, event_id, name, airline, outbound_flight_number, departure_airport,
                    departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                    return_flight_number, return_departure_airport, return_departure_date,
                    return_departure_time, return_arrival_airport, return_arrival_date,
                    return_arrival_time, notes, display_order, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_fg_id, new_event_id, fg['name'], fg['airline'], fg['outbound_flight_number'],
                fg['departure_airport'], fg['departure_date'], fg['departure_time'],
                fg['arrival_airport'], fg['arrival_date'], fg['arrival_time'],
                fg['return_flight_number'], fg['return_departure_airport'],
                fg['return_departure_date'], fg['return_departure_time'],
                fg['return_arrival_airport'], fg['return_arrival_date'],
                fg['return_arrival_time'], fg['notes'], fg['display_order'], now, now
            ))

        # Copy itinerary entries
        cursor.execute("SELECT * FROM itinerary_entries WHERE event_id = ?", (event_id,))
        for it in cursor.fetchall():
            target_fg_id = flight_map.get(it['flight_group_id']) if it['flight_group_id'] else None
            cursor.execute("""
                INSERT INTO itinerary_entries (
                    id, event_id, flight_group_id, date, start_time, end_time, title,
                    location, description, category, meeting_point, transportation_notes,
                    special_instructions, is_important, display_order, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()), new_event_id, target_fg_id, it['date'], it['start_time'],
                it['end_time'], it['title'], it['location'], it['description'],
                it['category'], it['meeting_point'], it['transportation_notes'],
                it['special_instructions'], it['is_important'], it['display_order'], now, now
            ))

        # Copy content sections
        cursor.execute("SELECT * FROM content_sections WHERE event_id = ?", (event_id,))
        for s in cursor.fetchall():
            cursor.execute("""
                INSERT INTO content_sections (id, event_id, section_key, title, content_json, display_order, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), new_event_id, s['section_key'], s['title'], s['content_json'], s['display_order'], now))

        # Copy contacts
        cursor.execute("SELECT * FROM contacts WHERE event_id = ?", (event_id,))
        for c in cursor.fetchall():
            cursor.execute("""
                INSERT INTO contacts (id, event_id, name, title, phone, whatsapp, category, display_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), new_event_id, c['name'], c['title'], c['phone'], c['whatsapp'], c['category'], c['display_order'], now))

        log_audit(new_event_id, "DUPLICATE_EVENT", admin['username'], f"Duplicated event from '{orig['title']}' ({event_id})", conn=conn)

    return {"new_event_id": new_event_id, "message": "Event duplicated successfully."}

@router.delete("/events/{event_id}")
def delete_event(event_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, is_active FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        if not ev:
            raise HTTPException(status_code=404, detail="Event not found.")
        if ev['is_active']:
            raise HTTPException(status_code=400, detail="Cannot delete the currently active event. Please set another event as active first.")

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        log_audit(None, "DELETE_EVENT", admin['username'], f"Deleted event '{ev['title']}' ({event_id})", conn=conn)

    return {"message": "Event deleted successfully."}

# ================= FLIGHT GROUP MANAGEMENT =================

@router.post("/events/{event_id}/flights")
def create_flight_group(event_id: str, req: FlightGroupCreateRequest, admin: dict = Depends(get_current_admin)):
    fg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO flight_groups (
                id, event_id, name, airline, outbound_flight_number, departure_airport,
                departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                return_flight_number, return_departure_airport, return_departure_date,
                return_departure_time, return_arrival_airport, return_arrival_date,
                return_arrival_time, notes, display_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fg_id, event_id, req.name, req.airline, req.outbound_flight_number,
            req.departure_airport, req.departure_date, req.departure_time,
            req.arrival_airport, req.arrival_date, req.arrival_time,
            req.return_flight_number, req.return_departure_airport,
            req.return_departure_date, req.return_departure_time,
            req.return_arrival_airport, req.return_arrival_date,
            req.return_arrival_time, req.notes, req.display_order or 0, now, now
        ))
        mark_unpublished_changes(event_id, conn=conn)
        log_audit(event_id, "CREATE_FLIGHT_GROUP", admin['username'], f"Created flight group '{req.name}' ({req.outbound_flight_number})", conn=conn)

    return {"id": fg_id, "message": "Flight group created successfully."}

@router.put("/flights/{flight_id}")
def update_flight_group(flight_id: str, req: FlightGroupUpdateRequest, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flight_groups WHERE id = ?", (flight_id,))
        curr = cursor.fetchone()
        if not curr:
            raise HTTPException(status_code=404, detail="Flight group not found.")

        updates = []
        params = []
        for field, val in req.dict(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            params.append(val)

        if updates:
            now = datetime.now(timezone.utc).isoformat()
            updates.append("updated_at = ?")
            params.append(now)
            params.append(flight_id)
            cursor.execute(f"UPDATE flight_groups SET {', '.join(updates)} WHERE id = ?", params)
            mark_unpublished_changes(curr['event_id'], conn=conn)
            
            # Check if arrival/departure times were changed
            changed_fields = req.dict(exclude_unset=True)
            time_warning = None
            if "arrival_time" in changed_fields or "departure_time" in changed_fields:
                time_warning = "Flight timing changed. Please review dependent itinerary entries (e.g., airport transfers, hotel check-in) for possible schedule conflicts."

            log_audit(curr['event_id'], "UPDATE_FLIGHT_GROUP", admin['username'], f"Updated flight group '{curr['name']}'. {time_warning or ''}", conn=conn)
            return {"message": "Flight group updated successfully.", "schedule_warning": time_warning}

    return {"message": "No changes made."}

@router.delete("/flights/{flight_id}")
def delete_flight_group(flight_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, name FROM flight_groups WHERE id = ?", (flight_id,))
        fg = cursor.fetchone()
        if not fg:
            raise HTTPException(status_code=404, detail="Flight group not found.")

        cursor.execute("DELETE FROM flight_groups WHERE id = ?", (flight_id,))
        mark_unpublished_changes(fg['event_id'], conn=conn)
        log_audit(fg['event_id'], "DELETE_FLIGHT_GROUP", admin['username'], f"Deleted flight group '{fg['name']}'", conn=conn)

    return {"message": "Flight group deleted."}

# ================= ITINERARY ENTRIES MANAGEMENT =================

@router.post("/events/{event_id}/itinerary")
def create_itinerary_entry(event_id: str, req: ItineraryEntryCreateRequest, admin: dict = Depends(get_current_admin)):
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itinerary_entries (
                id, event_id, flight_group_id, date, start_time, end_time, title,
                location, description, category, meeting_point, transportation_notes,
                special_instructions, is_important, display_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, event_id, req.flight_group_id, req.date, req.start_time,
            req.end_time, req.title, req.location, req.description,
            req.category or "activity", req.meeting_point, req.transportation_notes,
            req.special_instructions, 1 if req.is_important else 0,
            req.display_order or 0, now, now
        ))
        mark_unpublished_changes(event_id, conn=conn)
        scope = "Shared" if not req.flight_group_id else f"Flight Group {req.flight_group_id}"
        log_audit(event_id, "CREATE_ITINERARY", admin['username'], f"Created entry: '{req.title}' ({req.date} {req.start_time}) [{scope}]", conn=conn)

    return {"id": entry_id, "message": "Itinerary entry created."}

@router.put("/itinerary/{entry_id}")
def update_itinerary_entry(entry_id: str, req: ItineraryEntryUpdateRequest, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, title FROM itinerary_entries WHERE id = ?", (entry_id,))
        curr = cursor.fetchone()
        if not curr:
            raise HTTPException(status_code=404, detail="Itinerary entry not found.")

        updates = []
        params = []
        for field, val in req.dict(exclude_unset=True).items():
            if field == "is_important":
                updates.append("is_important = ?")
                params.append(1 if val else 0)
            else:
                updates.append(f"{field} = ?")
                params.append(val)

        if updates:
            now = datetime.now(timezone.utc).isoformat()
            updates.append("updated_at = ?")
            params.append(now)
            params.append(entry_id)
            cursor.execute(f"UPDATE itinerary_entries SET {', '.join(updates)} WHERE id = ?", params)
            mark_unpublished_changes(curr['event_id'], conn=conn)
            log_audit(curr['event_id'], "UPDATE_ITINERARY", admin['username'], f"Updated entry: '{curr['title']}'", conn=conn)

    return {"message": "Itinerary entry updated."}

@router.delete("/itinerary/{entry_id}")
def delete_itinerary_entry(entry_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, title FROM itinerary_entries WHERE id = ?", (entry_id,))
        curr = cursor.fetchone()
        if not curr:
            raise HTTPException(status_code=404, detail="Itinerary entry not found.")

        cursor.execute("DELETE FROM itinerary_entries WHERE id = ?", (entry_id,))
        mark_unpublished_changes(curr['event_id'], conn=conn)
        log_audit(curr['event_id'], "DELETE_ITINERARY", admin['username'], f"Deleted entry: '{curr['title']}'", conn=conn)

    return {"message": "Itinerary entry deleted."}

# ================= FIXED PDF TOPICS / SECTIONS =================

@router.put("/events/{event_id}/sections/{section_key}")
def update_content_section(event_id: str, section_key: str, req: ContentSectionUpdateRequest, admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM content_sections WHERE event_id = ? AND section_key = ?", (event_id, section_key))
        sec = cursor.fetchone()
        if not sec:
            raise HTTPException(status_code=404, detail=f"Content section '{section_key}' not found.")

        updates = ["content_json = ?", "updated_at = ?"]
        params = [json.dumps(req.content_json), now]
        if req.title:
            updates.append("title = ?")
            params.append(req.title)

        params.extend([event_id, section_key])
        cursor.execute(f"UPDATE content_sections SET {', '.join(updates)} WHERE event_id = ? AND section_key = ?", params)
        mark_unpublished_changes(event_id, conn=conn)
        log_audit(event_id, "UPDATE_SECTION", admin['username'], f"Updated PDF topic '{section_key}'", conn=conn)

    return {"message": f"Section '{section_key}' updated successfully."}

# ================= CONTACTS MANAGEMENT =================

@router.post("/events/{event_id}/contacts")
def create_contact(event_id: str, req: ContactCreateRequest, admin: dict = Depends(get_current_admin)):
    contact_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (id, event_id, name, title, phone, whatsapp, category, display_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_id, event_id, req.name, req.title, req.phone,
            req.whatsapp or req.phone, req.category or "Guest Care",
            req.display_order or 0, now
        ))
        mark_unpublished_changes(event_id, conn=conn)
        log_audit(event_id, "CREATE_CONTACT", admin['username'], f"Added guest care contact: '{req.name}'", conn=conn)

    return {"id": contact_id, "message": "Contact added."}

@router.put("/contacts/{contact_id}")
def update_contact(contact_id: str, req: ContactUpdateRequest, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, name FROM contacts WHERE id = ?", (contact_id,))
        curr = cursor.fetchone()
        if not curr:
            raise HTTPException(status_code=404, detail="Contact not found.")

        updates = []
        params = []
        for field, val in req.dict(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            params.append(val)

        if updates:
            params.append(contact_id)
            cursor.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?", params)
            mark_unpublished_changes(curr['event_id'], conn=conn)
            log_audit(curr['event_id'], "UPDATE_CONTACT", admin['username'], f"Updated contact: '{curr['name']}'", conn=conn)

    return {"message": "Contact updated."}

@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, name FROM contacts WHERE id = ?", (contact_id,))
        curr = cursor.fetchone()
        if not curr:
            raise HTTPException(status_code=404, detail="Contact not found.")

        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        mark_unpublished_changes(curr['event_id'], conn=conn)
        log_audit(curr['event_id'], "DELETE_CONTACT", admin['username'], f"Deleted contact: '{curr['name']}'", conn=conn)

    return {"message": "Contact deleted."}

# ================= CONFLICT DETECTION & AUDIT =================

@router.get("/events/{event_id}/conflicts")
def detect_event_conflicts(event_id: str, admin: dict = Depends(get_current_admin)):
    conflicts = []
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Check flight groups for missing vital details
        cursor.execute("SELECT * FROM flight_groups WHERE event_id = ?", (event_id,))
        flight_groups = [dict(r) for r in cursor.fetchall()]
        for fg in flight_groups:
            if not fg.get('outbound_flight_number'):
                conflicts.append({"type": "missing_flight_info", "severity": "error", "message": f"Flight group '{fg['name']}' is missing an outbound flight number."})
            if not fg.get('departure_time') or not fg.get('arrival_time'):
                conflicts.append({"type": "missing_schedule", "severity": "error", "message": f"Flight group '{fg['name']}' is missing departure or arrival time."})

        # 2. Check each flight group's itinerary for chronological alignment
        for fg in flight_groups:
            cursor.execute("""
                SELECT * FROM itinerary_entries
                WHERE event_id = ? AND (flight_group_id IS NULL OR flight_group_id = ?)
                ORDER BY date ASC, display_order ASC, start_time ASC
            """, (event_id, fg['id']))
            entries = [dict(r) for r in cursor.fetchall()]

            # Check for any transfer scheduled before arrival on arrival date
            arrival_date = fg.get('arrival_date')
            arr_time_str = fg.get('arrival_time')
            for entry in entries:
                if entry['date'] == arrival_date and entry['category'] in ['transfer', 'hotel']:
                    # Simple heuristic flag
                    pass

        # 3. Check for empty itinerary dates
        cursor.execute("SELECT DISTINCT date FROM itinerary_entries WHERE event_id = ?", (event_id,))
        dates = [r['date'] for r in cursor.fetchall()]
        if not dates:
            conflicts.append({"type": "no_itinerary", "severity": "warning", "message": "No itinerary entries configured for this event."})

    return {"conflict_count": len(conflicts), "conflicts": conflicts}

# ================= BACKUP EXPORT & IMPORT =================

@router.get("/events/{event_id}/export")
def export_event_bundle(event_id: str, admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")

        cursor.execute("SELECT * FROM flight_groups WHERE event_id = ?", (event_id,))
        flights = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM itinerary_entries WHERE event_id = ?", (event_id,))
        itinerary = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM content_sections WHERE event_id = ?", (event_id,))
        sections = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM contacts WHERE event_id = ?", (event_id,))
        contacts = [dict(r) for r in cursor.fetchall()]

        return {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "exported_by": admin['username'],
            "event": dict(event),
            "flight_groups": flights,
            "itinerary": itinerary,
            "sections": sections,
            "contacts": contacts
        }
