"""Event handlers for Telegram messages"""

import asyncio
import heapq
from typing import Any, Optional

from .handle_message import handle_message


def create_new_message_handler(message_processor):
    """Create event handler for new messages in real-time mode.

    Ensures processing occurs in ascending message ID order by buffering
    incoming events briefly and flushing them in order.
    """

    # Min-heap of (message_id, message)
    pending_heap: list[tuple[int, Any]] = []
    heap_lock = asyncio.Lock()
    processing = False
    processed_ids: set[int] = set()
    # Separate task just for the debounce timer (do not tie to the flush task)
    flush_timer_task: Optional[asyncio.Task] = None

    async def _flush_buffered_in_order():
        nonlocal processing
        if processing:
            return
        processing = True
        try:
            while True:
                # Pop a snapshot batch under lock
                async with heap_lock:
                    if not pending_heap:
                        break
                    batch = [
                        heapq.heappop(pending_heap) for _ in range(len(pending_heap))
                    ]

                # Process in ascending ID order
                for _, msg in batch:
                    if msg.id in processed_ids:
                        continue

                    print(
                        f"Processing message (ID: {msg.id}) in order...",
                        flush=True,
                    )
                    root_rec = await handle_message(msg, is_comment=False)
                    message_processor.process_new_message(root_rec, msg)

                    print(
                        f"Saved new message (ID: {msg.id}). Total messages: {len(message_processor.all_messages)}",
                        flush=True,
                    )

                    # Special output line for PowerShell to catch
                    print(
                        f"POWERSHELL_NOTIFICATION:NEW_MESSAGE:{msg.id}:{msg.text[:100] if msg.text else '[Media/No text]'}",
                        flush=True,
                    )

                    processed_ids.add(msg.id)

                # loop again to drain anything that arrived mid-processing
        finally:
            processing = False

    async def _schedule_flush():
        nonlocal flush_timer_task
        # Resettable debounce: cancel existing timer (if still sleeping) and start a new 1s timer
        if flush_timer_task and not flush_timer_task.done():
            flush_timer_task.cancel()
            try:
                await flush_timer_task
            except asyncio.CancelledError:
                pass

        async def _debounce_timer():
            # Wait 1 second since last message, then trigger a flush.
            await asyncio.sleep(1.0)
            # Fire-and-forget the flush so the timer cancellation never cancels an active flush
            asyncio.create_task(_flush_buffered_in_order())

        flush_timer_task = asyncio.create_task(_debounce_timer())

    async def new_message_handler(event):
        msg: Any = event.message
        print(
            f"New message received (ID: {msg.id}). Buffering for ordered processing...",
            flush=True,
        )

        # Buffer for ordered processing
        async with heap_lock:
            heapq.heappush(pending_heap, (msg.id, msg))

        await _schedule_flush()

    return new_message_handler
