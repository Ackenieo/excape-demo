const { get, post, upload } = require('./http');
const { getDeviceId } = require('./game');
const AVATAR_UPLOAD_PATH = '/api/v1/uploads/avatar';

function normalizeAchievement(item) {
  const source = item || {};
  return {
    id: source.id || '',
    title: source.title || '暂无成就',
    description: source.description || source.desc || '',
    active: Boolean(source.active),
  };
}

function normalizeRecentRun(item) {
  const source = item || {};
  const levelName = source.levelName || source.name || '';
  const result = source.result || source.status || 'success';

  return {
    runId: source.runId || '',
    levelName,
    name: levelName
      ? `${levelName} · ${result === 'success' ? '通关' : '失败'}`
      : (source.name || '暂无记录'),
    result,
    score: typeof source.score === 'number' ? source.score : 0,
    createdAt: source.createdAt || '',
  };
}

function normalizeProfile(data) {
  const source = data || {};
  return {
    deviceId: source.deviceId || getDeviceId(),
    nickname: source.nickname || '匿名玩家',
    avatarUrl: source.avatarUrl || '',
    rankText: source.rankText || '',
    passedCount: typeof source.passedCount === 'number' ? source.passedCount : 0,
    totalScore: typeof source.totalScore === 'number' ? source.totalScore : 0,
    passRate: source.passRate || '0%',
    achievements: Array.isArray(source.achievements)
      ? source.achievements.map(normalizeAchievement)
      : [],
    recentRuns: Array.isArray(source.recentRuns)
      ? source.recentRuns.map(normalizeRecentRun)
      : [],
  };
}

async function getProfile() {
  const data = await get('/api/v1/profile', {
    deviceId: getDeviceId(),
  });

  return normalizeProfile(data);
}

async function updateAvatar(avatarUrl) {
  if (!avatarUrl) {
    throw {
      code: -4,
      message: '缺少头像地址',
    };
  }

  const data = await post('/api/v1/profile/avatar', {
    deviceId: getDeviceId(),
    avatarUrl,
  });

  return {
    avatarUrl: (data && data.avatarUrl) || avatarUrl,
    updatedAt: (data && data.updatedAt) || '',
  };
}

async function uploadAvatar(filePath) {
  if (!filePath) {
    throw {
      code: -4,
      message: '缺少头像文件',
    };
  }

  const data = await upload(AVATAR_UPLOAD_PATH, filePath, {
    name: 'file',
    formData: {
      deviceId: getDeviceId(),
      bizType: 'profile_avatar',
    },
  });

  const avatarUrl = (data && (data.url || data.avatarUrl)) || '';

  if (!avatarUrl) {
    throw {
      code: -3,
      message: '上传成功但未返回头像地址',
      data,
    };
  }

  return {
    avatarUrl,
    fileId: (data && data.fileId) || '',
    uploadedAt: (data && data.uploadedAt) || '',
  };
}

module.exports = {
  getProfile,
  uploadAvatar,
  updateAvatar,
  normalizeProfile,
};
