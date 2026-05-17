const { createSceneManager } = require('./core/scene-manager');
const { createHomeScene } = require('./pages/home/index');
const { createGameScene } = require('./pages/game/index');
const { createResultScene } = require('./pages/result/index');
const { createRankScene } = require('./pages/rank/index');
const { createChallengeScene } = require('./pages/challenge/index');
const { createCustomNpcScene } = require('./pages/custom-npc/index');
const { createAppStore } = require('./store/app');
const { createRunStore } = require('./store/run');
const { loadLevels, createRun, sendPlayerLine } = require('./services/game');
const { getRankings } = require('./services/rank');
const { getProfile, uploadAvatar, updateAvatar } = require('./services/profile');
const { createCustomNpc } = require('./services/custom-npc');
const { setBaseURL } = require('./services/http');
const { CURRENT_ENV, getEnvConfig } = require('./config');

const APP_ENV = getEnvConfig();
const INPUT_MAX_LENGTH = 40;
const USER_AVATAR_STORAGE_KEY = 'npc_escape_user_avatar';
const NPC_AVATAR_GROUPS = {
  generic: ['images/隐藏1.png', 'images/隐藏2.png', 'images/隐藏3.png'],
  level_1: ['images/门卫1.png', 'images/门卫2.png', 'images/门卫2.png'],
  level_2: ['images/隐藏1.png', 'images/隐藏2.png', 'images/隐藏3.png'],
  level_3: ['images/隐藏1.png', 'images/隐藏2.png', 'images/隐藏3.png'],
  level_4: ['images/安保1.png', 'images/安保2.png', 'images/安保3.png'],
  level_5: ['images/林主任1.png', 'images/林主任2png.png', 'images/林主任3.png'],
  '门卫': ['images/门卫1.png', 'images/门卫2.png', 'images/门卫2.png'],
  '保安': ['images/安保1.png', 'images/安保2.png', 'images/安保3.png'],
  '林主任': ['images/林主任1.png', 'images/林主任2png.png', 'images/林主任3.png'],
  '冯律师': ['images/冯律师1.png', 'images/冯律师2.png', 'images/冯律师3.png'],
};
const CUSTOM_NPC_FIELD_CONFIGS = {
  name: {
    label: 'NPC 名称',
    defaultValue: '林队长',
    maxLength: 12,
  },
  role: {
    label: '身份设定',
    defaultValue: '夜班安保队长',
    maxLength: 24,
  },
  personality: {
    label: '性格描述',
    defaultValue: '谨慎、强势、重视规矩，但愿意听合理解释',
    maxLength: 40,
  },
  openingMessage: {
    label: '开场白',
    defaultValue: '证件、来访记录、预约信息，先拿出来。',
    maxLength: 40,
  },
  goal: {
    label: '本局目标',
    defaultValue: '说服他让你进入办公区',
    maxLength: 32,
  },
  maxTurns: {
    label: '最大句数',
    defaultValue: '5',
    maxLength: 2,
    keyboardType: 'number',
  },
};

function getTouchPoint(touch) {
  if (!touch) {
    return null;
  }

  const x = typeof touch.clientX === 'number'
    ? touch.clientX
    : (typeof touch.pageX === 'number' ? touch.pageX : touch.x);
  const y = typeof touch.clientY === 'number'
    ? touch.clientY
    : (typeof touch.pageY === 'number' ? touch.pageY : touch.y);

  if (typeof x !== 'number' || typeof y !== 'number') {
    return null;
  }

  return { x, y };
}

function getChosenImagePath(result) {
  if (!result || typeof result !== 'object') {
    return '';
  }

  if (Array.isArray(result.tempFilePaths) && result.tempFilePaths[0]) {
    return result.tempFilePaths[0];
  }

  if (Array.isArray(result.tempFiles) && result.tempFiles[0]) {
    return result.tempFiles[0].path || result.tempFiles[0].tempFilePath || '';
  }

  return result.filePath || '';
}

function isUserCancelError(error) {
  const message = String(
    (error && error.errMsg)
    || (error && error.message)
    || '',
  ).toLowerCase();

  return message.indexOf('cancel') !== -1;
}

function createDefaultCustomNpcDraft() {
  return {
    name: CUSTOM_NPC_FIELD_CONFIGS.name.defaultValue,
    role: CUSTOM_NPC_FIELD_CONFIGS.role.defaultValue,
    personality: CUSTOM_NPC_FIELD_CONFIGS.personality.defaultValue,
    openingMessage: CUSTOM_NPC_FIELD_CONFIGS.openingMessage.defaultValue,
    goal: CUSTOM_NPC_FIELD_CONFIGS.goal.defaultValue,
    maxTurns: CUSTOM_NPC_FIELD_CONFIGS.maxTurns.defaultValue,
  };
}

