(function() {
    'use strict';

    if (window.stopVoiceListener) {
        console.warn("[VoiceListener] Listener is already running. Stopping previous instance...");
        window.stopVoiceListener();
    }

    function initializeListener() {

        console.log("[VoiceListener] Starting listener logic in Console.");
        injectStyles();

        // Custom Element ID for the recording indicator button
        const INDICATOR_ID = 'voice-listener-recording-indicator';
        const MENU_ID = 'voice-listener-menu';

        // -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= CRITICAL SECTION -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        // Element that holds the user area (where voice status is shown)
        const USER_AREA_SELECTOR = '[aria-label="User area"]';

        // Element that points on "Voice Connected" indicator
        const CONNECTED_INDICATOR_SELECTOR = '[class*="rtcConnectionStatusConnected"]';

        // Element that holds the disconnect & Krisp button
        const VOICE_BUTTONS_CONTAINER_SELECTOR = '[class*="voiceButtonsContainer"]';

        // Element for one of the buttons within the voice buttons container
        const INDICATOR_BUTTON_ELEMENT_APPEND_CLASS = '[class*="contents"]';

        // Element for channel name (Server+Channel/PM)
        const CHANNEL_NAME_SELECTOR = '[class*="lineClamp1"]';
        // -=-=-=-=-=-=-=-=-=-=-=-=-=-=-= [END] CRITICAL SECTION [END] -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

        let wasConnected = false;
        let lastChannelId = null;

        let isRecordingPaused = false;
        let currentServerId = 'N/A';
        let currentChannelId = 'Unknown';
        let currentChannelName = 'Unknown Channel';

        const documentClickListener = (e) => {
            const menu = document.getElementById(MENU_ID);
            const button = document.getElementById(INDICATOR_ID);
            if (menu && !menu.classList.contains('hidden')) {
                if (!menu.contains(e.target) && (!button || !button.contains(e.target))) {
                    menu.classList.add('hidden');
                }
            }
        };
        document.addEventListener('click', documentClickListener);

        function checkUiForVoiceState() {
            const userArea = document.querySelector(USER_AREA_SELECTOR);
            const isConnected = userArea ? !!userArea.querySelector(CONNECTED_INDICATOR_SELECTOR) : false;

            if (isConnected && userArea) {
                const channelLink = userArea.querySelector('a');
                const channelNameElement = userArea.querySelector(CHANNEL_NAME_SELECTOR);

                if (channelLink && channelLink.href) {
                    const match = channelLink.href.match(/\/channels\/(@me|\d+)\/(\d+)/);
                    if (match && match.length === 3) {
                        currentServerId = match[1];
                        currentChannelId = match[2];
                    }
                }
                if (channelNameElement) currentChannelName = channelNameElement.textContent;
            }

            if (isConnected === wasConnected) return;

            if (isConnected) {
                console.log("[VoiceListener] Detected Voice Connection. Attempting to inject UI...");
                const voiceButtonsContainer = userArea.querySelector(VOICE_BUTTONS_CONTAINER_SELECTOR);
                if (!voiceButtonsContainer) return;

                if (!document.getElementById(INDICATOR_ID)) {
                    const referenceButton = voiceButtonsContainer.querySelector('button');
                    const contentsDiv = referenceButton ? referenceButton.querySelector(INDICATOR_BUTTON_ELEMENT_APPEND_CLASS) : null;

                    if (referenceButton && contentsDiv) {
                        const dynamicIndicatorHtml = `
                            <button id="${INDICATOR_ID}" title="Recording Options" type="button" class="${referenceButton.className}">
                              <div class="${contentsDiv.className}">
                                <div class="recording-wrapper" style="width: 15px; height: 15px; position: relative;">
                                  <div class="recording-dot"></div>
                                  <div class="circle"></div>
                                  <div class="circle"></div>
                                  <div class="circle"></div>
                                </div>
                              </div>
                            </button>
                        `;
                        voiceButtonsContainer.insertAdjacentHTML('afterbegin', dynamicIndicatorHtml);
                        console.log("[VoiceListener] UI Injected successfully.");

                        if (!document.getElementById(MENU_ID)) {
                            const menuHtml = `
                                <div id="${MENU_ID}" class="voice-listener-menu hidden">
                                    <div id="menu-github" class="voice-listener-menu-item">Open Github Project</div>
                                    <div id="menu-toggle-record" class="voice-listener-menu-item">Stop Recording</div>
                                </div>
                            `;
                            document.body.insertAdjacentHTML('beforeend', menuHtml);

                            const githubItem = document.getElementById('menu-github');
                            const toggleItem = document.getElementById('menu-toggle-record');
                            const menu = document.getElementById(MENU_ID);

                            if (githubItem) {
                                githubItem.addEventListener('click', () => {
                                    window.open('https://github.com/agamsol/discord-call-recorder', '_blank');
                                    menu.classList.add('hidden');
                                });
                            }

                            if (toggleItem) {
                                toggleItem.addEventListener('click', (e) => {
                                    e.stopPropagation();

                                    isRecordingPaused = !isRecordingPaused;

                                    const btn = document.getElementById(INDICATOR_ID);
                                    if (btn) {
                                        const dot = btn.querySelector('.recording-dot');
                                        const circles = btn.querySelectorAll('.circle');

                                        if (isRecordingPaused) {
                                            if(dot) dot.classList.add('paused');
                                            circles.forEach(c => c.classList.add('paused'));

                                            sendWebhook('leave', {
                                                build: (window.GLOBAL_ENV && window.GLOBAL_ENV.RELEASE_CHANNEL) || 'unknown',
                                                event: 'LEAVE',
                                                channel_id: currentChannelId,
                                                timestamp: Date.now()
                                            });
                                        } else {
                                            if(dot) dot.classList.remove('paused');
                                            circles.forEach(c => c.classList.remove('paused'));

                                            sendWebhook('join', {
                                                build: (window.GLOBAL_ENV && window.GLOBAL_ENV.RELEASE_CHANNEL) || 'unknown',
                                                event: 'JOIN',
                                                server_id: currentServerId,
                                                channel_id: currentChannelId,
                                                channel_name: currentChannelName,
                                                timestamp: Date.now()
                                            });
                                        }
                                    }
                                    menu.classList.add('hidden');
                                });
                            }
                        }

                        const newButton = document.getElementById(INDICATOR_ID);
                        if (newButton) {
                            newButton.addEventListener('click', (e) => {
                                e.preventDefault();
                                e.stopPropagation();

                                const menu = document.getElementById(MENU_ID);
                                const toggleItem = document.getElementById('menu-toggle-record');

                                if (menu) {
                                    if (menu.classList.contains('hidden')) {
                                        const rect = newButton.getBoundingClientRect();
                                        menu.style.bottom = (window.innerHeight - rect.top + 10) + 'px';
                                        menu.style.left = rect.left + 'px';

                                        if (toggleItem) {
                                            toggleItem.innerText = isRecordingPaused ? "Start Recording" : "Stop Recording";
                                        }

                                        menu.classList.remove('hidden');
                                    } else {
                                        menu.classList.add('hidden');
                                    }
                                }
                            });
                        }
                    }
                }

                if (!isRecordingPaused) {
                    sendWebhook('join', {
                        build: (window.GLOBAL_ENV && window.GLOBAL_ENV.RELEASE_CHANNEL) || 'unknown',
                        event: 'JOIN',
                        server_id: currentServerId,
                        channel_id: currentChannelId,
                        channel_name: currentChannelName,
                        timestamp: Date.now()
                    });
                }
                lastChannelId = currentChannelId;
            } else {
                console.log("[VoiceListener] Disconnected from Voice. Removing Recording DOT.");
                const indicator = document.getElementById(INDICATOR_ID);
                if (indicator) indicator.remove();

                const menu = document.getElementById(MENU_ID);
                if (menu) menu.remove();

                sendWebhook('leave', {
                    build: (window.GLOBAL_ENV && window.GLOBAL_ENV.RELEASE_CHANNEL) || 'unknown',
                    event: 'LEAVE',
                    channel_id: lastChannelId,
                    timestamp: Date.now()
                });
                lastChannelId = null;
                isRecordingPaused = false;
            }
            wasConnected = isConnected;
        }

        const mainIntervalId = setInterval(checkUiForVoiceState, 1000);

        window.stopVoiceListener = function() {
            if (mainIntervalId) clearInterval(mainIntervalId);
            const indicator = document.getElementById(INDICATOR_ID);
            if (indicator) indicator.remove();
            const menu = document.getElementById(MENU_ID);
            if (menu) menu.remove();
            const styles = document.getElementById('voice-listener-styles');
            if (styles) styles.remove();
            document.removeEventListener('click', documentClickListener);
            delete window.stopVoiceListener;
            console.log('[VoiceListener] Stopped.');
        };
        return true;
    }

    const INDICATOR_CSS = `
        .recording-dot { width: 15px; height: 15px; background-color: red; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: pulseDot 2s infinite; box-shadow: 0 0 10px rgba(255,0,0,0.4); }
        .circle { position: absolute; top: 50%; left: 50%; border: 1px solid red; border-radius: 50%; transform: translate(-50%, -50%) scale(1); opacity: 0.5; animation: pulseCircle 6s infinite; }
        .circle:nth-child(2) { animation-delay: 2s; } .circle:nth-child(3) { animation-delay: 4s; }
        @keyframes pulseDot { 0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; } 50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; } }
        @keyframes pulseCircle { 0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; } 70% { transform: translate(-50%, -50%) scale(3); opacity: 0; } 100% { transform: translate(-50%, -50%) scale(1); opacity: 0; } }

        /* New Styles for Paused State */
        .recording-dot.paused { background-color: gray !important; animation: none !important; box-shadow: none !important; }
        .circle.paused { display: none !important; }

        /* Menu Styles */
        .voice-listener-menu { position: fixed; background-color: #1e1f21; border-radius: 10px; box-shadow: 0 8px 16px rgba(0,0,0,0.24); padding: 6px 0; width: 180px; z-index: 10000; font-family: 'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 500; color: #dbdee1; }
        .voice-listener-menu.hidden { display: none !important; }
        .voice-listener-menu-item { padding: 8px 12px; cursor: pointer; display: block; user-select: none; }
        .voice-listener-menu-item:hover { background-color: #4752c4; color: white; }
    `;

    function injectStyles() {
        if (document.getElementById('voice-listener-styles')) return;
        const styleSheet = document.createElement("style");
        styleSheet.id = 'voice-listener-styles';
        styleSheet.innerText = INDICATOR_CSS;
        document.head.appendChild(styleSheet);
    }

    const WEBHOOK_BASE_URL = 'http://127.0.0.1:49151';
    function sendWebhook(endpoint, data) {
        console.log(`[VoiceListener] Sending ${endpoint} webhook...`, data);
        fetch(`${WEBHOOK_BASE_URL}/${endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
            .then(response => { if (!response.ok) console.error(`[VoiceListener] Backend error for '${endpoint}': ${response.status}`); })
            .catch(error => console.warn(`[VoiceListener] Failed to send '${endpoint}' event (Is your python server running?):`, error));
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
    console.log("[VoiceListener] Searching for Discord Webpack...");

    const startupInterval = setInterval(() => {
        attempts++;
        const webpackChunk = findWebpackChunk();
        if (webpackChunk) {
            window.webpackChunkdiscord_app = webpackChunk;
            if (initializeListener()) {
                clearInterval(startupInterval);
            } else if (attempts > maxAttempts) {
                console.error(`[VoiceListener] Found webpack but failed to find modules. Stopping.`);
                clearInterval(startupInterval);
            }
        } else if (attempts > maxAttempts) {
            console.error(`[VoiceListener] Failed to find webpack after ${maxAttempts} attempts. Stopping.`);
            clearInterval(startupInterval);
        }
    }, 1000);
})();