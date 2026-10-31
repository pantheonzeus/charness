// Presence helper for the cbrain console: facts only, one JSON object per line on stdout.
// Spawned and owned by webapp/presence.py; nothing is written to disk (presence stays in RAM).
//   {"t":"audio","inputs":[{"pid":1,"bundle":"…"}],"output":{"name":"…","transport":"bluetooth","headphones":true}}
//     emitted on any change (checked every 150 ms) and as a 5 s heartbeat
//   {"t":"wake"}                       the Mac woke from sleep
//   {"t":"hotkey","down":true|false}   Right Option held / released (push-to-talk); "cancel":true when a key was typed with it
//   {"t":"hotkey_ready"} / {"t":"hotkey_unavailable"}   Accessibility permission granted or not (asked once at start)
// Build: swiftc -O presence.swift -o bin/presence
import AppKit
import CoreAudio
import Foundation

setvbuf(stdout, nil, _IOLBF, 0)

func emit(_ obj: [String: Any]) {
    guard let d = try? JSONSerialization.data(withJSONObject: obj, options: .sortedKeys), let s = String(data: d, encoding: .utf8) else { return }
    print(s)
}

func addr(_ sel: AudioObjectPropertySelector, _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> AudioObjectPropertyAddress {
    AudioObjectPropertyAddress(mSelector: sel, mScope: scope, mElement: kAudioObjectPropertyElementMain)
}

func u32(_ obj: AudioObjectID, _ sel: AudioObjectPropertySelector, _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> UInt32 {
    var a = addr(sel, scope), v: UInt32 = 0, size = UInt32(MemoryLayout<UInt32>.size)
    return AudioObjectGetPropertyData(obj, &a, 0, nil, &size, &v) == noErr ? v : 0
}

func cfString(_ obj: AudioObjectID, _ sel: AudioObjectPropertySelector) -> String {
    var a = addr(sel), size = UInt32(MemoryLayout<Unmanaged<CFString>?>.size)
    var ref: Unmanaged<CFString>?
    guard AudioObjectGetPropertyData(obj, &a, 0, nil, &size, &ref) == noErr, let r = ref else { return "" }
    return r.takeRetainedValue() as String
}

func objectList(_ obj: AudioObjectID, _ sel: AudioObjectPropertySelector) -> [AudioObjectID] {
    var a = addr(sel), size: UInt32 = 0
    guard AudioObjectGetPropertyDataSize(obj, &a, 0, nil, &size) == noErr, size > 0 else { return [] }
    var ids = [AudioObjectID](repeating: 0, count: Int(size) / MemoryLayout<AudioObjectID>.size)
    return AudioObjectGetPropertyData(obj, &a, 0, nil, &size, &ids) == noErr ? ids : []
}

let system = AudioObjectID(kAudioObjectSystemObject)

func inputs() -> [[String: Any]] {
    objectList(system, kAudioHardwarePropertyProcessObjectList).compactMap { id in
        guard u32(id, kAudioProcessPropertyIsRunningInput) == 1 else { return nil }
        var a = addr(kAudioProcessPropertyPID), pid: pid_t = 0, size = UInt32(MemoryLayout<pid_t>.size)
        _ = AudioObjectGetPropertyData(id, &a, 0, nil, &size, &pid)
        return ["pid": Int(pid), "bundle": cfString(id, kAudioProcessPropertyBundleID)]
    }.sorted { ($0["pid"] as! Int) < ($1["pid"] as! Int) }
}

func output() -> [String: Any] {
    let dev = AudioObjectID(u32(system, kAudioHardwarePropertyDefaultOutputDevice))
    let transport: String
    switch u32(dev, kAudioDevicePropertyTransportType) {
    case kAudioDeviceTransportTypeBluetooth, kAudioDeviceTransportTypeBluetoothLE: transport = "bluetooth"
    case kAudioDeviceTransportTypeUSB: transport = "usb"
    case kAudioDeviceTransportTypeBuiltIn: transport = "builtin"
    case kAudioDeviceTransportTypeHDMI, kAudioDeviceTransportTypeDisplayPort: transport = "display"
    case kAudioDeviceTransportTypeAirPlay: transport = "airplay"
    default: transport = "other"
    }
    // Built-in output is a headset only when the jack's data source says headphones ('hdpn').
    let source = u32(dev, kAudioDevicePropertyDataSource, kAudioDevicePropertyScopeOutput)
    let headphones = transport == "bluetooth" || transport == "usb" || (transport == "builtin" && source == 0x6864_706E)
    return ["name": cfString(dev, kAudioObjectPropertyName), "transport": transport, "headphones": headphones]
}

var last = ""
var lastBeat = Date.distantPast
Timer.scheduledTimer(withTimeInterval: 0.15, repeats: true) { _ in
    let obj: [String: Any] = ["t": "audio", "inputs": inputs(), "output": output()]
    let key = (try? JSONSerialization.data(withJSONObject: obj, options: .sortedKeys)).flatMap { String(data: $0, encoding: .utf8) } ?? ""
    if key != last || Date().timeIntervalSince(lastBeat) > 5 {
        last = key; lastBeat = Date()
        emit(obj)
    }
}

NSWorkspace.shared.notificationCenter.addObserver(forName: NSWorkspace.didWakeNotification, object: nil, queue: .main) { _ in
    emit(["t": "wake"])
}

// Push-to-talk: hold Right Option (keyCode 61). A global monitor needs Accessibility permission.
// On a German layout Right Option is how @ [ ] { } | ~ € are typed: only a clean hold counts. "down" goes out
// after HOLD_S with no other key pressed; a key pressed after that cancels the take.
let trusted = AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary)
if trusted {
    emit(["t": "hotkey_ready"])
    let HOLD_S = 0.3
    var held = false, typed = false, sent = false, press = 0
    NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged) { e in
        guard e.keyCode == 61 else { return }
        let now = e.modifierFlags.contains(.option)
        if now == held { return }
        held = now
        if now {
            typed = false
            press += 1
            let me = press
            DispatchQueue.main.asyncAfter(deadline: .now() + HOLD_S) {
                if held && !typed && press == me { sent = true; emit(["t": "hotkey", "down": true]) }
            }
        } else if sent {
            sent = false
            emit(["t": "hotkey", "down": false])
        }
    }
    NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { _ in
        guard held else { return }
        typed = true
        if sent { sent = false; emit(["t": "hotkey", "down": false, "cancel": true]) }
    }
} else {
    emit(["t": "hotkey_unavailable"])
}

// Exit with the parent: when stdin closes, the server has gone.
FileHandle.standardInput.readabilityHandler = { h in if h.availableData.isEmpty { exit(0) } }

NSApplication.shared.setActivationPolicy(.prohibited)
NSApplication.shared.run()
