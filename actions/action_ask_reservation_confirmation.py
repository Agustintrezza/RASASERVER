from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionAskReservationConfirmation(Action):
    def name(self) -> Text:
        return "action_ask_reservation_confirmation"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("name")
        date = tracker.get_slot("date")
        people = tracker.get_slot("people")
        phone = tracker.get_slot("phone")
        selected_product = tracker.get_slot("selected_product")

        # ✅ Usar 'title' en vez de 'name'
        if isinstance(selected_product, dict):
            product_name = selected_product.get("title", "Producto desconocido")
        else:
            product_name = selected_product or "Producto desconocido"

        message = (
            f"🔎 *Por favor, confirmá los datos de tu reserva:*\n"
            f"🏷️ Producto: {product_name}\n"
            f"👤 Nombre: {name}\n"
            f"📅 Fecha: {date}\n"
            f"👥 Personas: {people}\n"
            f"📞 Teléfono: {phone}\n\n"
            "¿Es correcto?"
        )

        buttons = [
            {"title": "✅ Sí", "payload": "/affirm"},
            {"title": "❌ No", "payload": "/deny"},
        ]

        dispatcher.utter_message(text=message, buttons=buttons)

        return []
