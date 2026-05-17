const { get, post } = require('./http');

function normalizeChallenge(data) {
  const source = data || {};

  return {
    code: source.code || '',
    title: source.title || '',
    targetLevelId: source.targetLevelId || '',
    description: source.description || '',
    shareTitle: source.shareTitle || '',
    creatorNickname: source.creatorNickname || source.nickname || '',
    sourceScore: typeof source.sourceScore === 'number'
      ? source.sourceScore
      : (typeof source.bestScore === 'number' ? source.bestScore : 0),
    expiresAt: source.expiresAt || '',
    nickname: source.nickname || source.creatorNickname || '',
    avatarUrl: source.avatarUrl || source.userAvatarUrl || '',
    rankText: source.rankText || '',
    passedCount: typeof source.passedCount === 'number' ? source.passedCount : 0,
    totalScore: typeof source.totalScore === 'number' ? source.totalScore : 0,
    passRate: source.passRate || '',
    achievements: Array.isArray(source.achievements) ? source.achievements : [],
    recentRuns: Array.isArray(source.recentRuns) ? source.recentRuns : [],
  };
}

async function createChallenge(run) {
  if (!run || !run.runId) {
    throw {
      code: -4,
      message: '缺少 runId，无法生成挑战',
    };
  }

  const data = await post('/api/v1/challenges', {
    runId: run.runId,
  });

  return normalizeChallenge(data);
}

async function getChallengeByCode(code) {
  if (!code) {
    throw {
      code: -4,
      message: '缺少 challengeCode，无法获取挑战详情',
    };
  }

  const data = await get(`/api/v1/challenges/${encodeURIComponent(code)}`);
  return normalizeChallenge(data);
}

async function getChallengeDetail(input) {
  if (input && typeof input === 'object' && input.runId) {
    return createChallenge(input);
  }

  if (typeof input === 'string' && input.indexOf('NPC-') === 0) {
    return getChallengeByCode(input);
  }

  throw {
    code: -4,
    message: '挑战参数不合法',
  };
}

module.exports = {
  createChallenge,
  getChallengeByCode,
  getChallengeDetail,
};
