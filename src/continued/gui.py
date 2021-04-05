#!/usr/bin/env python3

import qtrio
import trio

from qtpy.QtWidgets import QApplication

from .app import ContinuEDApp


async def loop(task_status) -> None:

    loop_completed = trio.Event()

    QApplication.setApplicationName('ContinuED')
    QApplication.setApplicationVersion('0.1')
    QApplication.setOrganizationName('ExtraArcam')
    QApplication.setApplicationDisplayName('ContinuED')

    widget = ContinuEDApp()

    async with qtrio.enter_emissions_channel(signals=[
        widget.closed,
        widget.update_clicked,
    ]) as emissions:

        widget.show()

        task_status.started(loop_completed)

        i = 0
        async for emission in emissions.channel:

            if emission.is_from(widget.closed):
                break

            if emission.is_from(widget.update_clicked):
                i += 1
                widget.set_message(f"{i}")

    loop_completed.set()
