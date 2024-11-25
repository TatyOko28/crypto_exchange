from channels.generic.websocket import AsyncJsonWebsocketConsumer

class RatesConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("rates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rates", self.channel_name)

    async def rates_update(self, event):
        await self.send_json(event['data']) 