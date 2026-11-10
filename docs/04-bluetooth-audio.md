# Realme neckband: reliable Bluetooth audio

## What the hardware can do

The **realme Buds Wireless 5 ANC**, model RMA2412 in the manufacturer's manual, lists **SBC and AAC**, with A2DP/HFP/AVRCP. Do not plan on LDAC, aptX or LE Audio just because the Bluetooth version is 5.4. Verify your unit matches that model. Pairing mode uses separated earbuds and a roughly six-second hold of the multifunction button until the green light flashes. [Realme user manual, manufacturer-authored PDF hosted by Amazon](https://m.media-amazon.com/images/I/81T2WcgkN5L.pdf).

Start with **A2DP AAC if offered**, then compare SBC on this machine. AAC is not automatically the more reliable or lower-latency option. ANC is performed by the neckband; Linux does not need an ANC driver. Use the vendor-supported phone app for device-specific options and firmware when available.

## Pair and select routes

1. Disconnect the neckband from your phone for the initial test; charge it sufficiently.
2. Use KDE System Settings → Bluetooth to pair. Select the Realme device as audio output.
3. Open `pavucontrol` → Configuration and choose its high-fidelity A2DP profile. Names depend on the installed stack; choose an offered profile, not an invented codec name.
4. Under Input Devices, select the laptop microphone. Select that same input explicitly in browser/call apps.
5. Play local audio, then a browser video. Test volume and play/pause buttons.

Useful inspection commands:

```bash
systemctl status bluetooth
systemctl --user status pipewire pipewire-pulse wireplumber
rfkill list
bluetoothctl show
wpctl status
pactl list cards
pactl list sinks
```

`pactl` works through PipeWire's PulseAudio-compatible server; installing a second PulseAudio server is unnecessary. Inspect `api.bluez5.codec` or equivalent properties with `wpctl inspect ID`, using the relevant ID from `wpctl status`. Codec visibility varies by version; the profile list in the GUI is also useful.

## Music quality and microphone tradeoff

Classic Bluetooth A2DP playback does not provide the neckband microphone. Recording through that microphone generally changes to HFP/HSP and reduces playback fidelity. For music while talking, use **neckband output + laptop/USB microphone**. For convenience while walking around, use the neckband microphone and accept the headset profile. [WirePlumber policy](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/settings.html).

Only if apps keep switching profiles unexpectedly, save the existing setting and disable automatic switching:

```bash
wpctl settings bluetooth.autoswitch-to-headset-profile
wpctl settings --save bluetooth.autoswitch-to-headset-profile false
```

Now select the A2DP output again. This makes automatic neckband-microphone use unavailable; use the laptop input or manually change profiles for a call. Restore normal automatic behavior with:

```bash
wpctl settings --save bluetooth.autoswitch-to-headset-profile true
```

These commands target WirePlumber 0.5, which is installed on the inspected machine. Do not paste legacy WirePlumber 0.4 Lua configuration into a 0.5 setup. Leave codec and hardware-quirk defaults alone initially. Enabling a codec in a configuration file cannot add headset support for it. [Bluetooth configuration](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/bluetooth.html).

## Diagnose dropouts in this order

| Symptom | First test | Next step |
|---|---|---|
| Sound becomes telephone-like | Close microphone-using apps; inspect profile | Select laptop mic and A2DP; test autoswitch setting |
| Dropouts during Wi-Fi transfers | Use 5 GHz Wi-Fi or Ethernet; stay near laptop | Disconnect phone multipoint; compare AAC/SBC |
| Connected but silent | Inspect default sink and per-app output in pavucontrol | Reconnect neckband, then restart user audio services |
| Stops after suspend | Compare current kernel with LTS; inspect logs | Full shutdown, then cold boot; record whether controller disappears |
| Adapter missing | `rfkill list`, `lsusb`, kernel logs | Update kernel/firmware coherently; test live media |
| High latency but clean sound | Compare a local file with video compensation | Use wired/USB audio for precise timing; a smaller PipeWire buffer cannot remove Bluetooth transport delay |

MediaTek MT7921 Wi-Fi and the associated Bluetooth radio share a congested band with 2.4 GHz Wi-Fi. Testing 5 GHz and single-device operation is a diagnostic, not a claim that your adapter is faulty. Do not globally disable USB autosuspend or force experimental Bluetooth features without logs indicating a specific need.

Recovery commands, **when no call or recording is active**:

```bash
systemctl --user restart pipewire pipewire-pulse wireplumber
# If reconnect still fails, this disconnects all Bluetooth peripherals:
sudo systemctl restart bluetooth
```

Collect relevant logs locally:

```bash
journalctl -b -u bluetooth --since '-15 min' --no-pager
journalctl --user -b -u wireplumber --since '-15 min' --no-pager
journalctl -k -b --no-pager | rg -i 'bluetooth|btusb|btmtk|mt7921|firmware'
```

Logs may include device addresses and names; redact before sharing. Avoid deleting all pairing records as a first repair step. If repair requires re-pairing, remove only this headset in KDE and pair it again.

## Acceptance matrix

Copy this into private notes and fill actual results. No listening tests have been performed for this guide.

| Test | Profile/codec | Main kernel | LTS kernel | Pass criterion |
|---|---|---|---|---|
| Local music, 30 minutes | A2DP AAC, then SBC | Pending | Pending | No audible dropouts |
| Music + compile + Wi-Fi | A2DP | Pending | Pending | No repeatable stutter |
| Browser call, laptop mic | A2DP output | Pending | Pending | Stereo output retained; input works |
| Browser call, neckband mic | HFP offered codec | Pending | Pending | Usable two-way speech |
| Five suspend/resume cycles | Chosen daily profile | Pending | Pending | Reconnect without service restart |
| Phone multipoint enabled | Chosen daily profile | Pending | Pending | Acceptable handover behavior |

If AAC fails but SBC passes, choose SBC. Stable audio is more useful than a codec badge.