function buildCustomNpcLevel(customNpc) {
  const source = customNpc || {};
  return {
    id: source.npcId || 'custom_npc',
    name: source.name || '自定义 NPC',
    difficulty: typeof source.difficulty === 'number' ? source.difficulty : 3,
    goal: source.goal || '',
    intro: source.role || '自定义角色',
    scene: 'custom',
    avatarGroup: 'generic',
    maxTurns: typeof source.maxTurns === 'number' ? source.maxTurns : 5,
    openingMessage: source.openingMessage || '',
    status: 'active',
  };
}

class MiniGameApp {
  constructor() {
    this.systemInfo = tt.getSystemInfoSync();
    this.canvas = tt.createCanvas();
    this.ctx = this.canvas.getContext('2d');
    this.canvas.width = this.systemInfo.windowWidth;
    this.canvas.height = this.systemInfo.windowHeight;

    this.appStore = createAppStore(this.systemInfo);
    this.runStore = createRunStore();
    this.sceneManager = createSceneManager();
    this.isRunning = false;
    this.scenes = {};
    this.lastRenderTime = 0;
    this.lastKeyboardSubmittedValue = '';
    this.keyboardSession = null;
    this.imageCache = {};
    this.userAvatarUrl = this.readStoredUserAvatar();

    setBaseURL(APP_ENV.baseURL);
    if (APP_ENV.enableLog) {
      console.info(`[env] ${CURRENT_ENV}: ${APP_ENV.envName} -> ${APP_ENV.baseURL}`);
    }

    this.registerScenes();
    this.bindTouchEvents();
    this.bindKeyboardEvents();
  }

  readStoredUserAvatar() {
    try {
      return tt.getStorageSync(USER_AVATAR_STORAGE_KEY) || '';
    } catch (error) {
      console.warn('读取用户头像缓存失败', error);
      return '';
    }
  }

  setUserAvatar(url) {
    this.userAvatarUrl = url || '';
    try {
      tt.setStorageSync(USER_AVATAR_STORAGE_KEY, this.userAvatarUrl);
    } catch (error) {
      console.warn('写入用户头像缓存失败', error);
    }
  }

  getUserAvatarSource() {
    const profile = this.appStore.profile || {};
    if (profile.avatarUrl) {
      if (profile.avatarUrl !== this.userAvatarUrl) {
        this.setUserAvatar(profile.avatarUrl);
      }
      return profile.avatarUrl;
    }

    return this.userAvatarUrl || '';
  }

  setProfileAvatar(avatarUrl) {
    const currentProfile = this.appStore.profile || {};
    this.appStore.setProfile({
      ...currentProfile,
      avatarUrl: avatarUrl || '',
    });
    this.setUserAvatar(avatarUrl || '');
  }

  getCustomNpcDraft() {
    if (!this.appStore.customNpcDraft) {
      this.appStore.setCustomNpcDraft(createDefaultCustomNpcDraft());
    }

    return this.appStore.customNpcDraft;
  }

  updateCustomNpcDraft(patch) {
    const currentDraft = this.getCustomNpcDraft();
    this.appStore.setCustomNpcDraft({
      ...currentDraft,
      ...(patch || {}),
    });
  }

  getNpcEmotionStage(shakeValue) {
    if (shakeValue >= 67) {
      return 2;
    }

    if (shakeValue >= 34) {
      return 1;
    }

    return 0;
  }

  resolveNpcAvatarSource(level, shakeValue) {
    const levelId = level && level.id;
    const levelName = level && level.name ? String(level.name) : '';
    const avatarGroup = level && level.avatarGroup ? String(level.avatarGroup) : '';
    let group = null;

    if (avatarGroup && NPC_AVATAR_GROUPS[avatarGroup]) {
      group = NPC_AVATAR_GROUPS[avatarGroup];
    }

    if (!group && levelId && NPC_AVATAR_GROUPS[levelId]) {
      group = NPC_AVATAR_GROUPS[levelId];
    }

    if (!group) {
      group = Object.keys(NPC_AVATAR_GROUPS)
        .filter((key) => key !== 'generic' && key.indexOf('level_') !== 0)
        .map((key) => ({ key, value: NPC_AVATAR_GROUPS[key] }))
        .find((item) => levelName.indexOf(item.key) !== -1);
      group = group ? group.value : null;
    }

    if (!group) {
      group = NPC_AVATAR_GROUPS.generic;
    }

    return group[this.getNpcEmotionStage(shakeValue)] || group[group.length - 1] || '';
  }

