function createAppStore(systemInfo) {
  return {
    systemInfo,
    loading: false,
    levels: [],
    rankings: null,
    challenge: null,
    profile: null,
    customNpcDraft: null,
    customNpc: null,
    setLoading(value) {
      this.loading = value;
    },
    setLevels(levels) {
      this.levels = levels;
    },
    setRankings(rankings) {
      this.rankings = rankings;
    },
    setChallenge(challenge) {
      this.challenge = challenge;
    },
    setProfile(profile) {
      this.profile = profile;
    },
    setCustomNpcDraft(draft) {
      this.customNpcDraft = draft;
    },
    setCustomNpc(customNpc) {
      this.customNpc = customNpc;
    },
  };
}

module.exports = {
  createAppStore,
};
