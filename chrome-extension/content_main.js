function extractSongs() {
  if (typeof UGAPP === 'undefined') return { songs: [], debug: 'UGAPP not found' };

  const pageData = UGAPP?.store?.page?.data;
  if (!pageData) return { songs: [], debug: 'UGAPP.store.page.data not found' };

  const keys = Object.keys(pageData);
  let rawTabs = [];

  if (pageData.songbookTabs) {
    rawTabs = pageData.songbookTabs;
  } else if (pageData.playlist) {
    rawTabs = pageData.playlist.tabs || [];
  } else if (pageData.list) {
    rawTabs = pageData.list.list || [];
  } else {
    return { songs: [], debug: `Unknown page structure. pageData keys: ${keys.join(', ')}` };
  }

  const songs = rawTabs
    .map(t => ({
      song_name: t.song_name || t.name || 'Unknown Song',
      band_name: t.band_name || t.artist_name || 'Unknown Artist',
      song_url: t.song_url || t.tab_url,
    }))
    .filter(t => t.song_url);

  return { songs, debug: `OK — key: ${keys.find(k => ['songbookTabs','playlist','list'].includes(k))}` };
}

window.addEventListener('UGS_GET_SONGS', () => {
  const result = extractSongs();
  window.dispatchEvent(new CustomEvent('UGS_SONGS_RESULT', { detail: result }));
});
