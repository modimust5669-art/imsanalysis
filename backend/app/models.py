from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class EventCreateRequest(BaseModel):
    title: str
    subtitle: Optional[str] = "Welcome to Saudi Arabia"
    destination: str
    start_date: str
    end_date: str
    date_display: str
    status: Optional[str] = "published"

class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    date_display: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class FlightGroupCreateRequest(BaseModel):
    event_id: str
    name: str
    airline: str
    outbound_flight_number: str
    departure_airport: str
    departure_date: str
    departure_time: str
    arrival_airport: str
    arrival_date: str
    arrival_time: str
    return_flight_number: Optional[str] = None
    return_departure_airport: Optional[str] = None
    return_departure_date: Optional[str] = None
    return_departure_time: Optional[str] = None
    return_arrival_airport: Optional[str] = None
    return_arrival_date: Optional[str] = None
    return_arrival_time: Optional[str] = None
    notes: Optional[str] = None
    display_order: Optional[int] = 0

class FlightGroupUpdateRequest(BaseModel):
    name: Optional[str] = None
    airline: Optional[str] = None
    outbound_flight_number: Optional[str] = None
    departure_airport: Optional[str] = None
    departure_date: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_airport: Optional[str] = None
    arrival_date: Optional[str] = None
    arrival_time: Optional[str] = None
    return_flight_number: Optional[str] = None
    return_departure_airport: Optional[str] = None
    return_departure_date: Optional[str] = None
    return_departure_time: Optional[str] = None
    return_arrival_airport: Optional[str] = None
    return_arrival_date: Optional[str] = None
    return_arrival_time: Optional[str] = None
    notes: Optional[str] = None
    display_order: Optional[int] = None

class ItineraryEntryCreateRequest(BaseModel):
    event_id: str
    flight_group_id: Optional[str] = None  # None = Shared across all flight groups
    date: str
    start_time: str
    end_time: Optional[str] = None
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "activity"
    meeting_point: Optional[str] = None
    transportation_notes: Optional[str] = None
    special_instructions: Optional[str] = None
    is_important: Optional[bool] = False
    display_order: Optional[int] = 0

class ItineraryEntryUpdateRequest(BaseModel):
    flight_group_id: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    meeting_point: Optional[str] = None
    transportation_notes: Optional[str] = None
    special_instructions: Optional[str] = None
    is_important: Optional[bool] = None
    display_order: Optional[int] = None

class ContentSectionUpdateRequest(BaseModel):
    title: Optional[str] = None
    content_json: Dict[str, Any]

class ContactCreateRequest(BaseModel):
    event_id: str
    name: str
    title: str
    phone: str
    whatsapp: Optional[str] = None
    category: Optional[str] = "Guest Care"
    display_order: Optional[int] = 0

class ContactUpdateRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    category: Optional[str] = None
    display_order: Optional[int] = None
