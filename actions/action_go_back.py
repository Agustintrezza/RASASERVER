from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

class ActionGoBack(Action):
    def name(self) -> Text:
        return "action_go_back"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[EventType]:

        navigation_step = tracker.get_slot("navigation_step")

        if navigation_step == "product_detail":
            dispatcher.utter_message(text="📚 Volviendo al listado de productos...")

            selected_category = tracker.get_slot("selected_category")

            # 👉 Manualmente devolvemos la lista sin FollowupAction
            import requests
            import urllib.parse
            import string

            if selected_category:
                try:
                    encoded_category = urllib.parse.quote(selected_category)
                    response = requests.get(f"http://localhost:5000/api/tours?category={encoded_category}")
                    response.raise_for_status()
                    products = response.json()
                except Exception as e:
                    dispatcher.utter_message(text="⚠️ No pude cargar los productos. Intentá más tarde.")
                    return []

                if not products:
                    dispatcher.utter_message(text=f"⚠️ No hay productos disponibles para *{selected_category}*.")
                    return []

                message = f"📚 *Productos disponibles en {selected_category}:*\n\n"
                for idx, prod in enumerate(products):
                    letter = string.ascii_uppercase[idx]
                    title = prod.get('title', 'Sin título')
                    description = prod.get('description', 'Sin descripción')
                    message += f"{letter}. 🎯 *{title}*\n   📜 {description}\n\n"

                message += "👉 Respondé con la letra del producto para más detalles."

                dispatcher.utter_message(text=message)

                return [
                    SlotSet("dynamic_products", products),
                    SlotSet("navigation_step", "category")
                ]
            else:
                dispatcher.utter_message(text="⚠️ Error: no hay categoría seleccionada.")
                return []

        elif navigation_step == "category":
            dispatcher.utter_message(text="📋 Volviendo al menú principal...")

            # Lo mismo para el menú:
            import requests

            try:
                response = requests.get("http://localhost:5000/api/categories")
                response.raise_for_status()
                categories = response.json()
            except Exception as e:
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

        else:
            dispatcher.utter_message(text="📋 Volviendo al menú principal... (default)")

            # Igual que arriba
            import requests

            try:
                response = requests.get("http://localhost:5000/api/categories")
                response.raise_for_status()
                categories = response.json()
            except Exception as e:
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
