from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
import requests
import urllib.parse
import string

# ----- VOLVER ATRÁS -----
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
                    SlotSet("navigation_step", "category"),
                    SlotSet("selected_product", None),  # 🔥 Limpio producto
                    SlotSet("selected_section", None)   # 🔥 Limpio sección por las dudas
                ]
            else:
                dispatcher.utter_message(text="⚠️ Error: no hay categoría seleccionada.")
                return []

        else:
            dispatcher.utter_message(text="📋 Volviendo al menú principal...")

            try:
                categories_response = requests.get("http://localhost:5000/api/categories")
                sections_response = requests.get("http://localhost:5000/api/sections")
                categories_response.raise_for_status()
                sections_response.raise_for_status()
                categories = categories_response.json()
                sections = sections_response.json()
            except Exception as e:
                print(f"🌐 Error al volver al menú: {e}")
                dispatcher.utter_message(text="⚠️ No pude volver al menú. Intentá más tarde.")
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
                SlotSet("navigation_step", "menu"),
                SlotSet("selected_category", None),
                SlotSet("dynamic_products", None),
                SlotSet("selected_product", None),
                SlotSet("selected_section", None)  # 🔥 Limpiar sección al volver
            ]