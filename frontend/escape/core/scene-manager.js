function createSceneManager() {
  return {
    current: 'home',
    payload: null,
    go(sceneName, payload) {
      this.current = sceneName;
      this.payload = payload || null;
    },
  };
}

module.exports = {
  createSceneManager,
};
