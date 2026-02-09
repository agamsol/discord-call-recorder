# Discord Call Recorder 0.5 (Discord Audio Recorder)
Automatically record discord calls on PMs, DM Groups and even guilds (servers)

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-windows-informational?style=for-the-badge&logo=windows&logoColor=white)
![GitHub stars](https://img.shields.io/github/stars/agamsol/discord-call-recorder?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/agamsol/discord-call-recorder?style=for-the-badge)

</div>

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

## ⚙️ Installation And Deployment Process (0.5)
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


## 📰 Whats new in version 0.5
- Added automatic plugin updates from GitHub (configurable via `config.env`)
    - Set `FETCH_PLUGIN_UPDATES_FROM_GITHUB` to a raw URL to enable auto-plugin-updates on startup. (not backend updates)
    > PS. This is done because discord updates elements very often and people end up running backend with outdated plugin
- Major: Updated Discord Classes


<details>

<summary>View older versions</summary>


## 📰 Whats new in version 0.4
- Fixed discord startup with windows throwing an error (added handler to the injector)
- More builds are now supported `stable`, `ptb`, `canary`

    Modify under `config.env` (example: `DISCORD_BUILDS=stable, ptb, canary`)

## 📰 Whats new in version 0.3
- Fixed a bug that crashes the application when swapping a call (fast join and leave)
- Syncronos print caused delay at printing logs (switched to the logger library)

## 📰 Whats new in version 0.2
1. Patched the latest HTML Class element changes (Critical)
2. Saving the current record even on a restart/crash (by changing the format to mkv)
3. Pause & Resume the recording without leaving the call

</details>

## 🙏 Thanks to the people that made this possible
- Thanks to [Roger Pack](https://github.com/rdp) for providing the amazing [virtual-audio-capture driver](https://github.com/rdp/virtual-audio-capture-grabber-device)
- Thanks to [Jabka-M](https://github.com/Jabka-M) for providing the "idea" of the injection at repository [DiscordInject](https://github.com/Jabka-M/DiscordInject) (The idea was re-implamented by me in a pure pythonic way for higher compatibility)