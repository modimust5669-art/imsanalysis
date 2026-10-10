import json
from fastapi import APIRouter, HTTPException, Query, status
from app.database import get_db

router = APIRouter(prefix="/api/public", tags=["Public / Participant"])

@router.get("/events/active")
def get_active_event():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, subtitle, destination, start_date, end_date, date_display,
                   status, published_at, updated_at
            FROM events
            WHERE is_active = 1 AND status = 'published'
            LIMIT 1
        """)
        row = cursor.fetchone()
        if not row:
            # Fallback to any published event
            cursor.execute("""
                SELECT id, title, subtitle, destination, start_date, end_date, date_display,
                       status, published_at, updated_at
                FROM events
                WHERE status = 'published'
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No published event is currently available. Please check back soon or contact the event administrator."
            )
        return dict(row)

@router.get("/events")
def list_published_events():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, subtitle, destination, start_date, end_date, date_display, is_active, published_at
            FROM events
            WHERE status = 'published'
            ORDER BY start_date ASC
        """)
        return [dict(r) for r in cursor.fetchall()]

@router.get("/events/{event_id}")
def get_published_event_details(event_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, subtitle, destination, start_date, end_date, date_display,
                   status, is_active, published_at, updated_at
            FROM events
            WHERE id = ? AND status = 'published'
        """, (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found or has not been published yet."
            )

        # Get flight groups
        cursor.execute("""
            SELECT id, event_id, name, airline, outbound_flight_number, departure_airport,
                   departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                   return_flight_number, return_departure_airport, return_departure_date,
                   return_departure_time, return_arrival_airport, return_arrival_date,
                   return_arrival_time, notes, display_order
            FROM flight_groups
            WHERE event_id = ?
            ORDER BY display_order ASC, departure_time ASC
        """, (event_id,))
        flights = [dict(r) for r in cursor.fetchall()]

        # Get content sections (PDF topics)
        cursor.execute("""
            SELECT section_key, title, content_json, display_order
            FROM content_sections
            WHERE event_id = ?
            ORDER BY display_order ASC
        """, (event_id,))
        sections = {}
        for r in cursor.fetchall():
            sections[r['section_key']] = {
                "title": r['title'],
                "content": json.loads(r['content_json']),
                "display_order": r['display_order']
            }

        # Get guest care contacts
        cursor.execute("""
            SELECT id, name, title, phone, whatsapp, category, display_order
            FROM contacts
            WHERE event_id = ?
            ORDER BY display_order ASC
        """, (event_id,))
        contacts = [dict(r) for r in cursor.fetchall()]

        return {
            "event": dict(event),
            "flights": flights,
            "sections": sections,
            "contacts": contacts
        }

@router.get("/events/{event_id}/flights")
def get_event_flight_options(event_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        if not ev or ev['status'] != 'published':
            raise HTTPException(status_code=404, detail="Published event not found.")

        cursor.execute("""
            SELECT id, name, airline, outbound_flight_number, departure_airport,
                   departure_date, departure_time, arrival_airport, arrival_date, arrival_time,
                   return_flight_number, return_departure_airport, return_departure_date,
                   return_departure_time, return_arrival_airport, return_arrival_date,
                   return_arrival_time, notes, display_order
            FROM flight_groups
            WHERE event_id = ?
            ORDER BY display_order ASC, departure_time ASC
        """, (event_id,))
        return [dict(r) for r in cursor.fetchall()]

@router.get("/events/{event_id}/itinerary")
def get_flight_specific_itinerary(
    event_id: str,
    flight_group_id: str = Query(..., description="The selected flight group ID")
):
    with get_db() as conn:
        cursor = conn.cursor()
        # Ensure event is published
        cursor.execute("SELECT status FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        if not ev or ev['status'] != 'published':
            raise HTTPException(status_code=404, detail="Published event not found.")

        # Ensure flight group exists
        cursor.execute("""
            SELECT id, name, airline, outbound_flight_number, departure_time, arrival_time
            FROM flight_groups
            WHERE id = ? AND event_id = ?
        """, (flight_group_id, event_id))
        flight_group = cursor.fetchone()
        if not flight_group:
            raise HTTPException(status_code=404, detail="Selected flight group not found.")

        # Query all entries that are either:
        # 1. Shared (flight_group_id IS NULL)
        # 2. Specifically for this flight group (flight_group_id = :flight_group_id)
        cursor.execute("""
            SELECT id, event_id, flight_group_id, date, start_time, end_time, title,
                   location, description, category, meeting_point, transportation_notes,
                   special_instructions, is_important, display_order
            FROM itinerary_entries
            WHERE event_id = ? AND (flight_group_id IS NULL OR flight_group_id = ?)
            ORDER BY date ASC, display_order ASC, start_time ASC
        """, (event_id, flight_group_id))
        
        entries = []
        for r in cursor.fetchall():
            item = dict(r)
            item['is_shared'] = (item['flight_group_id'] is None)
            item['flight_group_name'] = flight_group['name'] if not item['is_shared'] else "All Groups"
            entries.append(item)

        # Organize by date
        grouped_by_date = {}
        for entry in entries:
            d = entry['date']
            if d not in grouped_by_date:
                grouped_by_date[d] = []
            grouped_by_date[d].append(entry)

        return {
            "flight_group": dict(flight_group),
            "total_entries": len(entries),
            "dates": grouped_by_date
        }
