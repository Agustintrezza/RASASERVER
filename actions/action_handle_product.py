from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import string

class ActionHandleProduct(Action):
    def name(self) -> Text:
        return "action_handle_product"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        option = tracker.latest_message.get("text").strip().upper()

        dynamic_products = tracker.get_slot("dynamic_products")
        if not dynamic_products:
            dispatcher.utter_message(text="⚠️ No hay productos cargados. Por favor, seleccioná una categoría primero.")
            return []

        letters = list(string.ascii_uppercase)
        try:
            selected_index = letters.index(option)
        except ValueError:
            dispatcher.utter_message(text="⚠️ Selección inválida. Respondé con la letra de un producto de la lista.")
            return []

        if selected_index >= len(dynamic_products):
            dispatcher.utter_message(text="⚠️ Selección inválida. No encontré ese producto.")
            return []

        selected_product = dynamic_products[selected_index]

        # Mostrar el detalle del producto
        title = selected_product.get('title', 'Sin título')
        description = selected_product.get('description', 'Sin descripción')
        price = selected_product.get('price', 'Precio no disponible')
        duration = selected_product.get('duration', 'Duración no disponible')
        stock = selected_product.get('stock', 'Stock no disponible')

        # Mostrar el detalle del producto
        message = (
            f"📝 Has seleccionado: *{title}*\n"
            f"📜 {description}\n"
            f"💰 Precio: {price}\n"
            f"🕒 Duración: {duration}\n"
            f"📦 Stock disponible: {stock}"
        )

        dispatcher.utter_message(text=message)

        # ✅ Mando los botones de confirmación
        dispatcher.utter_message(response="utter_ask_if_wants_reservation")

        return [
            SlotSet("selected_product", selected_product),
            SlotSet("navigation_step", "product_detail")
        ]
