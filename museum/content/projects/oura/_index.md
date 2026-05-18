---
title: Oura
summary: Reverse-engineering the Oura ring's BLE protocol enough to pull your own sleep and HR data without the official cloud.
status: research
started: 2026-03
---

Ringwise the device is fine; the cloud is the lock-in. The work here is mapping the GATT services, characterising the handshake, and building a small client that talks to the ring directly so the data stays on your machine.
