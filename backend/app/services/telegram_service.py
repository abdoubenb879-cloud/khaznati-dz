"""
Khaznati DZ - Telegram Storage Service

Telegram Bot client for centralized file storage.
Adapted from CloudVault's telegram_client.py.
"""

import asyncio
import os
import threading
from typing import Optional, List, Callable

from pyrogram import Client
from pyrogram.errors import FloodWait

from app.core.config import settings


# Shared background loop for all clients
_loop = None
_loop_thread = None
_loop_ready = threading.Event()
_loop_lock = threading.Lock()


def ensure_loop_running():
    """Ensure the background event loop is running."""
    global _loop, _loop_thread
    
    # Quick check without lock
    if _loop_thread is not None and _loop_thread.is_alive() and _loop is not None:
        return _loop
    
    with _loop_lock:
        # Double-check after acquiring lock
        if _loop_thread is not None and _loop_thread.is_alive() and _loop is not None:
            return _loop
        
        # Reset state if thread died or never started
        _loop_ready.clear()
        
        def run_loop():
            global _loop
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            _loop_ready.set()
            _loop.run_forever()
            
        _loop_thread = threading.Thread(target=run_loop, name="KhaznatiTelegramLoop", daemon=True)
        _loop_thread.start()
        
        # Wait for the loop to be assigned
        if not _loop_ready.wait(timeout=30):
            raise RuntimeError("Failed to start event loop thread")
        
        return _loop


