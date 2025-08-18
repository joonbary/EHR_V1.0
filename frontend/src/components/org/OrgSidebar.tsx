/**
 * Organization Chart Sidebar Component
 */
import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Stack,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Chip,
  InputAdornment,
  Alert
} from '@mui/material';
import {
  Search,
  Save,
  CompareArrows,
  CloudUpload,
  CloudDownload,
  FolderOpen,
  Add,
  Refresh,
  FilterList,
  PlayArrow
} from '@mui/icons-material';
import { OrgSnapshot, OrgScenario } from '../../types/organization';

interface OrgSidebarProps {
  company: string;
  onCompanyChange: (company: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sandboxMode: boolean;
  onSandboxToggle: (enabled: boolean) => void;
  snapshotA: OrgSnapshot | null;
  snapshotB: OrgSnapshot | null;
  onSnapshotSave: (type: 'A' | 'B') => void;
  onSnapshotCompare: () => void;
  scenarios: OrgScenario[];
  onScenarioSave: (name: string, description: string) => void;
  onScenarioLoad: (scenarioId: string) => void;
  onExcelImport: (file: File) => void;
  onExcelExport: () => void;
}

const OrgSidebar: React.FC<OrgSidebarProps> = ({
  company,
  onCompanyChange,
  searchQuery,
  onSearchChange,
  sandboxMode,
  onSandboxToggle,
  snapshotA,
  snapshotB,
  onSnapshotSave,
  onSnapshotCompare,
  scenarios,
  onScenarioSave,
  onScenarioLoad,
  onExcelImport,
  onExcelExport,
}) => {
  const [scenarioDialogOpen, setScenarioDialogOpen] = useState(false);
  const [scenarioName, setScenarioName] = useState('');
  const [scenarioDescription, setScenarioDescription] = useState('');
  const [loadDialogOpen, setLoadDialogOpen] = useState(false);

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onExcelImport(file);
    }
  };

  // Handle scenario save
  const handleScenarioSave = () => {
    if (scenarioName.trim()) {
      onScenarioSave(scenarioName, scenarioDescription);
      setScenarioDialogOpen(false);
      setScenarioName('');
      setScenarioDescription('');
    }
  };

  return (
    <Paper
      sx={{
        width: 320,
        height: '100%',
        p: 2,
        overflow: 'auto',
        borderRadius: 0,
        borderRight: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Typography variant="h6" gutterBottom>
        조직도 관리
      </Typography>

      <Divider sx={{ my: 2 }} />

      {/* Company Filter */}
      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
        <InputLabel>회사 선택</InputLabel>
        <Select
          value={company}
          label="회사 선택"
          onChange={(e) => onCompanyChange(e.target.value)}
        >
          <MenuItem value="ALL">전체</MenuItem>
          <MenuItem value="OK저축은행">OK저축은행</MenuItem>
          <MenuItem value="OK캐피탈">OK캐피탈</MenuItem>
          <MenuItem value="OK금융그룹">OK금융그룹</MenuItem>
        </Select>
      </FormControl>

      {/* Search */}
      <TextField
        fullWidth
        size="small"
        placeholder="조직, 리더, 기능 검색..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 2 }}
      />

      {/* Sandbox Mode */}
      <FormControlLabel
        control={
          <Switch
            checked={sandboxMode}
            onChange={(e) => onSandboxToggle(e.target.checked)}
            color="primary"
          />
        }
        label="샌드박스 모드"
        sx={{ mb: 2 }}
      />

      {sandboxMode && (
        <Alert severity="info" sx={{ mb: 2 }}>
          샌드박스 모드에서는 조직 구조를 자유롭게 변경할 수 있습니다.
        </Alert>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Snapshot Management */}
      <Typography variant="subtitle2" gutterBottom>
        스냅샷 관리
      </Typography>

      <Stack spacing={1} sx={{ mb: 2 }}>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Save />}
            onClick={() => onSnapshotSave('A')}
            fullWidth
          >
            스냅샷 A 저장
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Save />}
            onClick={() => onSnapshotSave('B')}
            fullWidth
          >
            스냅샷 B 저장
          </Button>
        </Stack>

        {snapshotA && (
          <Chip
            label={`A: ${snapshotA.name}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        )}

        {snapshotB && (
          <Chip
            label={`B: ${snapshotB.name}`}
            size="small"
            color="secondary"
            variant="outlined"
          />
        )}

        <Button
          variant="contained"
          size="small"
          startIcon={<CompareArrows />}
          onClick={onSnapshotCompare}
          disabled={!snapshotA || !snapshotB}
          fullWidth
        >
          스냅샷 비교
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      {/* Scenario Management */}
      <Typography variant="subtitle2" gutterBottom>
        시나리오 관리
      </Typography>

      <Stack spacing={1} sx={{ mb: 2 }}>
        <Button
          variant="outlined"
          size="small"
          startIcon={<Add />}
          onClick={() => setScenarioDialogOpen(true)}
          fullWidth
        >
          시나리오 저장
        </Button>

        <Button
          variant="outlined"
          size="small"
          startIcon={<FolderOpen />}
          onClick={() => setLoadDialogOpen(true)}
          fullWidth
          disabled={scenarios.length === 0}
        >
          시나리오 불러오기 ({scenarios.length})
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      {/* Excel I/O */}
      <Typography variant="subtitle2" gutterBottom>
        엑셀 관리
      </Typography>

      <Stack spacing={1}>
        <Button
          variant="outlined"
          size="small"
          component="label"
          startIcon={<CloudUpload />}
          fullWidth
        >
          엑셀 업로드
          <input
            type="file"
            hidden
            accept=".xlsx,.xls"
            onChange={handleFileUpload}
          />
        </Button>

        <Button
          variant="outlined"
          size="small"
          startIcon={<CloudDownload />}
          onClick={onExcelExport}
          fullWidth
        >
          엑셀 다운로드
        </Button>
      </Stack>

      {/* Scenario Save Dialog */}
      <Dialog
        open={scenarioDialogOpen}
        onClose={() => setScenarioDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>시나리오 저장</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="시나리오 이름"
            fullWidth
            variant="outlined"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="설명"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={scenarioDescription}
            onChange={(e) => setScenarioDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScenarioDialogOpen(false)}>취소</Button>
          <Button onClick={handleScenarioSave} variant="contained">
            저장
          </Button>
        </DialogActions>
      </Dialog>

      {/* Scenario Load Dialog */}
      <Dialog
        open={loadDialogOpen}
        onClose={() => setLoadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>시나리오 불러오기</DialogTitle>
        <DialogContent>
          <List>
            {scenarios.map((scenario) => (
              <ListItemButton
                key={scenario.scenario_id}
                onClick={() => {
                  onScenarioLoad(scenario.scenario_id);
                  setLoadDialogOpen(false);
                }}
              >
                <ListItemText
                  primary={scenario.name}
                  secondary={
                    <>
                      {scenario.description}
                      <br />
                      <Typography variant="caption" color="text.secondary">
                        {new Date(scenario.created_at).toLocaleString()}
                      </Typography>
                    </>
                  }
                />
                {scenario.is_active && (
                  <Chip label="활성" size="small" color="success" />
                )}
              </ListItemButton>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLoadDialogOpen(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default OrgSidebar;