  createCanvasImage() {
    if (typeof tt.createImage === 'function') {
      return tt.createImage();
    }

    if (this.canvas && typeof this.canvas.createImage === 'function') {
      return this.canvas.createImage();
    }

    return null;
  }

  getImageAsset(src) {
    if (!src) {
      return null;
    }

    const cached = this.imageCache[src];
    if (cached) {
      return cached.status === 'loaded' ? cached.image : null;
    }

    const image = this.createCanvasImage();
    if (!image) {
      return null;
    }

    const entry = {
      status: 'loading',
      image,
    };
    this.imageCache[src] = entry;

    image.onload = () => {
      entry.status = 'loaded';
    };

    image.onerror = (error) => {
      entry.status = 'error';
      console.warn('头像资源加载失败', src, error);
    };

    image.src = src;
    return null;
  }

  registerScenes() {
    this.scenes.home = createHomeScene(this);
    this.scenes.game = createGameScene(this);
    this.scenes.result = createResultScene(this);
    this.scenes.rank = createRankScene(this);
    this.scenes.challenge = createChallengeScene(this);
    this.scenes.customNpc = createCustomNpcScene(this);
  }

  start() {
    this.isRunning = true;
    this.loop();

    this.bootstrap().catch((error) => {
      console.error('小游戏启动失败', error);
      this.appStore.setLoading(false);
      this.navigate('home');
      this.showToast((error && error.message) || '启动失败，请检查网络');
    });
  }

  async bootstrap() {
    this.appStore.setLoading(true);
    const levels = await loadLevels();
    this.appStore.setLevels(levels);
    this.sceneManager.go('home');
    this.appStore.setLoading(false);
  }

  bindTouchEvents() {
    tt.onTouchStart((event) => {
      const touch = event.touches && event.touches[0];
      const point = getTouchPoint(touch);
      if (!point) {
        return;
      }

      const activeScene = this.getActiveScene();
      if (!activeScene) {
        return;
      }

      if (typeof activeScene.onTouchStart === 'function') {
        activeScene.onTouchStart(point);
        return;
      }

      if (typeof activeScene.onTap === 'function') {
        activeScene.onTap(point);
      }
    });

    if (typeof tt.onTouchMove === 'function') {
      tt.onTouchMove((event) => {
        const touch = event.touches && event.touches[0];
        const activeScene = this.getActiveScene();
        const point = getTouchPoint(touch);
        if (!point || !activeScene || typeof activeScene.onTouchMove !== 'function') {
          return;
        }

        activeScene.onTouchMove(point);
      });
    }

    if (typeof tt.onTouchEnd === 'function') {
      tt.onTouchEnd((event) => {
        const touch = event.changedTouches && event.changedTouches[0];
        const activeScene = this.getActiveScene();
        const point = getTouchPoint(touch);
        if (!point || !activeScene) {
          return;
        }

        if (typeof activeScene.onTouchEnd === 'function') {
          activeScene.onTouchEnd(point);
          return;
        }

        if (typeof activeScene.onTap === 'function') {
          activeScene.onTap(point);
        }
      });
    }
  }

  bindKeyboardEvents() {
    if (typeof tt.onKeyboardInput === 'function') {
      tt.onKeyboardInput((event) => {
        if (this.keyboardSession) {
          this.keyboardSession.value = (event && event.value) || '';
          return;
        }

        this.runStore.setInputDraft((event && event.value) || '');
      });
    }

    if (typeof tt.onKeyboardConfirm === 'function') {
      tt.onKeyboardConfirm((event) => {
        const value = ((event && event.value) || '').trim();
        this.lastKeyboardSubmittedValue = value;

        if (this.keyboardSession) {
          this.keyboardSession.confirmed = true;
          if (typeof this.keyboardSession.onConfirm === 'function') {
            this.keyboardSession.onConfirm(value);
          }
          return;
        }

        this.submitDraftMessage(value);
      });
    }

    if (typeof tt.onKeyboardComplete === 'function') {
      tt.onKeyboardComplete((event) => {
        const value = ((event && event.value) || '').trim();

        if (this.keyboardSession) {
          const session = this.keyboardSession;
          this.keyboardSession = null;
          if (typeof session.onComplete === 'function') {
            session.onComplete(value, session.confirmed === true);
          }
          this.lastKeyboardSubmittedValue = '';
          return;
        }

        this.runStore.setKeyboardVisible(false);

        if (value && value !== this.lastKeyboardSubmittedValue) {
          this.runStore.setInputDraft(value);
        }

        this.lastKeyboardSubmittedValue = '';
      });
    }
  }

