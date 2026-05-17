const DEFAULT_TIMEOUT = 10000;

const ERROR_CODES = {
  TIMEOUT: -1,
  NETWORK: -2,
  RESPONSE_FORMAT: -3,
  UNKNOWN: -4,
};

let baseURL = '';

function setBaseURL(nextBaseURL) {
  baseURL = String(nextBaseURL || '').replace(/\/+$/, '');
}

function getBaseURL() {
  return baseURL;
}

function buildQueryString(params) {
  if (!params) {
    return '';
  }

  const parts = Object.keys(params)
    .filter((key) => params[key] !== undefined && params[key] !== null)
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`);

  return parts.length ? `?${parts.join('&')}` : '';
}

function buildURL(url, query) {
  const normalizedPath = String(url || '');
  const prefix = baseURL ? `${baseURL}${normalizedPath}` : normalizedPath;
  return `${prefix}${buildQueryString(query)}`;
}

function createHttpError(code, message, extra) {
  return {
    code,
    message: message || '请求失败',
    ...(extra || {}),
  };
}

function parseResponseData(rawData) {
  if (typeof rawData !== 'string') {
    return rawData;
  }

  try {
    return JSON.parse(rawData);
  } catch (error) {
    throw createHttpError(
      ERROR_CODES.RESPONSE_FORMAT,
      '响应数据解析失败',
      { raw: rawData },
    );
  }
}

function unwrapResponse(responseData) {
  if (!responseData || typeof responseData !== 'object') {
    throw createHttpError(
      ERROR_CODES.RESPONSE_FORMAT,
      '响应结构不合法',
      { raw: responseData },
    );
  }

  const code = typeof responseData.code === 'number'
    ? responseData.code
    : ERROR_CODES.RESPONSE_FORMAT;
  const message = responseData.message || '请求失败';

  if (code !== 0) {
    throw createHttpError(code, message, {
      data: responseData.data,
      raw: responseData,
    });
  }

  return responseData.data;
}

function request(options) {
  const {
    url,
    method = 'GET',
    data,
    query,
    timeout = DEFAULT_TIMEOUT,
    header,
  } = options || {};

  if (!url) {
    return Promise.reject(
      createHttpError(ERROR_CODES.UNKNOWN, '缺少请求地址'),
    );
  }

  return new Promise((resolve, reject) => {
    tt.request({
      url: buildURL(url, query),
      method,
      data: data || {},
      timeout,
      header: {
        'content-type': 'application/json',
        ...(header || {}),
      },
      success(res) {
        if (!res || typeof res.statusCode !== 'number') {
          reject(createHttpError(
            ERROR_CODES.RESPONSE_FORMAT,
            '未获取到有效响应',
            { raw: res },
          ));
          return;
        }

        if (res.statusCode < 200 || res.statusCode >= 300) {
          reject(createHttpError(
            res.statusCode,
            `服务异常(${res.statusCode})`,
            { raw: res.data, statusCode: res.statusCode },
          ));
          return;
        }

        try {
          const result = unwrapResponse(parseResponseData(res.data));
          resolve(result);
        } catch (error) {
          reject(error);
        }
      },
      fail(error) {
        const errorMessage = String((error && error.errMsg) || '');
        const isTimeout = errorMessage.indexOf('timeout') !== -1;

        reject(createHttpError(
          isTimeout ? ERROR_CODES.TIMEOUT : ERROR_CODES.NETWORK,
          isTimeout ? '请求超时，请稍后重试' : '网络异常，请检查网络后重试',
          { raw: error },
        ));
      },
    });
  });
}

function upload(url, filePath, options) {
  const {
    name = 'file',
    formData,
    timeout = DEFAULT_TIMEOUT,
    header,
  } = options || {};

  if (!url) {
    return Promise.reject(
      createHttpError(ERROR_CODES.UNKNOWN, '缺少上传地址'),
    );
  }

  if (!filePath) {
    return Promise.reject(
      createHttpError(ERROR_CODES.UNKNOWN, '缺少上传文件'),
    );
  }

  if (!tt || typeof tt.uploadFile !== 'function') {
    return Promise.reject(
      createHttpError(ERROR_CODES.UNKNOWN, '当前环境不支持文件上传'),
    );
  }

  return new Promise((resolve, reject) => {
    tt.uploadFile({
      url: buildURL(url),
      filePath,
      name,
      formData: formData || {},
      timeout,
      header: {
        ...(header || {}),
      },
      success(res) {
        if (!res || typeof res.statusCode !== 'number') {
          reject(createHttpError(
            ERROR_CODES.RESPONSE_FORMAT,
            '未获取到有效上传响应',
            { raw: res },
          ));
          return;
        }

        if (res.statusCode < 200 || res.statusCode >= 300) {
          reject(createHttpError(
            res.statusCode,
            `上传失败(${res.statusCode})`,
            { raw: res.data, statusCode: res.statusCode },
          ));
          return;
        }

        try {
          const result = unwrapResponse(parseResponseData(res.data));
          resolve(result);
        } catch (error) {
          reject(error);
        }
      },
      fail(error) {
        const errorMessage = String((error && error.errMsg) || '');
        const isTimeout = errorMessage.indexOf('timeout') !== -1;

        reject(createHttpError(
          isTimeout ? ERROR_CODES.TIMEOUT : ERROR_CODES.NETWORK,
          isTimeout ? '上传超时，请稍后重试' : '上传失败，请检查网络后重试',
          { raw: error },
        ));
      },
    });
  });
}

function get(url, query, options) {
  return request({
    ...(options || {}),
    url,
    method: 'GET',
    query,
  });
}

function post(url, data, options) {
  return request({
    ...(options || {}),
    url,
    method: 'POST',
    data,
  });
}

module.exports = {
  ERROR_CODES,
  setBaseURL,
  getBaseURL,
  createHttpError,
  request,
  get,
  post,
  upload,
};
