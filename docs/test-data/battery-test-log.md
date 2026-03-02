# MahalaOS Battery Test Log
### Device: OnePlus 6T (fajita) · postmarketOS edge · GNOME Mobile

---

## Standby Tests

| Date | Start % | Start Time | End % | End Time | Duration | Drain | Rate/hr | Conditions |
|---|---|---|---|---|---|---|---|---|
| 01/03/26 | 85% | 22:44 | 72% | 06:26 | 7h 42m | 13% | ~1.7% | WiFi + mobile data, screen off |
|  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |

---

## Active Use Tests

| Date | Test Type | Start % | End % | Duration | Drain | Rate/hr | Est. full battery life | Conditions |
|---|---|---|---|---|---|---|---|---|
| 02/03/26 | Medium | 63% | 53% | 30 mins | 10% | ~20% | ~5 hrs | YouTube + AirPods, 50% brightness |
| 02/03/26 | Heavy | 83% | 73% | 30 mins | 10% | ~20% | ~5 hrs | YouTube + AirPods + Waydroid/WhatsApp, 50% brightness |
|  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |

---

## Anomalies

| Date | Time | observed % | Notes |
|---|---|---|---|
| 02/03/26 | ~13:00 | 5% | Sudden drop from ~55% after Waydroid active. Recharged fine from 5%. Likely fuel gauge recalibration. Not repeated in subsequent tests. |
|  |  |  |  |

---

## Summary (update as data grows)

| Metric | Result | Target | Status |
|---|---|---|---|
| Standby (WiFi + data) | ~20 hrs | 24 hrs | ⚠️ Below target |
| Active use (mixed) | ~5 hrs | 8 hrs | ⚠️ Below target |
| Battery reporting stability | Mostly stable | Consistent | ⚠️ One anomaly observed |
| Charging behaviour | Normal | Normal | ✅ |

---

## Notes

- All tests conducted at 50% screen brightness unless stated
- AirPods used for audio tests (Bluetooth, SBC codec)
- Waydroid running GApps + WhatsApp unless stated
- Battery reporting may be inaccurate due to Qualcomm fuel gauge driver limitations on postmarketOS
- Suspend/deep sleep likely not fully implemented — contributes to higher than expected standby drain
