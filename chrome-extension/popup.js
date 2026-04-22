const status = document.getElementById('status');
const songCard = document.getElementById('song-card');
const songName = document.getElementById('song-name');
const bandName = document.getElementById('band-name');
const btnShuffle = document.getElementById('btn-shuffle');
const btnOpen = document.getElementById('btn-open');

let songs = [];
let currentSong = null;

async function getSeenSet() {
  const result = await chrome.storage.session.get('seen');
  return new Set(result.seen || []);
}

async function saveSeenSet(seen) {
  await chrome.storage.session.set({ seen: [...seen] });
}

async function pickSong() {
  let seen = await getSeenSet();
  const resetThreshold = Math.floor(songs.length / 2);

  if (seen.size >= resetThreshold) {
    seen = new Set();
  }

  const candidates = songs.filter(s => !seen.has(s.song_url));
  const song = candidates[Math.floor(Math.random() * candidates.length)];
  seen.add(song.song_url);
  await saveSeenSet(seen);
  return song;
}

async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab.url.includes('ultimate-guitar.com')) {
    status.textContent = 'Open a UG playlist or favorites page first.';
    btnShuffle.disabled = true;
    return;
  }

  chrome.tabs.sendMessage(tab.id, { type: 'GET_SONGS' }, async (response) => {
    if (chrome.runtime.lastError || !response) {
      status.textContent = 'Could not read page. Try refreshing.';
      return;
    }

    songs = response.songs;

    if (songs.length === 0) {
      status.textContent = `No songs found. Debug: ${response.debug}`;
      return;
    }

    status.textContent = `${songs.length} songs loaded.`;
    btnShuffle.disabled = false;
  });
}

btnShuffle.addEventListener('click', async () => {
  if (!songs.length) return;
  currentSong = await pickSong();

  songName.textContent = currentSong.song_name;
  bandName.textContent = currentSong.band_name;
  songCard.style.display = 'block';
  btnOpen.style.display = 'block';
  status.textContent = `${songs.length} songs loaded.`;
});

btnOpen.addEventListener('click', () => {
  if (currentSong?.song_url) {
    chrome.tabs.create({ url: currentSong.song_url });
  }
});

init();
