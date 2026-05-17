const { post } = require('./http');
const { getDeviceId } = require('./game');

function normalizeCustomNpc(data) {
  const source = data || {};

  return {
    npcId: source.npcId || '',
    name: source.name || '未命名 NPC',
    avatarUrl: source.avatarUrl || '',
    role: source.role || '',
    personality: source.personality || '',
    openingMessage: source.openingMessage || '',
    goal: source.goal || '',
    maxTurns: typeof source.maxTurns === 'number' ? source.maxTurns : 5,
    difficulty: typeof source.difficulty === 'number' ? source.difficulty : 3,
    createdAt: source.createdAt || '',
    runId: source.runId || '',
  };
}

function buildCustomNpcPayload(draft) {
  const source = draft || {};
  const payload = {
    deviceId: getDeviceId(),
    name: String(source.name || '').trim(),
    role: String(source.role || '').trim(),
    personality: String(source.personality || '').trim(),
    openingMessage: String(source.openingMessage || '').trim(),
    goal: String(source.goal || '').trim(),
    maxTurns: Number(source.maxTurns) || 5,
  };

  if (source.avatarUrl) {
    payload.avatarUrl = String(source.avatarUrl).trim();
  }

  if (typeof source.difficulty === 'number' && source.difficulty > 0) {
    payload.difficulty = source.difficulty;
  }

  if (source.systemPrompt) {
    payload.systemPrompt = String(source.systemPrompt).trim();
  }

  return payload;
}

async function createCustomNpc(draft) {
  const payload = buildCustomNpcPayload(draft);
  const data = await post('/api/v1/custom-npcs', payload);
  return normalizeCustomNpc(data);
}

module.exports = {
  createCustomNpc,
  normalizeCustomNpc,
  buildCustomNpcPayload,
};
