const { CURRENT_ENV } = require('./env');

const ENV_CONFIG = {
  dev: {
    envName: '开发环境',
    baseURL: 'http://673b010a.r33.cpolar.top',
    enableLog: true,
  },
  prod: {
    envName: '正式环境',
    baseURL: 'https://api.example.com',
    enableLog: false,
  },
};

function getEnvConfig() {
  return ENV_CONFIG[CURRENT_ENV] || ENV_CONFIG.dev;
}

module.exports = {
  CURRENT_ENV,
  ENV_CONFIG,
  getEnvConfig,
};
