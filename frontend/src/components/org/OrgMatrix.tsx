/**
 * Organization Matrix Component
 */
import React from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
  CircularProgress,
  Tooltip,
  Popover,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { Group } from '@mui/icons-material';

interface MatrixCell {
  leader: string;
  headcount: number;
  units: string[];
}

interface MatrixRow {
  function: string;
  cells: MatrixCell[];
}

interface MatrixData {
  headers: string[];
  rows: MatrixRow[];
}

interface OrgMatrixProps {
  data: MatrixData | null;
  loading: boolean;
}

const OrgMatrix: React.FC<OrgMatrixProps> = ({ data, loading }) => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);
  const [selectedCell, setSelectedCell] = React.useState<MatrixCell | null>(null);

  const handleCellClick = (event: React.MouseEvent<HTMLElement>, cell: MatrixCell) => {
    if (cell.headcount > 0) {
      setAnchorEl(event.currentTarget);
      setSelectedCell(cell);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
    setSelectedCell(null);
  };

  const open = Boolean(anchorEl);

  // Get cell color based on headcount
  const getCellColor = (headcount: number) => {
    if (headcount === 0) return '#f5f5f5';
    if (headcount <= 5) return '#e3f2fd';
    if (headcount <= 10) return '#bbdefb';
    if (headcount <= 20) return '#90caf9';
    if (headcount <= 50) return '#64b5f6';
    return '#42a5f5';
  };

  // Get text color based on background
  const getTextColor = (headcount: number) => {
    if (headcount <= 10) return '#000';
    return '#fff';
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%' 
      }}>
        <Typography variant="h6" color="textSecondary">
          매트릭스 데이터가 없습니다.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 200px)' }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell 
                  sx={{ 
                    fontWeight: 'bold',
                    backgroundColor: '#f0f0f0',
                    minWidth: 150
                  }}
                >
                  기능 \ 리더
                </TableCell>
                {data.headers.map((header, index) => (
                  <TableCell
                    key={index}
                    align="center"
                    sx={{
                      fontWeight: 'bold',
                      backgroundColor: '#f0f0f0',
                      minWidth: 120,
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {header}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {data.rows.map((row, rowIndex) => (
                <TableRow key={rowIndex} hover>
                  <TableCell
                    component="th"
                    scope="row"
                    sx={{
                      fontWeight: 'bold',
                      backgroundColor: '#fafafa',
                      position: 'sticky',
                      left: 0,
                      zIndex: 1
                    }}
                  >
                    {row.function}
                  </TableCell>
                  {row.cells.map((cell, cellIndex) => (
                    <TableCell
                      key={cellIndex}
                      align="center"
                      sx={{
                        cursor: cell.headcount > 0 ? 'pointer' : 'default',
                        backgroundColor: getCellColor(cell.headcount),
                        color: getTextColor(cell.headcount),
                        transition: 'all 0.3s ease',
                        '&:hover': cell.headcount > 0 ? {
                          transform: 'scale(1.05)',
                          boxShadow: 2,
                          zIndex: 1,
                          position: 'relative'
                        } : {}
                      }}
                      onClick={(e) => handleCellClick(e, cell)}
                    >
                      {cell.headcount > 0 ? (
                        <Tooltip title={`${cell.units.length}개 조직, ${cell.headcount}명`}>
                          <Chip
                            icon={<Group sx={{ fontSize: 16 }} />}
                            label={cell.headcount}
                            size="small"
                            sx={{
                              backgroundColor: 'transparent',
                              color: 'inherit',
                              fontWeight: 'bold',
                              border: '1px solid',
                              borderColor: cell.headcount > 20 ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.2)'
                            }}
                          />
                        </Tooltip>
                      ) : (
                        <Typography variant="caption" color="textSecondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Summary Row */}
        <Box sx={{ p: 2, backgroundColor: '#f5f5f5', borderTop: '2px solid #ddd' }}>
          <Typography variant="subtitle2" gutterBottom>
            매트릭스 요약
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              label={`총 ${data.rows.length}개 기능`}
              size="small"
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`총 ${data.headers.length}명 리더`}
              size="small"
              color="secondary"
              variant="outlined"
            />
            <Chip
              label={`총 ${data.rows.reduce((acc, row) => 
                acc + row.cells.reduce((sum, cell) => sum + cell.headcount, 0), 0
              )}명`}
              size="small"
              color="success"
              variant="outlined"
            />
          </Box>
        </Box>
      </Paper>

      {/* Popover for cell details */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
      >
        {selectedCell && (
          <Box sx={{ p: 2, minWidth: 200 }}>
            <Typography variant="subtitle2" gutterBottom>
              {selectedCell.leader}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              총 {selectedCell.headcount}명 / {selectedCell.units.length}개 조직
            </Typography>
            <List dense>
              {selectedCell.units.map((unitId, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={unitId}
                    primaryTypographyProps={{
                      variant: 'body2'
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Popover>
    </Box>
  );
};

export default OrgMatrix;