  loop() {
    if (!this.isRunning) {
      return;
    }

    const now = Date.now();
    const delta = now - this.lastRenderTime;
    this.lastRenderTime = now;
    this.render(delta);
    requestAnimationFrame(() => this.loop());
  }

  render(delta) {
    const activeScene = this.getActiveScene();
    if (!activeScene) {
      return;
    }

    activeScene.render({
      ctx: this.ctx,
      canvas: this.canvas,
      width: this.canvas.width,
      height: this.canvas.height,
      delta,
    });
  }

  getActiveScene() {
    return this.scenes[this.sceneManager.current];
  }

  navigate(sceneName, payload) {
    this.sceneManager.go(sceneName, payload);
  }

  getScenePayload() {
    return this.sceneManager.payload;
  }

  async startRun(level, options) {
    this.appStore.setLoading(true);
    const run = await createRun(level, options);
    this.runStore.setCurrentRun(run);
    this.runStore.setInputDraft('');
    this.appStore.setLoading(false);
    this.navigate('game');
  }

  showToast(title) {
    if (typeof tt.showToast === 'function') {
      tt.showToast({
        title,
        icon: 'none',
      });
    }
  }

  openCustomNpc() {
    this.getCustomNpcDraft();
    this.navigate('customNpc');
  }

  startKeyboardSession(options) {
    if (typeof tt.showKeyboard !== 'function') {
      this.showToast('当前环境暂不支持输入');
      return;
    }

    const session = {
      value: (options && options.defaultValue) || '',
      confirmed: false,
      onConfirm: options && options.onConfirm,
      onComplete: options && options.onComplete,
    };
    this.keyboardSession = session;
    tt.showKeyboard({
      defaultValue: session.value,
      maxLength: (options && options.maxLength) || INPUT_MAX_LENGTH,
      multiple: false,
      confirmHold: false,
      confirmType: 'done',
      ...(options && options.keyboardType ? { confirmType: 'done' } : {}),
    });
  }

  editCustomNpcField(fieldKey) {
    const config = CUSTOM_NPC_FIELD_CONFIGS[fieldKey];
    if (!config) {
      return;
    }

    const draft = this.getCustomNpcDraft();
    this.showToast(`请输入${config.label}`);
    this.startKeyboardSession({
      defaultValue: String(draft[fieldKey] || ''),
      maxLength: config.maxLength,
      onConfirm: (value) => {
        this.applyCustomNpcField(fieldKey, value);
      },
      onComplete: (value, confirmed) => {
        if (!confirmed && value) {
          this.applyCustomNpcField(fieldKey, value);
        }
      },
    });
  }

  applyCustomNpcField(fieldKey, value) {
    if (fieldKey === 'maxTurns') {
      const parsed = Math.max(3, Math.min(10, Number(value) || 5));
      this.updateCustomNpcDraft({
        maxTurns: String(parsed),
      });
      return;
    }

    this.updateCustomNpcDraft({
      [fieldKey]: String(value || '').trim(),
    });
  }

  async submitCustomNpc() {
    const draft = this.getCustomNpcDraft();
    const requiredKeys = ['name', 'role', 'personality', 'openingMessage', 'goal', 'maxTurns'];
    const missingField = requiredKeys.find((key) => !String(draft[key] || '').trim());
    if (missingField) {
      this.showToast(`请先补全${CUSTOM_NPC_FIELD_CONFIGS[missingField].label}`);
      return;
    }

    this.appStore.setLoading(true);
    try {
      const customNpc = await createCustomNpc({
        ...draft,
        maxTurns: Math.max(3, Math.min(10, Number(draft.maxTurns) || 5)),
      });
      this.appStore.setCustomNpc(customNpc);
      this.appStore.setCustomNpcDraft(createDefaultCustomNpcDraft());
      this.navigate('home');
      this.showToast('自定义 NPC 创建成功');
    } catch (error) {
      this.showToast((error && error.message) || '创建失败，请稍后重试');
    } finally {
      this.appStore.setLoading(false);
    }
  }

