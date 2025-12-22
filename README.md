# Discord Call Recorder 0.2 (Discord Audio Recorder) - Pre-Release
Automatically record discord calls on PMs, DM Groups and even guilds (servers)

### ⚠️ DISCLAIMER: USE AT YOUR OWN RISK
This project is a proof-of-concept for educational purposes only. It is a direct violation of [Discord's TOS](https://discord.com/terms) and should not be used.
Applying client modifications or "self-botting" (automating a user account)
**CAN AND WILL RESULT IN A PERMANENT BAN FROM DISCORD**

#### LEGAL WARNING: Recording, intercepting, or saving conversations without the consent of all parties may be illegal in your country. You are responsible for complying with all applicable laws.

# Screenshots (Preview)
![Preview](https://cdn.agamsol.xyz/public/screenshots/discord-call-recorder-screenshots/preview.png) ![Preview-Menu](https://cdn.agamsol.xyz/public/screenshots/discord-call-recorder-screenshots/preview-sub.png)
# How it works
when you join and leave a discord call your client sends a request to a localserver that's running in background. recording your desktop audio and microphone and saving the records to the documents folder on your computer.
> PS. Stable discord is the only supported build for this release!

## ⚙️ Installation And Deployment Process (Version Pre-0.1)
- Clone the [repository](https://github.com/agamsol/discord-call-recorder.git)
`git clone https://github.com/agamsol/discord-call-recorder.git`
- install the virtual-audio-capturer driver _(for capturing desktop audio - aka person you are calling with)_:
run `install_virtual_audio_capturer.cmd` **As administrator** under `\bin\install_virtual_audio_capturer.cmd`)
- run `choose_audio_device.exe` and choose your microphone from the list
- run `main.exe` _(kill discord.exe and start again if running)_

## 🌅 Adding to startup (Optional)
- Create a shortcut of `main.exe` and put that in the following directory
- `%appdata%\Microsoft\Windows\Start Menu\Programs\Startup`

Feel free to report any bugs and don't forget to give a star if you are enjoying this project 💖

## 📰 Whats new in version 0.2
1. Patched the latest HTML Class element changes (Critical)
2. Saving the current record even on a restart/crash (by changing the format to mkv)
3. Pause & Resume the recording without leaving the call

## 🙏 Thanks to the people that made this possible
- Thanks to [Roger Pack](https://github.com/rdp) for providing the amazing [virtual-audio-capture driver](https://github.com/rdp/virtual-audio-capture-grabber-device)
- Thanks to [Jabka-M](https://github.com/Jabka-M) for providing the "idea" of the injection at repository [DiscordInject](https://github.com/Jabka-M/DiscordInject) (The idea was re-implamented by me in a pure pythonic way for higher compatibility)