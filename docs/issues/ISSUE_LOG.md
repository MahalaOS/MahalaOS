# MahalaOS Issue Log

A running log of all friction points, bugs, and blockers discovered during testing.
Issues are numbered sequentially. See `docs/issues/` for full individual reports.

---

## Issue Index

| ID | Title | Phase | Component | Status | Device | Date |
|----|-------|-------|-----------|--------|--------|------|
| [#001](#001) | Waydroid — no network connectivity | 0 | Waydroid / nftables | ✅ Fixed | OnePlus 6T | 2026-02-28 |
| [#002](#002) | Lock screen — full QWERTY shown for PIN entry | 0 | Shell / buffyboard | 🔵 Upstream | OnePlus 6T | 2026-03-01 |
| [#003](#003) | Call audio — feedback reported by other party | 0 | Audio / callaudiod | ✅ Fixed | OnePlus 6T | 2026-03-01 |
| [#004](#004) | GNOME Settings — swipe-back navigation missing in some panels | 0 | Shell / GNOME | 🔵 Upstream | OnePlus 6T | 2026-03-02 |
| [#005](#005) | Waydroid — notifications not bridging to host shell | 0 | Waydroid / notifications | 🟡 In Progress | OnePlus 6T | 2026-03-02 |

---

## Template

Copy this block for each new issue.

---

### #XXX — [Short descriptive title]

**Date discovered:** YYYY-MM-DD  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0 / 1 / 2 / 3  
**Component:** e.g. Telephony / Audio / Waydroid / Shell / Networking / Battery / Camera  
**Status:** 🔴 Open · 🟡 In Progress · ✅ Fixed · 🔵 Upstream · ❌ Won't Fix  

**Symptom**  
What the user experiences. Write this as a non-technical person would describe it.

**Steps to reproduce**  
1. Step one  
2. Step two  
3. Observed result  

**Expected behaviour**  
What should happen.

**Root cause**  
Technical explanation once known. Leave blank if undetermined.

**Fix / Workaround**  
What was done to resolve it. Include file paths, commands, or service names where relevant.

**Fix location**  
`overlay/path/to/file` or `upstream` with link.

**Consumer impact**  
Rate 1–5 (5 = blocks daily use entirely).

**Notes**  
Any upstream issues, related tickets, or follow-up work.

---

---

## Issues

---

### #001 — Waydroid — no network connectivity

**Date discovered:** 2026-02-28  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0  
**Component:** Waydroid / nftables / Networking  
**Status:** ✅ Fixed  

**Symptom**  
Waydroid starts and the Android container loads, but has no internet connection. Apps cannot reach the network.

**Steps to reproduce**  
1. Start Waydroid session  
2. Open any Android app requiring internet  
3. Network requests fail — no IP/DNS in container  

**Expected behaviour**  
Android container obtains IP via DHCP on `waydroid0` bridge and can reach the internet.

**Root cause**  
postmarketOS's nftables firewall has a default drop policy on the `inet filter` chain. The `waydroid0` bridge interface had no explicit allow rules, causing all DHCP traffic to be silently dropped. The container could not obtain an IP address, default route, or DNS configuration.

**Fix / Workaround**  
Added two nftables rules to allow traffic from `waydroid0`, implemented as a persistent systemd service (`mahala-waydroid-net.service`) so rules survive reboots.

**Fix location**  
`overlay/etc/systemd/system/mahala-waydroid-net.service`

**Consumer impact**  
5 — Waydroid unusable without fix. WhatsApp (key consumer use case) requires network.

**Notes**  
Likely affects all Waydroid users on postmarketOS with nftables. Worth raising upstream with postmarketOS.

---

### #002 — Lock screen — full QWERTY shown for PIN entry

**Date discovered:** 2026-03-01  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0  
**Component:** Shell / buffyboard / initramfs  
**Status:** 🔵 Upstream  

**Symptom**  
On boot, the LUKS passphrase screen presents a full QWERTY keyboard (buffyboard). Users with a numeric PIN must hunt for digits on a full keyboard rather than seeing a numpad.

**Steps to reproduce**  
1. Power on device (LUKS encryption enabled)  
2. Observe unlock screen  
3. Full QWERTY keyboard displayed  

**Expected behaviour**  
Numeric PIN entry should present a numpad, consistent with the post-boot GNOME lock screen which correctly shows a numpad for PIN codes.

**Root cause**  
`buffyboard` (the initramfs on-screen keyboard) has no numeric/PIN mode. `init_functions.sh` spawns it unconditionally without a layout flag.

**Fix / Workaround**  
None currently. Workaround: set a password-style passphrase that is easier to type on QWERTY.

**Fix location**  
Upstream — postmarketOS `buffyboard` and `init_functions.sh`

**Consumer impact**  
3 — Confusing for non-technical users but functional.

**Notes**  
Upstream issue raised. This is a legitimate MahalaOS upstream contribution opportunity. Until fixed, MahalaOS could document recommended passphrase format in setup wizard.

---

### #003 — Call audio — Feedback reported by other party when on a call

**Date discovered:** 2026-03-01  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0  
**Component:** Audio / callaudiod / PulseAudio / Telephony  
**Status:** ✅ Fixed  

**Symptom**  
Phone calls connect successfully and clear audio both ways but other party was reporting high levels of feedback/echo.

**Steps to reproduce**  
1. Dial an outbound call or receive an inbound call  
2. Call connects  
3. High levls of feedback/echo for the third party  

**Expected behaviour**  
Audio switches automatically to Voice Call profile on call connect and returns to HiFi on disconnect.

**Root cause**  
`callaudiod` was not automatically switching PulseAudio from the "HiFi" profile to the "Voice Call" profile when calls became active. The system uses PulseAudio for audio (PipeWire handles video/camera only). The Voice Call UCM profile existed and worked correctly, but the daemon did not trigger the switch.

**Fix / Workaround**  
Shell script monitors ModemManager DBus signals for call state changes and switches PulseAudio profiles accordingly. Implemented as a systemd user service.

**Fix location**  
`overlay/etc/systemd/user/mahala-call-audio.service`

**Consumer impact**  
4 — Phone calls become difficult and annoying for others.

**Notes**  
Root cause investigation required ruling out PipeWire, WirePlumber, and UCM configs before identifying callaudiod as the failing layer. Debugging required SSH access and multi-layer audio stack tracing.

---

### #004 — GNOME Settings — swipe-back navigation missing in some panels

**Date discovered:** 2026-03-02  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0  
**Component:** Shell / GNOME / gnome-control-center  
**Status:** 🔵 Upstream  

**Symptom**  
In GNOME Settings, some panels support swipe-back gesture navigation and some do not. Navigation is inconsistent and confusing on a touchscreen device.

**Steps to reproduce**  
1. Open GNOME Settings  
2. Navigate into a panel (e.g. Wi-Fi)  
3. Attempt swipe-back gesture to return  
4. Gesture works in some panels, fails silently in others  

**Expected behaviour**  
All panels support consistent swipe-back navigation as expected on a mobile device.

**Root cause**  
gnome-control-center panels were written at different times with different libadwaita navigation patterns. Older panels do not use the newer `AdwNavigationView` which supports swipe-back.

**Fix / Workaround**  
None — use back button. Phosh uses a separate settings app built mobile-first and may not have this issue.

**Fix location**  
Upstream — GNOME / gnome-control-center  
Reference: https://gitlab.gnome.org/GNOME/gnome-control-center/-/issues/3608

**Consumer impact**  
2 — Inconsistent but functional. Back button works.

**Notes**  
Active upstream issue with no near-term fix. Another point in favour of Phosh for the consumer image. Document as known limitation.

---

### 005 — Waydroid — notifications not bridging to host shell

**Date discovered:** 2026-03-02  
**Reporter:** Connor  
**Device:** OnePlus 6T (fajita) / postmarketOS edge  
**Phase:** 0  
**Component:** Waydroid / notifications  
**Status:** 🟡 In Progress  

**Symptom**  
Notifications from Android apps running in Waydroid do not appear in the GNOME notification area. Users receive no alerts from WhatsApp, Signal, or other Android apps unless they have the Waydroid window open.

**Steps to reproduce**  
1. Start Waydroid session  
2. Install an Android app that sends notifications (e.g. WhatsApp)  
3. Trigger a notification (e.g. receive a message)  
4. No notification appears in GNOME shell — only visible inside the Waydroid window  

**Expected behaviour**  
Android app notifications should bridge to the host desktop notification system and appear in the GNOME notification area.

**Root cause**  
Under investigation. Waydroid notification bridging relies on `waydroid-notification-client` or similar tooling; not enabled or available by default on postmarketOS.

**Fix / Workaround**  
None confirmed yet. Investigation ongoing.

**Fix location**  
TBD — likely overlay config or additional service.

**Consumer impact**  
5 — Silently missed notifications from messaging apps makes the device unsuitable as a daily driver. Critical for WhatsApp use case.

**Notes**  
Key blocker for consumer readiness. Notification bridging is one of the more fragile parts of the Waydroid stack and may depend on waydroid-extras or a separate notification daemon. Follow up once networking (#001) is confirmed stable.

---
