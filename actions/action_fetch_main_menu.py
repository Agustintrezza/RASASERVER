from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import requests
import urllib.parse

class ActionFetchMainMenu(Action):
    def name(self) -> Text:
        return "action_fetch_main_menu"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            categories_response = requests.get("http://localhost:5000/api/categories")
            sections_response = requests.get("http://localhost:5000/api/sections")
            categories_response.raise_for_status()
            sections_response.raise_for_status()
            categories = categories_response.json()
            sections = sections_response.json()
        except Exception as e:
            print(f"🌐 Error al obtener menú: {e}")
            dispatcher.utter_message(text="⚠️ No pude cargar el menú. Intentá más tarde.")
            return []

        if not categories and not sections:
            dispatcher.utter_message(text="⚠️ No hay opciones disponibles por el momento.")
            return []

        # Armamos menú combinado
        message = "👌 ¡Bienvenido a *Ethereal Tours*! 🇦🇷✨\n"
        message += "📋 **Seleccioná una opción escribiendo su número:**\n\n"

        combined_menu = []
        for cat in categories:
            combined_menu.append({"type": "category", "name": cat.get('name', 'Sin nombre')})
        for sec in sections:
            combined_menu.append({"type": "section", "title": sec.get('title', 'Sin título')})

        for idx, item in enumerate(combined_menu, 1):
            if item['type'] == 'category':
                message += f"{idx}. {item['name']}\n"
            else:
                message += f"{idx}. {item['title']} (Sección)\n"

        message += "\n📞 También podés escribir \"hablar con un asesor\" para asistencia personalizada."

        dispatcher.utter_message(text=message)

        return [
            SlotSet("menu_items", combined_menu),
            SlotSet("navigation_step", "menu")
        ]

class ActionHandleOption(Action):
    def name(self) -> Text:
        return "action_handle_option"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        option = tracker.latest_message.get("text").strip()

        menu_items = tracker.get_slot("menu_items")
        if not menu_items:
            dispatcher.utter_message(text="⚠️ No hay menú cargado. Por favor, saludá de nuevo.")
            return []

        try:
            selected_index = int(option) - 1
            if selected_index < 0 or selected_index >= len(menu_items):
                raise ValueError
        except (ValueError, TypeError):
            dispatcher.utter_message(text="⚠️ Selección inválida. Por favor, respondé con un número de la lista.")
            return []

        selected_item = menu_items[selected_index]

        if selected_item['type'] == 'category':
            selected_category = selected_item.get('name', 'Categoría desconocida')
            dispatcher.utter_message(text=f"📚 Has seleccionado: *{selected_category}*\nBuscando opciones disponibles...")
            return [
                SlotSet("selected_category", selected_category),
                FollowupAction("action_fetch_products")
            ]
        elif selected_item['type'] == 'section':
            selected_section = selected_item.get('title', 'Sección desconocida')
            dispatcher.utter_message(text=f"📝 Has seleccionado la sección: *{selected_section}*")
            return [
                SlotSet("selected_section", selected_section),
                FollowupAction("action_fetch_section_details")  # 👈 Nuevo llamado a traer los detalles
            ]