class TelegramStorage:
    """
    Singleton Bot client for centralized file storage.
    All users share this single bot instance for uploads/downloads.
    """
    _instance = None
    _lock = threading.Lock()
    
    # Class-level cooldown tracking
    _flood_wait_until = 0
    _flood_wait_duration = 0
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        ensure_loop_running()
        
        self.bot_token = settings.bot_token
        self.channel_id = settings.storage_channel_id
        self.api_id = settings.api_id
        self.api_hash = settings.api_hash
        self.chunk_size = settings.chunk_size
        
        if not self.bot_token:
            print("[TELEGRAM] Warning: BOT_TOKEN not configured")
            self._initialized = True
            self._connected = False
            self.client = None
            return
            
        if not self.channel_id:
            print("[TELEGRAM] Warning: STORAGE_CHANNEL_ID not configured")
            self._initialized = True
            self._connected = False
            self.client = None
            return
        
        # Create bot client
        async def create_bot():
            return Client(
                "khaznati_bot",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token,
                in_memory=True,
                no_updates=True
            )
        
        future = asyncio.run_coroutine_threadsafe(create_bot(), _loop)
        self.client = future.result(timeout=30)
        self._connected = False
        self._initialized = True
        print("[TELEGRAM] TelegramStorage initialized successfully")
    
    def _run_async(self, coro, timeout: int = 120):
        """Run async operation in the background loop with timeout."""
        global _loop, _loop_thread
        
        # Ensure the loop thread is running
        if _loop_thread is None or not _loop_thread.is_alive():
            print("[TELEGRAM] Background thread not alive, restarting...")
            ensure_loop_running()
        
        if _loop is None:
            raise RuntimeError("Background event loop not initialized")
        
        if not _loop.is_running():
            ensure_loop_running()
        
        future = asyncio.run_coroutine_threadsafe(coro, _loop)
        
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            print(f"[TELEGRAM] TIMEOUT: Operation did not complete in {timeout}s")
            raise
        except Exception as e:
            print(f"[TELEGRAM] Operation failed: {type(e).__name__}: {e}")
            raise
    
    @classmethod
    def get_cooldown_status(cls):
        """Check if we're in a FloodWait cooldown period."""
        import time as time_module
        now = time_module.time()
        if now < cls._flood_wait_until:
            remaining = int(cls._flood_wait_until - now)
            return True, remaining
        return False, 0
    
    def connect(self):
        """Start the bot client."""
        import time as time_module
        
        if not self.client:
            raise RuntimeError("Telegram client not configured. Check BOT_TOKEN and STORAGE_CHANNEL_ID.")
        
        if self._connected:
            return self
        
        # Check cooldown
        in_cooldown, remaining = TelegramStorage.get_cooldown_status()
        if in_cooldown:
            raise Exception(f"FloodWait cooldown active. Wait {remaining} seconds.")
        
        with TelegramStorage._lock:
            if self._connected:
                return self
            
            try:
                async def work():
                    await self.client.start()
                
                self._run_async(work(), timeout=60)
                self._connected = True
                print(f"[TELEGRAM] Connected to channel {self.channel_id}")
                return self
                
            except FloodWait as fw:
                wait_time = fw.value if hasattr(fw, 'value') else 300
                TelegramStorage._flood_wait_until = time_module.time() + wait_time
                TelegramStorage._flood_wait_duration = wait_time
                print(f"[TELEGRAM] FloodWait: {wait_time}s cooldown set")
                raise Exception(f"Telegram FloodWait: Must wait {wait_time} seconds")
                
            except Exception as e:
                print(f"[TELEGRAM] Connection failed: {e}")
                raise
    
    def stop(self):
        """Stop the bot client."""
        if self._connected and self.client:
            async def work():
                await self.client.stop()
            self._run_async(work())
            self._connected = False
    
    def upload_file(self, file_path: str, progress_callback: Callable = None):
        """Upload a file to the storage channel."""
        if not self._connected:
            self.connect()
            
        async def work():
            return await self.client.send_document(
                self.channel_id,
                document=file_path,
                file_name=os.path.basename(file_path),
                progress=progress_callback
            )
        return self._run_async(work())
    
    def download_file(self, message_id: int, output_path: str, progress_callback: Callable = None) -> str:
        """Download a file from the storage channel."""
        if not self._connected:
            self.connect()
            
        async def work():
            msg = await self.client.get_messages(self.channel_id, message_id)
            if not msg or not msg.document:
                raise Exception("File not found on Telegram")
            return await self.client.download_media(msg, file_name=output_path, progress=progress_callback)
        return self._run_async(work())
    
    def download_to_memory(self, message_id: int) -> Optional[bytes]:
        """Download a file to memory."""
        if not self._connected:
            self.connect()
            
        async def work():
            msg = await self.client.get_messages(self.channel_id, message_id)
            if not msg or not msg.document:
                return None
            return await self.client.download_media(msg, in_memory=True)
        return self._run_async(work())
    
    def delete_message(self, message_id: int):
        """Delete a message from the storage channel."""
        if not self._connected:
            self.connect()
            
        async def work():
            await self.client.delete_messages(self.channel_id, message_id)
        self._run_async(work())
    
    def upload_chunks(self, chunk_paths: List[str], max_concurrent: int = 3) -> List:
        """Upload multiple chunks in parallel to Telegram."""
        if not self._connected:
            self.connect()
            
        target = self.channel_id
        print(f"[TELEGRAM] Starting upload of {len(chunk_paths)} chunks")
        
        async def upload_single(cp, idx):
            print(f"[TELEGRAM] Uploading chunk {idx+1}/{len(chunk_paths)}")
            result = await self.client.send_document(
                target,
                document=cp,
                file_name=os.path.basename(cp)
            )
            print(f"[TELEGRAM] Chunk {idx+1} uploaded, msg_id: {result.id}")
            return result
        
        async def work():
            results = []
            for i in range(0, len(chunk_paths), max_concurrent):
                batch = chunk_paths[i:i + max_concurrent]
                batch_indices = list(range(i, min(i + max_concurrent, len(chunk_paths))))
                batch_results = await asyncio.gather(*[
                    upload_single(cp, idx) for idx, cp in zip(batch_indices, batch)
                ])
                results.extend(batch_results)
            return results
        
        # Use 10 minute timeout for large file uploads
        return self._run_async(work(), timeout=600)
    
    def download_chunks(self, message_ids: List[int], output_dir: str, max_concurrent: int = 3) -> List[str]:
        """Download multiple chunks in parallel."""
        if not self._connected:
            self.connect()
            
        async def download_single(msg_id, idx):
            msg = await self.client.get_messages(self.channel_id, msg_id)
            if not msg or not msg.document:
                return None
            output_path = os.path.join(output_dir, f"chunk_{idx}")
            return await self.client.download_media(msg, file_name=output_path)
        
        async def work():
            results = []
            for i in range(0, len(message_ids), max_concurrent):
                batch = message_ids[i:i + max_concurrent]
                batch_indices = list(range(i, min(i + max_concurrent, len(message_ids))))
                batch_results = await asyncio.gather(*[
                    download_single(mid, idx) for idx, mid in zip(batch_indices, batch)
                ])
                results.extend(batch_results)
            return results
        
        return self._run_async(work(), timeout=600)


# Global instance
_telegram_instance = None


def get_telegram_storage() -> TelegramStorage:
    """Get the global Telegram storage instance."""
    global _telegram_instance
    if _telegram_instance is None:
        _telegram_instance = TelegramStorage()
    return _telegram_instance


# Convenience export
telegram_storage = get_telegram_storage()
