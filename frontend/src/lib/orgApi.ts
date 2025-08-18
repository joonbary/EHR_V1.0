/**
 * Organization API Helper
 */
import axios from 'axios';
import { OrgUnit, OrgScenario, OrgSnapshot } from '../types/organization';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: `${API_BASE_URL}/organization`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const orgApi = {
  // Organization Units
  async getUnits(params?: { company?: string; q?: string }): Promise<OrgUnit[]> {
    const response = await api.get('/units/', { params });
    return response.data;
  },

  async getUnit(id: string): Promise<OrgUnit> {
    const response = await api.get(`/units/${id}/`);
    return response.data;
  },

  async createUnit(data: Partial<OrgUnit>): Promise<OrgUnit> {
    const response = await api.post('/units/', data);
    return response.data;
  },

  async updateUnit(id: string, data: Partial<OrgUnit>): Promise<OrgUnit> {
    const response = await api.patch(`/units/${id}/`, data);
    return response.data;
  },

  async deleteUnit(id: string): Promise<void> {
    await api.delete(`/units/${id}/`);
  },

  // Tree Structure
  async getTree(params?: { company?: string }): Promise<any[]> {
    const response = await api.get('/units/tree/', { params });
    return response.data;
  },

  // Matrix
  async getMatrix(params?: { company?: string }): Promise<any> {
    const response = await api.get('/units/group/matrix/', { params });
    return response.data;
  },

  // Scenarios
  async getScenarios(): Promise<OrgScenario[]> {
    const response = await api.get('/scenarios/');
    return response.data;
  },

  async getScenario(id: string): Promise<OrgScenario> {
    const response = await api.get(`/scenarios/${id}/`);
    return response.data;
  },

  async saveScenario(data: {
    name: string;
    description: string;
    payload: any[];
  }): Promise<OrgScenario> {
    const response = await api.post('/scenarios/', data);
    return response.data;
  },

  async applyScenario(id: string): Promise<{ status: string; message: string }> {
    const response = await api.post(`/scenarios/${id}/apply/`);
    return response.data;
  },

  async compareScenarios(
    scenarioA: string,
    scenarioB: string
  ): Promise<any[]> {
    const response = await api.post('/scenarios/diff/', {
      scenario_a: scenarioA,
      scenario_b: scenarioB,
    });
    return response.data;
  },

  // What-if Analysis
  async whatIfReassign(data: {
    unitId: string;
    newReportsTo: string | null;
  }): Promise<{ snapshot_id: string; data: any[] }> {
    const response = await api.post('/whatif/reassign/', data);
    return response.data;
  },

  // Snapshots
  async compareSnapshots(
    snapshotA: string,
    snapshotB: string
  ): Promise<any[]> {
    // This would typically call a snapshot comparison endpoint
    // For now, we'll use scenario comparison as a proxy
    return this.compareScenarios(snapshotA, snapshotB);
  },

  // Excel I/O
  async importExcel(formData: FormData): Promise<{
    status: string;
    created: number;
    updated: number;
    errors: string[];
  }> {
    const response = await api.post('/io/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async exportExcel(params?: { company?: string }): Promise<void> {
    const response = await api.get('/io/export/', {
      params,
      responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download',
      `organization_${new Date().toISOString().slice(0, 10)}.xlsx`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};