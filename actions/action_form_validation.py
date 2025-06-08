from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset, ActiveLoop
import re
from datetime import datetime

class ValidateReservationForm(Action):
    def name(self) -> Text:
        return "validate_reservation_form"

    def should_cancel(self, tracker: Tracker) -> bool:
        intent = tracker.latest_message.get("intent", {}).get("name")
        return intent == "go_to_main_menu"

    def cancel_and_return_to_menu(self) -> List[Dict[Text, Any]]:
        return [
            ActiveLoop(None),
            AllSlotsReset(),
            FollowupAction("action_fetch_main_menu"),
        ]

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # 🔥 Si usuario quiere salir
        if self.should_cancel(tracker):
            dispatcher.utter_message(text="🛑 Reserva cancelada. Volviendo al menú principal...")
            return self.cancel_and_return_to_menu()

        slot_to_validate = tracker.get_slot("requested_slot")
        user_input = tracker.latest_message.get("text")

        # 👤 Validar nombre
        if slot_to_validate == "name":
            if user_input and len(user_input.strip().split()) >= 2:
                return [SlotSet("name", user_input)]
            dispatcher.utter_message(text="⚠️ Por favor, ingresá tu nombre completo (nombre y apellido).")
            return [SlotSet("name", None)]

        # 📅 Validar fecha
        if slot_to_validate == "date":
            try:
                date_obj = datetime.strptime(user_input, "%d/%m/%Y")
                if date_obj.date() < datetime.today().date():
                    dispatcher.utter_message(text="⚠️ La fecha no puede ser anterior a hoy. Por favor, indicá una fecha futura.")
                    return [SlotSet("date", None)]
                return [SlotSet("date", user_input)]
            except ValueError:
                dispatcher.utter_message(text="⚠️ Formato de fecha inválido. Usá el formato DD/MM/AAAA, por favor.")
                return [SlotSet("date", None)]

        # 👥 Validar cantidad de personas
        if slot_to_validate == "people":
            if user_input.isdigit() and int(user_input) > 0:
                return [SlotSet("people", user_input)]
            dispatcher.utter_message(text="⚠️ Por favor, ingresá un número válido de personas (mayor a 0).")
            return [SlotSet("people", None)]

        # 📞 Validar teléfono
        if slot_to_validate == "phone":
            if re.fullmatch(r"^\+?\d{8,15}$", user_input):
                return [SlotSet("phone", user_input)]
            dispatcher.utter_message(text="⚠️ Número inválido. Ingresá un teléfono válido, con código de país si es posible (ej: +5491123456789).")
            return [SlotSet("phone", None)]

        return []