  async startCustomNpc(customNpc) {
    if (!customNpc || !customNpc.npcId) {
      this.showToast('请先创建自定义 NPC');
      return;
    }

    const customLevel = buildCustomNpcLevel(customNpc);
    this.appStore.setLoading(true);
    try {
      const run = await createRun(customLevel, {
        npcId: customNpc.npcId,
      });
      this.runStore.setCurrentRun(run);
      this.runStore.setInputDraft('');
      this.navigate('game');
    } catch (error) {
      this.showToast((error && error.message) || '后端暂未开放自定义 NPC 开局');
    } finally {
      this.appStore.setLoading(false);
    }
  }

  chooseAvatarImage() {
    if (typeof tt.chooseImage !== 'function') {
      return Promise.reject({
        code: -4,
        message: '当前环境暂不支持选图',
      });
    }

    return new Promise((resolve, reject) => {
      tt.chooseImage({
        count: 1,
        sourceType: ['album', 'camera'],
        success: (result) => {
          const filePath = getChosenImagePath(result);
          if (!filePath) {
            reject({
              code: -4,
              message: '未获取到头像文件',
            });
            return;
          }
          resolve(filePath);
        },
        fail: reject,
      });
    });
  }

  async changeAvatar() {
    if (this.appStore.loading) {
      return;
    }

    this.appStore.setLoading(true);

    try {
      const filePath = await this.chooseAvatarImage();
      const uploaded = await uploadAvatar(filePath);
      const updated = await updateAvatar(uploaded.avatarUrl);
      const nextAvatarUrl = updated.avatarUrl || uploaded.avatarUrl;

      this.setProfileAvatar(nextAvatarUrl);
      this.showToast('头像更新成功');
    } catch (error) {
      if (!isUserCancelError(error)) {
        this.showToast((error && error.message) || '头像更新失败');
      }
    } finally {
      this.appStore.setLoading(false);
    }
  }

  openTextComposer() {
    const currentRun = this.runStore.currentRun;
    if (!currentRun || currentRun.status !== 'playing' || this.runStore.sending) {
      return;
    }

    if (this.sceneManager.current !== 'game' || this.runStore.keyboardVisible) {
      return;
    }

    if (typeof tt.showKeyboard !== 'function') {
      this.showToast('当前环境暂不支持输入');
      return;
    }

    this.runStore.setKeyboardVisible(true);
    tt.showKeyboard({
      defaultValue: this.runStore.inputDraft,
      maxLength: INPUT_MAX_LENGTH,
      multiple: false,
      confirmHold: false,
      confirmType: 'send',
    });
  }

  async submitDraftMessage(content) {
    const currentRun = this.runStore.currentRun;
    if (!currentRun || currentRun.status !== 'playing') {
      return;
    }

    const message = typeof content === 'string'
      ? content.trim()
      : this.runStore.inputDraft.trim();
    if (!message) {
      this.showToast('先输入你想说的话');
      return;
    }

    this.runStore.setSending(true);
    this.runStore.setInputDraft('');

    if (typeof tt.hideKeyboard === 'function') {
      tt.hideKeyboard();
    }

    try {
      const nextState = await sendPlayerLine(currentRun, message);
      this.runStore.setCurrentRun(nextState);
      this.runStore.setKeyboardVisible(false);

      if (nextState.status !== 'playing') {
        this.navigate('result');
      }
    } catch (error) {
      this.runStore.setInputDraft(message);
      this.showToast((error && error.message) || '发送失败，请稍后重试');
    } finally {
      this.runStore.setSending(false);
    }
  }

  async openRankings() {
    this.appStore.setLoading(true);
    const rankings = await getRankings();
    this.appStore.setRankings(rankings);
    this.appStore.setLoading(false);
    this.navigate('rank');
  }

  async openChallenge() {
    this.appStore.setLoading(true);
    try {
      const tasks = [
        getProfile().then((profile) => {
          this.appStore.setProfile(profile);
          if (profile.avatarUrl) {
            this.setUserAvatar(profile.avatarUrl);
          }
        }),
      ];

      if (!this.appStore.rankings) {
        tasks.push(
          getRankings().then((rankings) => {
            this.appStore.setRankings(rankings);
          })
        );
      }

      await Promise.all(tasks);
      this.navigate('challenge');
    } catch (error) {
      this.showToast((error && error.message) || '个人中心加载失败');
      this.navigate('challenge');
    } finally {
      this.appStore.setLoading(false);
    }
  }
}

module.exports = {
  MiniGameApp,
};
