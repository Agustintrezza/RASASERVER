from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import urllib.parse
import string

class ActionFetchProducts(Action):
    def name(self) -> Text:
        return "action_fetch_products"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        selected_category = tracker.get_slot("selected_category")
        if not selected_category:
            dispatcher.utter_message(text="⚠️ No has seleccionado ninguna categoría.")
            return []

        try:
            encoded_category = urllib.parse.quote(selected_category)
            response = requests.get(f"http://localhost:5000/api/tours?category={encoded_category}")
            response.raise_for_status()
            products = response.json()
        except Exception as e:
            print(f"🌐 Error al obtener productos: {e}")
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
            SlotSet("dynamic_categories", None),
            SlotSet("navigation_step", "category")  # 👈🏻 ¡ESTO ES LO QUE FALTABA!
        ]
