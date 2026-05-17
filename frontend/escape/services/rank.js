const { get } = require('./http');

async function getRankings(options) {
  const query = {
    scope: (options && options.scope) || 'overall',
  };

  if (options && options.levelId) {
    query.levelId = options.levelId;
  }

  const data = await get('/api/v1/rankings', query);

  return {
    overall: Array.isArray(data && data.overall) ? data.overall : [],
    stats: {
      playCount: data && data.stats ? data.stats.playCount : 0,
      passRate: data && data.stats ? data.stats.passRate : '0%',
      bestScore: data && data.stats ? data.stats.bestScore : 0,
    },
  };
}

module.exports = {
  getRankings,
};
