/**
 * Centralized API Configuration for RoadAI Frontend
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  DETECT: `${API_BASE_URL}/api/v1/detect`,
  ANALYZE: `${API_BASE_URL}/api/v1/analyze`,
  ANALYSES: `${API_BASE_URL}/api/v1/analyses`,
};
