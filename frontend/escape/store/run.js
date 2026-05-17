function createRunStore() {
  return {
    currentRun: null,
    sending: false,
    inputDraft: '',
    keyboardVisible: false,
    setCurrentRun(run) {
      this.currentRun = run;
    },
    setSending(value) {
      this.sending = value;
    },
    setInputDraft(value) {
      this.inputDraft = value || '';
    },
    setKeyboardVisible(value) {
      this.keyboardVisible = Boolean(value);
    },
    reset() {
      this.currentRun = null;
      this.sending = false;
      this.inputDraft = '';
      this.keyboardVisible = false;
    },
  };
}

module.exports = {
  createRunStore,
};
