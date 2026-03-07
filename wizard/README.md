<<<<<<< HEAD
# MahalaOS Setup Wizard

First-boot setup experience for MahalaOS — a consumer-focused Linux phone OS built on postmarketOS.

## Structure

```
wizard/
├── mahalaos-wizard.py      # Main application entry point
├── screens/
│   ├── base.py             # Base screen class (shared layout/navigation)
│   ├── welcome.py          # Screen 1: Welcome
│   ├── language.py         # Screen 2: Language & Region [stub]
│   ├── wifi.py             # Screen 3: WiFi connection (nmcli)
│   ├── sim.py              # Screen 4: SIM detection [stub - ModemManager]
│   ├── honest.py           # Screen 5: What works / what doesn't
│   ├── whatsapp.py         # Screen 6: WhatsApp/Waydroid setup [stub]
│   └── done.py             # Screen 7: All done
├── data/
│   └── mahalaos-wizard.desktop   # Autostart entry
└── polkit/
    └── org.mahalaos.wizard.policy  # Polkit privileges
```

## Requirements

- Python 3.x
- GTK4 (`python-gobject` / `py3-gobject3` on Alpine/postmarketOS)
- libadwaita (`libadwaita` on Alpine)
- NetworkManager + nmcli (for WiFi screen)
- ModemManager (for SIM screen — stub for now)

Install on postmarketOS:
```sh
sudo apk add py3-gobject3 gtk4 libadwaita networkmanager
```

## Running

### Dev mode (for testing — bypasses completion check, allows window close):
```sh
python3 wizard/mahalaos-wizard.py --dev
```

### Production mode:
```sh
python3 wizard/mahalaos-wizard.py
```

### Reset wizard (to re-run on device):
```sh
sudo rm -f /var/lib/mahalaos/wizard-complete
```

## Deploy to Device

```sh
chmod +x deploy.sh
./deploy.sh user@172.16.42.1    # USB SSH default
```

## Screen Status

| Screen     | Status        | Notes                                      |
|------------|---------------|--------------------------------------------|
| Welcome    | ✅ Complete   |                                            |
| Language   | 🔧 Stub       | Shows placeholder values                   |
| WiFi       | ✅ Complete   | nmcli scan + connect + verify              |
| SIM        | 🔧 Stub       | Needs ModemManager DBus integration        |
| Honest     | ✅ Complete   | Feature status list                        |
| WhatsApp   | 🔧 Stub       | Needs Waydroid state check + launch        |
| Done       | ✅ Complete   | Flag file written, app quick-launch        |

## Completion Flag

The wizard writes `/var/lib/mahalaos/wizard-complete` on finish.
Autostart checks for this file before launching the wizard.
=======
# MahalaOS

**A Linux phone for normal people.**

> Mobile Linux is technically capable but nobody has packaged it for normal people. This project takes the best-supported hardware and best-supported software and creates an opinionated, preconfigured image that a non-technical person could use as their daily phone. The goal isn't perfection — it's reaching "good enough" across the things people actually do with their phones every day.

---

## The Problem

Apple and Google control the mobile experience for billions of people. Both ecosystems are closed, surveillance-friendly, and hostile to user freedom. Existing alternatives (GrapheneOS, /e/OS) are still Android underneath — still dependent on Google's AOSP releases, still playing within Google's rules.

Mobile Linux exists. The kernel works. The phone stack works. But nobody has made it usable for someone who doesn't know what a terminal is.

This project changes that.

## The Approach

We're not building an OS from scratch. We're curating and polishing what already exists:

- **Hardware:** OnePlus 6T (codename: fajita) — best mainline Linux support of any mainstream phone, real-phone build quality, £70-100 used
- **Base OS:** postmarketOS — Alpine Linux-based, the most active mobile Linux distribution
- **Shell:** Phosh — GNOME's mobile interface, the most mature Linux mobile UI
- **Android Compatibility:** Waydroid — run essential Android apps (WhatsApp, Messenger) in a seamless container
- **Philosophy:** One device, done well. No scope creep. Ship when it's good enough, not when it's perfect.

## Current Status

**Phase 0 — Foundation**

See [ROADMAP.md](ROADMAP.md) for the full plan and [GOOD_ENOUGH.md](GOOD_ENOUGH.md) for our definition of "done."

## Documentation

| Document | Description |
|----------|-------------|
| [GOOD_ENOUGH.md](GOOD_ENOUGH.md) | Pass/fail criteria for every feature — our definition of shippable |
| [ROADMAP.md](ROADMAP.md) | Phased plan from proof of concept to product |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to help — for coders and non-coders |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical overview of the software stack |
| [docs/install-guide.md](docs/install-guide.md) | How to flash the image on a OnePlus 6T |
| [docs/testing-checklist.md](docs/testing-checklist.md) | Weekly QA checklist |
| [docs/known-issues.md](docs/known-issues.md) | Current limitations and workarounds |

## Contributing

We need help from people with all skill levels — not just kernel hackers. See [CONTRIBUTING.md](CONTRIBUTING.md) for details, but in short:

- **Testers** — Use the phone daily, report what breaks
- **Developers** — C, Python, Vala, Rust — there's work at every layer
- **Designers** — The UI needs to feel as polished as iOS/Android
- **Writers** — Documentation, guides, blog posts
- **Translators** — If this is for everyone, it needs to speak their language

## Why Not Just Use...

| Project | Why we're different |
|---------|-------------------|
| GrapheneOS | Still Android. Still Google's AOSP. Still plays by Google's rules. |
| /e/OS | Same — degoogled Android, not a true alternative |
| PureOS (Librem 5) | Right philosophy, but £1100 for underpowered hardware few can afford |
| PinePhone | Developer tool, not a consumer device — hardware too weak for daily use |
| Ubuntu Touch | Community-maintained but small team, limited app strategy |
| postmarketOS (vanilla) | We build on top of this — our value is the curation, polish, and "it just works" experience |

## Licence

[TBD — likely GPLv3 for OS components, MIT for tooling]

## Contact

TBD
>>>>>>> origin/main
