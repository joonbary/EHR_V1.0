/**
 * Organization Chart Main Page Component
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, Tab, Box, Paper, Alert, Snackbar } from '@mui/material';
import OrgTree from '../../components/org/OrgTree';
import OrgMatrix from '../../components/org/OrgMatrix';
import OrgSidebar from '../../components/org/OrgSidebar';
import { orgApi } from '../../lib/orgApi';
import { OrgUnit, OrgSnapshot, OrgScenario } from '../../types/organization';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`org-tabpanel-${index}`}
      aria-labelledby={`org-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const OrganizationChart: React.FC = () => {
  // State Management
  const [tabValue, setTabValue] = useState(0);
  const [company, setCompany] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sandboxMode, setSandboxMode] = useState<boolean>(true);
  const [units, setUnits] = useState<OrgUnit[]>([]);
  const [treeData, setTreeData] = useState<any[]>([]);
  const [matrixData, setMatrixData] = useState<any>(null);
  const [snapshotA, setSnapshotA] = useState<OrgSnapshot | null>(null);
  const [snapshotB, setSnapshotB] = useState<OrgSnapshot | null>(null);
  const [scenarios, setScenarios] = useState<OrgScenario[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch Organization Units
  const fetchUnits = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await orgApi.getUnits({ company, q: searchQuery });
      setUnits(data);
    } catch (err: any) {
      setError(err.message || '조직 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [company, searchQuery]);

  // Fetch Tree Data
  const fetchTreeData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await orgApi.getTree({ company });
      setTreeData(data);
    } catch (err: any) {
      setError(err.message || '트리 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [company]);

  // Fetch Matrix Data
  const fetchMatrixData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await orgApi.getMatrix({ company });
      setMatrixData(data);
    } catch (err: any) {
      setError(err.message || '매트릭스 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [company]);

  // Fetch Scenarios
  const fetchScenarios = useCallback(async () => {
    try {
      const data = await orgApi.getScenarios();
      setScenarios(data);
    } catch (err: any) {
      console.error('Failed to fetch scenarios:', err);
    }
  }, []);

  // Initial Load
  useEffect(() => {
    fetchUnits();
    fetchTreeData();
    fetchMatrixData();
    fetchScenarios();
  }, [company, searchQuery]);

  // Handle Tab Change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle Unit Update (from drag and drop)
  const handleUnitUpdate = async (unitId: string, newReportsTo: string | null) => {
    if (!sandboxMode) {
      setError('샌드박스 모드에서만 조직 변경이 가능합니다.');
      return;
    }

    try {
      const result = await orgApi.whatIfReassign({
        unitId,
        newReportsTo
      });

      // Update local state with new data
      if (result.data) {
        // Update units and tree data based on result
        await fetchTreeData();
        setSuccess('조직 구조가 업데이트되었습니다.');
      }
    } catch (err: any) {
      setError(err.message || '조직 변경에 실패했습니다.');
    }
  };

  // Handle Snapshot Save
  const handleSnapshotSave = (type: 'A' | 'B') => {
    const snapshot: OrgSnapshot = {
      snapshot_id: Date.now().toString(),
      name: `Snapshot ${type}`,
      snapshot_type: 'WHATIF',
      data: units,
      created_at: new Date().toISOString()
    };

    if (type === 'A') {
      setSnapshotA(snapshot);
    } else {
      setSnapshotB(snapshot);
    }

    setSuccess(`스냅샷 ${type}가 저장되었습니다.`);
  };

  // Handle Snapshot Compare
  const handleSnapshotCompare = async () => {
    if (!snapshotA || !snapshotB) {
      setError('비교할 스냅샷을 먼저 저장해주세요.');
      return;
    }

    try {
      const diffs = await orgApi.compareSnapshots(
        snapshotA.snapshot_id,
        snapshotB.snapshot_id
      );
      
      // Show diffs in a dialog or panel
      console.log('Snapshot differences:', diffs);
      setSuccess('스냅샷 비교가 완료되었습니다.');
    } catch (err: any) {
      setError(err.message || '스냅샷 비교에 실패했습니다.');
    }
  };

  // Handle Scenario Save
  const handleScenarioSave = async (name: string, description: string) => {
    try {
      const scenario = await orgApi.saveScenario({
        name,
        description,
        payload: units
      });
      
      setScenarios([...scenarios, scenario]);
      setSuccess('시나리오가 저장되었습니다.');
    } catch (err: any) {
      setError(err.message || '시나리오 저장에 실패했습니다.');
    }
  };

  // Handle Scenario Load
  const handleScenarioLoad = async (scenarioId: string) => {
    try {
      const scenario = scenarios.find(s => s.scenario_id === scenarioId);
      if (scenario) {
        setUnits(scenario.payload);
        await fetchTreeData();
        setSuccess('시나리오가 로드되었습니다.');
      }
    } catch (err: any) {
      setError(err.message || '시나리오 로드에 실패했습니다.');
    }
  };

  // Handle Excel Import
  const handleExcelImport = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const result = await orgApi.importExcel(formData);
      await fetchUnits();
      await fetchTreeData();
      setSuccess(`엑셀 임포트 완료: ${result.created}개 생성, ${result.updated}개 업데이트`);
    } catch (err: any) {
      setError(err.message || '엑셀 임포트에 실패했습니다.');
    }
  };

  // Handle Excel Export
  const handleExcelExport = async () => {
    try {
      await orgApi.exportExcel({ company });
      setSuccess('엑셀 다운로드가 시작되었습니다.');
    } catch (err: any) {
      setError(err.message || '엑셀 익스포트에 실패했습니다.');
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Left Sidebar */}
      <OrgSidebar
        company={company}
        onCompanyChange={setCompany}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        sandboxMode={sandboxMode}
        onSandboxToggle={setSandboxMode}
        snapshotA={snapshotA}
        snapshotB={snapshotB}
        onSnapshotSave={handleSnapshotSave}
        onSnapshotCompare={handleSnapshotCompare}
        scenarios={scenarios}
        onScenarioSave={handleScenarioSave}
        onScenarioLoad={handleScenarioLoad}
        onExcelImport={handleExcelImport}
        onExcelExport={handleExcelExport}
      />

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <Paper sx={{ width: '100%', mb: 2 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab label="조직 트리" />
            <Tab label="기능 매트릭스" />
          </Tabs>
        </Paper>

        <TabPanel value={tabValue} index={0}>
          <OrgTree
            data={treeData}
            loading={loading}
            sandboxMode={sandboxMode}
            onNodeUpdate={handleUnitUpdate}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <OrgMatrix
            data={matrixData}
            loading={loading}
          />
        </TabPanel>
      </Box>

      {/* Notifications */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default OrganizationChart;