# Issue 003 — Call audio silent: callaudiod not switching PulseAudio to Voice Call profile

**Date:** 2026-03-01
**Device:** OnePlus 6T (fajita), postmarketOS edge, GNOME Mobile, systemd
**Severity:** Blocker
**Status:** Fixed

---

## Summary

Voice calls connect but produce no audio. callaudiod logs `no available output found / no available input found` on every call. The Voice Call UCM profile exists and works — callaudiod simply isn't switching to it.

---

## Steps to Reproduce

1. Flash postmarketOS edge on OnePlus 6T
2. Make or receive a phone call
3. Observe: no audio through earpiece, no mic input

## Expected

Audio routed through earpiece during calls, mic active, clear two-way conversation.

## Actual

Silence. callaudiod reports no available audio devices despite the hardware and UCM profiles being present and functional.

---

## Investigation

### PipeWire has no audio devices

`wpctl status` shows empty Audio section. Only video/camera devices visible. Initially suspected missing ALSA enumeration in PipeWire config.

### Two audio stacks present

The postmarketOS image uses `postmarketos-base-ui-audio-backend-pulseaudio` — PulseAudio owns the audio hardware. PipeWire handles video only. callaudiod uses the PulseAudio backend (`callaudiod-pulse`), not PipeWire directly. PipeWire having no audio was irrelevant.

### PulseAudio has everything needed

`pactl list cards` reveals:

```
Profiles:
  Voice Call: Make a phone call (sinks: 1, sources: 1, available: yes)
  HiFi: HiFi quality Music. (sinks: 2, sources: 3, available: yes)
Active Profile: HiFi

Ports:
  [Out] Earpiece (type: Earpiece) — Part of profile: Voice Call
  [In] Mic: Bottom Microphone — Part of profile: Voice Call
```

The Voice Call UCM profile is present and available. Manual switch confirms it works:

```bash
pactl set-card-profile alsa_card.platform-sound "Voice Call"
# Earpiece sink appears, clear audio on test call
```

### callaudiod not switching profiles

callaudiod's ModemManager integration is not functioning — it fails to switch PulseAudio to the Voice Call profile when a call becomes active. The exact failure mode is unclear but the result is it queries for voice sinks while HiFi is still active, finds none, and gives up.

### DBus signal analysis

Captured ModemManager `StateChanged` signals via dbus-monitor:

```
# Call becomes active:
interface=org.freedesktop.ModemManager1.Call member=StateChanged
  int32 3   # old state (ringing)
  int32 4   # new state (active)
  uint32 3  # reason

# Call terminates:
interface=org.freedesktop.ModemManager1.Call member=StateChanged
  int32 4   # old state (active)
  int32 7   # new state (terminated)
  uint32 0  # reason
```

---

## Fix

Shell script watching ModemManager DBus signals and switching PulseAudio profile:

**`/usr/local/bin/mahala-call-audio.sh`:**

```bash
#!/bin/sh
dbus-monitor --system \
  "type='signal',interface='org.freedesktop.ModemManager1.Call',member='StateChanged'" \
  2>/dev/null | \
while read -r line; do
    case "$line" in
        *"interface=org.freedesktop.ModemManager1.Call"*)
            read -r old_line
            read -r new_line
            read -r reason_line
            new_state=$(echo "$new_line" | grep -o '[0-9]*')
            if [ "$new_state" = "4" ]; then
                pactl set-card-profile alsa_card.platform-sound "Voice Call"
            elif [ "$new_state" = "7" ] || [ "$new_state" = "6" ]; then
                pactl set-card-profile alsa_card.platform-sound "HiFi"
            fi
            ;;
    esac
done
```

## Persistence

User systemd service at `~/.config/systemd/user/mahala-call-audio.service`:

```ini
[Unit]
Description=MahalaOS call audio profile switcher
After=pulseaudio.service

[Service]
Type=simple
ExecStart=/usr/local/bin/mahala-call-audio.sh
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

Enabled with: `systemctl --user enable --now mahala-call-audio.service`

---

## Upstream

- callaudiod ModemManager integration not functioning on postmarketOS with PulseAudio backend
- Worth filing upstream against callaudiod or postmarketOS
- This fix should work for any postmarketOS device using PulseAudio with a Voice Call UCM profile

## Notes

- `pipewire-tools` and `pipewire-echo-cancel` were also installed during investigation — these resolved the `pw-loopback: not found` errors in `call_audio_idle_suspend_workaround` and may contribute to audio quality
- The Voice Call UCM profile correctly maps to the earpiece and bottom microphone — hardware is fully functional
- Affects any postmarketOS user with a working Voice Call UCM profile but broken callaudiod integration
