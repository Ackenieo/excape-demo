const { get, post } = require('./http');

function getDeviceId() {
  const storageKey = 'npc_escape_device_id';

  try {
    const stored = tt.getStorageSync(storageKey);
    if (stored) {
      return stored;
    }
  } catch (error) {
    console.warn('读取 deviceId 失败', error);
  }

  const nextId = `tt_device_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

  try {
    tt.setStorageSync(storageKey, nextId);
  } catch (error) {
    console.warn('写入 deviceId 失败', error);
  }

  return nextId;
}

function normalizeLevelItem(item) {
  return {
    id: item.id,
    name: item.name,
    difficulty: item.difficulty,
    goal: item.goal,
    intro: item.intro || '',
    scene: item.scene || '',
    maxTurns: item.maxTurns || 0,
    openingMessage: item.openingMessage || '',
    status: item.status || 'active',
  };
}

function mergeMessages(currentRun, incomingMessages, playerInput) {
  const merged = currentRun && Array.isArray(currentRun.messages)
    ? currentRun.messages.slice()
    : [];

  if (playerInput) {
    merged.push({
      role: 'player',
      content: playerInput,
    });
  }

  incomingMessages.forEach((message) => {
    const lastMessage = merged[merged.length - 1];
    if (
      lastMessage &&
      lastMessage.role === message.role &&
      lastMessage.content === message.content
    ) {
      return;
    }

    merged.push(message);
  });

  return merged;
}

function normalizeRunState(rawRun, fallbackLevel, currentRun, playerInput) {
  const level = fallbackLevel || (currentRun && currentRun.level) || {
    id: rawRun.levelId,
    name: '',
    difficulty: 1,
    goal: '',
    intro: '',
    scene: '',
    maxTurns: rawRun.remainingTurns || 0,
    openingMessage: rawRun.openingMessage || '',
    status: 'active',
  };

  const incomingMessages = Array.isArray(rawRun.messages) ? rawRun.messages : [];
  const mergedMessages = mergeMessages(currentRun, incomingMessages, playerInput);
  const openingMessage = rawRun.openingMessage || level.openingMessage || '';

  if (!mergedMessages.length && openingMessage) {
    mergedMessages.push({
      role: 'npc',
      content: openingMessage,
    });
  }

  return {
    runId: rawRun.runId,
    levelId: rawRun.levelId || level.id,
    level: {
      ...level,
      id: rawRun.levelId || level.id,
      openingMessage,
    },
    status: rawRun.status || 'playing',
    remainingTurns: typeof rawRun.remainingTurns === 'number'
      ? rawRun.remainingTurns
      : (currentRun ? currentRun.remainingTurns : level.maxTurns),
    shakeValue: typeof rawRun.shakeValue === 'number' ? rawRun.shakeValue : 0,
    score: typeof rawRun.score === 'number' ? rawRun.score : 0,
    passed: Boolean(rawRun.passed),
    bestLine: rawRun.bestLine || '',
    finalReply: rawRun.finalReply || '',
    openingMessage,
    messages: mergedMessages,
    nextIndex: currentRun ? currentRun.nextIndex + 1 : 0,
    shakeDelta: typeof rawRun.shakeDelta === 'number' ? rawRun.shakeDelta : 0,
    bestLineUpdated: Boolean(rawRun.bestLineUpdated),
    assistantReply: rawRun.assistantReply || '',
  };
}

async function loadLevels() {
  const data = await get('/api/v1/levels');
  const items = Array.isArray(data && data.items) ? data.items : [];
  return items.map(normalizeLevelItem);
}

async function createRun(level, options) {
  const payload = {
    deviceId: getDeviceId(),
  };

  if (options && options.npcId) {
    payload.npcId = options.npcId;
  } else if (level && level.id) {
    payload.levelId = level.id;
  }

  const data = await post('/api/v1/runs', payload);

  return normalizeRunState(data, level, null);
}

async function sendPlayerLine(run, content) {
  const data = await post('/api/v1/chat/send', {
    runId: run.runId,
    content,
  });

  return normalizeRunState(data, run.level, run, content);
}

module.exports = {
  getDeviceId,
  loadLevels,
  createRun,
  sendPlayerLine,
  normalizeRunState,
};
