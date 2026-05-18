---
title: ESP32 Zigbee
summary: ESP32-C6 acting as a Zigbee node, talking to IKEA Tradfri devices. Experimental — half firmware exploration, half home-automation playground.
status: research
started: 2026-03
---

The C6 has Zigbee on-die, which makes it the cheapest plausible Zigbee dev board on the market. The work here is figuring out the Espressif Zigbee SDK, getting reliable pairing against IKEA hubs, and seeing how far custom endpoints can be pushed before things get weird.
