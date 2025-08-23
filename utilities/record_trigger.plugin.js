/**
 * ===================================================================================
 *                  Discord-Call-Listener for discord-call-recorder
 * ===================================================================================
 *
 * HOW TO USE MANUALLY:
 * 1. Locate and open your Discord `index.js` file in the `discord_desktop_core` module.
 * 2. Copy and paste this ENTIRE code block at the VERY END of the file. (or require() its full file path)
 * 3. Save the file and restart Discord completely.
 */
const { app, BrowserWindow} = require("electron");

const listenerScript = `
(function() {
    'use strict';

    if (window.stopVoiceListener) {
        console.warn("[VoiceListener] Listener is already running.");
        return;
    }

    function initializeListener() {
        const ChannelStore = findModule(m => m.getChannel && m.getChannels);
        if (!ChannelStore) return false;

        console.log("[VoiceListener] Discord modules found. Starting listener.");
        injectStyles();

        const INDICATOR_ID = 'voice-listener-recording-indicator';
        const USER_AREA_SELECTOR = '[aria-label="User area"]';
        const CONNECTED_INDICATOR_SELECTOR = '[class*="rtcConnectionStatusConnected__"]';
        const VOICE_BUTTONS_CONTAINER_SELECTOR = '[class*="voiceButtonsContainer_"]';

        let wasConnected = false;
        let lastChannelId = null;

        function checkUiForVoiceState() {
            const userArea = document.querySelector(USER_AREA_SELECTOR);
            const isConnected = userArea ? !!userArea.querySelector(CONNECTED_INDICATOR_SELECTOR) : false;

            if (isConnected === wasConnected) return;

            if (isConnected) {
                const voiceButtonsContainer = userArea.querySelector(VOICE_BUTTONS_CONTAINER_SELECTOR);
                if (!voiceButtonsContainer) return;

                if (!document.getElementById(INDICATOR_ID)) {
                    const referenceButton = voiceButtonsContainer.querySelector('button');
                    const contentsDiv = referenceButton ? referenceButton.querySelector('[class*="contents__"]') : null;

                    if (referenceButton && contentsDiv) {
                        const dynamicIndicatorHtml = \`
                            <button id="\${INDICATOR_ID}" title="Discord Call Recorder By Agam Solomon" type="button" class="\${referenceButton.className}">
                              <div class="\${contentsDiv.className}">
                                <div class="recording-wrapper" style="width: 15px; height: 15px; position: relative;">
                                  <div class="recording-dot"></div>
                                  <div class="circle"></div>
                                  <div class="circle"></div>
                                  <div class="circle"></div>
                                </div>
                              </div>
                            </button>
                        \`;
                        voiceButtonsContainer.insertAdjacentHTML('afterbegin', dynamicIndicatorHtml);

                        const newButton = document.getElementById(INDICATOR_ID);
                        if (newButton) {
                            newButton.addEventListener('click', () => {
                                window.open('http://github.com/agamsol', '_blank');
                            });
                        }
                    }
                }

                const channelLink = userArea.querySelector('a');
                const channelNameElement = userArea.querySelector('[class*="subtext__"]');
                let channelId = 'Unknown', serverId = 'N/A', channelName = 'Unknown Channel';

                if (channelLink && channelLink.href) {
                    const match = channelLink.href.match(/\\/channels\\/(@me|\\d+)\\/(\\d+)/);
                    if (match && match.length === 3) {
                        serverId = match[1];
                        channelId = match[2];
                    }
                }
                if (channelNameElement) channelName = channelNameElement.textContent;

                sendWebhook('join', { build: window.GLOBAL_ENV.RELEASE_CHANNEL, event: 'JOIN', server_id: serverId, channel_id: channelId, channel_name: channelName, timestamp: Date.now() });
                lastChannelId = channelId;
            } else {
                const indicator = document.getElementById(INDICATOR_ID);
                if (indicator) indicator.remove();
                sendWebhook('leave', { build: window.GLOBAL_ENV.RELEASE_CHANNEL, event: 'LEAVE', channel_id: lastChannelId, timestamp: Date.now() });
                lastChannelId = null;
            }
            wasConnected = isConnected;
        }

        const mainIntervalId = setInterval(checkUiForVoiceState, 1000);

        window.stopVoiceListener = function() {
            if (mainIntervalId) clearInterval(mainIntervalId);
            const indicator = document.getElementById(INDICATOR_ID);
            if (indicator) indicator.remove();
            const styles = document.getElementById('voice-listener-styles');
            if (styles) styles.remove();
            delete window.stopVoiceListener;
            console.log('[VoiceListener] Stopped.');
        };
        return true;
    }

    const INDICATOR_CSS = \`
        .recording-dot { width: 15px; height: 15px; background-color: red; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: pulseDot 2s infinite; box-shadow: 0 0 10px rgba(255,0,0,0.4); }
        .circle { position: absolute; top: 50%; left: 50%; border: 1px solid red; border-radius: 50%; transform: translate(-50%, -50%) scale(1); opacity: 0.5; animation: pulseCircle 6s infinite; }
        .circle:nth-child(2) { animation-delay: 2s; } .circle:nth-child(3) { animation-delay: 4s; }
        @keyframes pulseDot { 0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; } 50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; } }
        @keyframes pulseCircle { 0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; } 70% { transform: translate(-50%, -50%) scale(3); opacity: 0; } 100% { transform: translate(-50%, -50%) scale(1); opacity: 0; } }
    \`;

    function injectStyles() {
        if (document.getElementById('voice-listener-styles')) return;
        const styleSheet = document.createElement("style");
        styleSheet.id = 'voice-listener-styles';
        styleSheet.innerText = INDICATOR_CSS;
        document.head.appendChild(styleSheet);
    }

    const WEBHOOK_BASE_URL = 'http://127.0.0.1:49151';
    function sendWebhook(endpoint, data) {
        fetch(\`\${WEBHOOK_BASE_URL}/\${endpoint}\`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
            .then(response => { if (!response.ok) console.error(\`[VoiceListener] Backend error for '\${endpoint}': \${response.status}\`); })
            .catch(error => console.error(\`[VoiceListener] Failed to send '\${endpoint}' event:\`, error));
    }

    function findModule(filter) {
        if (!window.webpackChunkdiscord_app) return null;
        const modules = window.webpackChunkdiscord_app.push([ [Math.random()], {}, (e) => e ]);
        window.webpackChunkdiscord_app.pop();
        for (const id in modules.c) {
            if (modules.c[id] && modules.c[id].exports) {
                const module = modules.c[id].exports;
                try {
                    if (module && filter(module)) return module;
                    if (module.default && filter(module.default)) return module.default;
                } catch (e) {}
            }
        }
        return null;
    }

    function findWebpackChunk() {
        const webpackGlobal = Object.keys(window).find(key => key.startsWith('webpackChunk') && typeof window[key] === 'object' && window[key].hasOwnProperty('push'));
        return window[webpackGlobal];
    }

    let attempts = 0;
    const maxAttempts = 30;
    console.log("[VoiceListener] Waiting for Discord to load...");
    const startupInterval = setInterval(() => {
        attempts++;
        const webpackChunk = findWebpackChunk();
        if (webpackChunk) {
            window.webpackChunkdiscord_app = webpackChunk;
            if (initializeListener()) {
                clearInterval(startupInterval);
            } else if (attempts > maxAttempts) {
                console.error(\`[VoiceListener] Found webpack but failed to find modules after \${maxAttempts} attempts. Halting.\`);
                clearInterval(startupInterval);
            }
        } else if (attempts > maxAttempts) {
            console.error(\`[VoiceListener] Failed to find webpack after \${maxAttempts} attempts. Halting.\`);
            clearInterval(startupInterval);
        }
    }, 1000);
})();
`;

// Handle the first discord's startup
let int = setInterval(() => {
    const window = Array.from(BrowserWindow.getAllWindows()).find(win => !win.title.toLowerCase().includes("update"));
    if (window === undefined) return;

    clearInterval(int);

    window.webContents.executeJavaScript(listenerScript);
}, 1000);

// Handle Discord Crashes and reloads
app.on('web-contents-created', (event, webContents) => {
    webContents.on('did-finish-load', () => {
        const url = webContents.getURL();
        if (url.startsWith('https://discord.com/channels')) {
            console.log(`[Injector] Discord window finished loading at ${url}. Injecting listener script.`);
            webContents.executeJavaScript(listenerScript).catch(err => {
                console.error('[Injector] Failed to inject script:', err);
            });
        }
    });
});
