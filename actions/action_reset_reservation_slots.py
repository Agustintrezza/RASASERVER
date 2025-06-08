from typing import Any, Dict, List, Text
from rasa_sdk import Action
from rasa_sdk.events import SlotSet, AllSlotsReset

class ActionResetReservationSlots(Action):
    def name(self) -> Text:
        return "action_reset_reservation_slots"

    async def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        # ⚡ Reseteamos SOLO los slots de la reserva
        return [
            SlotSet("name", None),
            SlotSet("date", None),
            SlotSet("people", None),
            SlotSet("phone", None),
            SlotSet("reservation_confirmation", None),
        ]
