import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Animation, Job
from mkgif import utils
from uuid import uuid4


class StatusConsumer(AsyncWebsocketConsumer):
    """Consumer for animation status."""

    async def connect(self):
        self.anim_id = self.scope["url_route"]["kwargs"]["pk"]
        self.keep_running = True
        await self.accept()
        asyncio.create_task(self.check_animation_status())

    async def disconnect(self, close_code):
        self.keep_running = False

    async def check_animation_status(self):
        while self.keep_running:
            status = await self.get_job_status()
            print(status)
            await self.send(text_data=json.dumps({"status": status}))
            if status == "finished" and not await self.is_animation_complete():
                await self.mark_animation_complete()
                self.keep_running = False
            await asyncio.sleep(1)  # Sleep for a second before next check

    @database_sync_to_async
    def get_job_status(self):
        animation = Animation.objects.get(pk=self.anim_id)
        return utils.get_job_status(animation.job_id)

    @database_sync_to_async
    def is_animation_complete(self):
        animation = Animation.objects.get(pk=self.anim_id)
        return animation.status == "complete"

    @database_sync_to_async
    def mark_animation_complete(self):
        animation = Animation.objects.get(pk=self.anim_id)
        animation.status = "complete"
        animation.save()


class MP3ConversionConsumer(AsyncWebsocketConsumer):
    """Consumer for MP3 Conversion."""

    async def connect(self):
        self.job_id = self.scope["url_route"]["kwargs"]["job_id"]
        self.keep_running = True
        await self.accept()
        asyncio.create_task(self.check_conversion_status())

    async def disconnect(self, close_code):
        self.keep_running = False

    async def check_conversion_status(self):
        while self.keep_running:
            status = await self.get_async_job_status(self.job_id)
            if status == "finished":
                file_path = await self.get_file_path(self.job_id)
                await self.send(
                    text_data=json.dumps({"status": "finished", "file_path": file_path})
                )
                self.keep_running = False
            await asyncio.sleep(1)  # Sleep for a second before next check

    @database_sync_to_async
    def get_async_job_status(self, job_id):
        return utils.get_job_status(job_id)

    @database_sync_to_async
    def get_file_path(self, job_id):
        job = Job.objects.get(job_id=job_id)
        return job.file_path
