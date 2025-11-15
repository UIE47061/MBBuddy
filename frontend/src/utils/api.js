// API 配置文件
// 動態檢測 API URL
export const getApiBaseUrl = () => {
  // 如果是開發環境的 5173 端口，使用 8001
  if (window.location.port === '5173') {
    return `${window.location.protocol}//${window.location.hostname}:8001`;
  }
  // 如果是生產環境的 80 端口，使用 8000
  return `${window.location.protocol}//${window.location.hostname}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();
