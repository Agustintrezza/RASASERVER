from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import urllib.parse

class ActionFetchSectionDetails(Action):
    def name(self) -> Text:
        return "action_fetch_section_details"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_section = tracker.get_slot("selected_section")

        if not selected_section:
            dispatcher.utter_message(text="⚠️ No hay sección seleccionada.")
            return [SlotSet("selected_section", None)]

        try:
            response = requests.get("http://localhost:5000/api/sections")
            response.raise_for_status()
            sections = response.json()

            # Buscar la sección por título (case insensitive)
            section_detail = next((sec for sec in sections if sec.get('title', '').lower() == selected_section.lower()), None)

            if not section_detail:
                dispatcher.utter_message(text=f"⚠️ No encontré detalles para la sección *{selected_section}*.")
                return [SlotSet("selected_section", None)]

            # Armar el mensaje de detalle
            title = section_detail.get('title', 'Sin título')
            description = section_detail.get('description', 'Sin descripción')

            message = f"📝 *{title}*\n📖 {description}"

            dispatcher.utter_message(text=message)

            return [SlotSet("selected_section", None)]  # 🔥 Limpio después de mostrar
        except Exception as e:
            print(f"🌐 Error al obtener detalles de sección: {e}")
            dispatcher.utter_message(text="⚠️ No pude cargar los detalles de la sección. Intentá más tarde.")
            return [SlotSet("selected_section", None)]
