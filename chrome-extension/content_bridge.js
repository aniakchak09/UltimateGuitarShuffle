chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_SONGS') {
    window.addEventListener('UGS_SONGS_RESULT', (e) => {
      sendResponse(e.detail);
    }, { once: true });
    window.dispatchEvent(new Event('UGS_GET_SONGS'));
    return true; // keep message channel open for async response
  }
});
