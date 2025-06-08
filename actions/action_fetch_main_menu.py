from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import requests
import urllib.parse

class ActionFetchMainMenu(Action):
    def name(self) -> Text:
        return "action_fetch_main_menu"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        try:
            response = requests.get("http://localhost:5000/api/categories")
            response.raise_for_status()
            categories = response.json()
        except Exception as e:
            print(f"🌐 Error al obtener categorías: {e}")
            dispatcher.utter_message(text="⚠️ No pude cargar el menú. Intentá más tarde.")
            return []

        if not categories:
            dispatcher.utter_message(text="⚠️ No hay categorías disponibles por el momento.")
            return []

        message = "👌 ¡Bienvenido a *Ethereal Tours*! 🇦🇷✨\n"
        message += "📋 **Seleccioná una opción escribiendo su número:**\n\n"

        for idx, cat in enumerate(categories, 1):
            name = cat.get('name', 'Sin nombre')
            message += f"{idx}. {name}\n"

        message += "\n📞 También podés escribir \"hablar con un asesor\" para asistencia personalizada."

        dispatcher.utter_message(text=message)

        return [
            SlotSet("dynamic_categories", categories),
            SlotSet("navigation_step", "menu")
        ]

class ActionHandleOption(Action):
    def name(self) -> Text:
        return "action_handle_option"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        option = tracker.latest_message.get("text").strip()

        dynamic_categories = tracker.get_slot("dynamic_categories")
        if not dynamic_categories:
            dispatcher.utter_message(text="⚠️ No hay menú cargado. Por favor, saludá de nuevo.")
            return []

        try:
            selected_index = int(option) - 1
            if selected_index < 0 or selected_index >= len(dynamic_categories):
                raise ValueError
        except (ValueError, TypeError):
            dispatcher.utter_message(text="⚠️ Selección inválida. Por favor, respondé con un número de la lista.")
            return []

        selected_category = dynamic_categories[selected_index].get('name', 'Categoría desconocida')

        dispatcher.utter_message(text=f"📚 Has seleccionado: *{selected_category}*\nBuscando opciones disponibles...")

        return [
            SlotSet("selected_category", selected_category),
            FollowupAction("action_fetch_products")
        ]
