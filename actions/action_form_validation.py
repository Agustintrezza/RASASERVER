from typing import Any, Dict, Text

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re
from datetime import datetime

class ValidateReservationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reservation_form"

    async def validate_name(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if not value:
            return {"name": None}
        if len(value.strip().split()) >= 2:
            return {"name": value}
        dispatcher.utter_message(text="⚠️ Por favor, ingresá tu nombre completo (nombre y apellido).")
        return {"name": None}

    async def validate_people(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if not value:
            return {"people": None}
        if value.isdigit() and int(value) > 0:
            return {"people": value}
        dispatcher.utter_message(text="⚠️ Por favor, ingresá un número válido de personas (mayor a 0).")
        return {"people": None}

    async def validate_date(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if not value:
            return {"date": None}
        try:
            date_obj = datetime.strptime(value, "%d/%m/%Y")
            if date_obj.date() < datetime.today().date():
                dispatcher.utter_message(text="⚠️ La fecha no puede ser anterior a hoy. Por favor, indicá una fecha futura.")
                return {"date": None}
            return {"date": value}
        except ValueError:
            dispatcher.utter_message(text="⚠️ Formato de fecha inválido. Usá el formato DD/MM/AAAA, por favor.")
            return {"date": None}

    async def validate_phone(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if not value:
            return {"phone": None}
        if re.fullmatch(r"^\+?\d{8,15}$", value):
            return {"phone": value}
        dispatcher.utter_message(text="⚠️ Número inválido. Ingresá un teléfono válido, con código de país si es posible (ej: +5491123456789).")
        return {"phone": None}
