# Discord Call Recorder (Discord Audio Recorder)
Automatically record discord calls on PMs, DM Groups and even guilds (servers)
Pre-release has not been revealed yet - so stay tuned

### ⚠️ DISCLAIMER: USE AT YOUR OWN RISK
This project is a proof-of-concept for educational purposes only. It is a direct violation of [Discord's TOS](https://discord.com/terms) and should not be used.
Applying client modifications or "self-botting" (automating a user account)
**CAN AND WILL RESULT IN A PERMANENT BAN FROM DISCORD**

#### LEGAL WARNING: Recording, intercepting, or saving conversations without the consent of all parties may be illegal in your country. You are responsible for complying with all applicable laws.

# How it works
when you join and leave a discord call your client sends a request to a localserver that's running in background. recording your desktop audio and microphone and saving the records to the documents folder on your computer.
> PS. Pre-release supported clients will be: Discord, PTB, Canary (browsers still not supported)

## 🙏 Thanks to the people that made this possible
- Thanks to [Roger Pack](https://github.com/rdp) for providing the amazing [virtual-audio-capture driver](https://github.com/rdp/virtual-audio-capture-grabber-device)
- Thanks to [Jabka-M](https://github.com/Jabka-M) for providing the "idea" of the injection at repository [DiscordInject](https://github.com/Jabka-M/DiscordInject) (The idea was re-implamented by me in a pure pythonic way for higher compatibility)