/**
 * Organization Node Card Component for React Flow
 */
import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Avatar,
  Tooltip,
  Stack,
  Divider
} from '@mui/material';
import {
  Business,
  Person,
  Group,
  Functions
} from '@mui/icons-material';

interface OrgNodeData {
  id: string;
  company: string;
  name: string;
  function?: string;
  headcount: number;
  leader?: {
    title: string;
    rank: string;
    name: string;
    age?: number;
  };
  members?: Array<{
    grade: string;
    count: number;
  }>;
  sandboxMode?: boolean;
  onUpdate?: (unitId: string, newReportsTo: string | null) => void;
}

const OrgNodeCard: React.FC<NodeProps<OrgNodeData>> = ({ data, selected }) => {
  // Company color scheme
  const getCompanyColor = (company: string) => {
    switch (company) {
      case 'OK저축은행':
        return { bg: '#E6F2FF', border: '#4169E1', text: '#1e3a8a' };
      case 'OK캐피탈':
        return { bg: '#FFE6E6', border: '#FF6347', text: '#991b1b' };
      case 'OK금융그룹':
        return { bg: '#F0FDF4', border: '#22C55E', text: '#166534' };
      default:
        return { bg: '#F5F5F5', border: '#888888', text: '#424242' };
    }
  };

  const colors = getCompanyColor(data.company);

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: colors.border,
          width: 12,
          height: 12,
          border: '2px solid white',
        }}
      />
      
      <Card
        sx={{
          width: 300,
          minHeight: 150,
          backgroundColor: colors.bg,
          border: `2px solid ${selected ? colors.border : 'transparent'}`,
          borderRadius: 2,
          boxShadow: selected ? 4 : 2,
          cursor: data.sandboxMode ? 'move' : 'default',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-2px)',
          },
        }}
      >
        <CardContent sx={{ p: 2 }}>
          {/* Header with Company Badge and Name */}
          <Stack direction="row" spacing={1} alignItems="center" mb={1}>
            <Chip
              icon={<Business sx={{ fontSize: 14 }} />}
              label={data.company}
              size="small"
              sx={{
                backgroundColor: colors.border,
                color: 'white',
                fontWeight: 'bold',
                fontSize: 11,
              }}
            />
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 'bold',
                color: colors.text,
                flexGrow: 1,
              }}
              noWrap
            >
              {data.name}
            </Typography>
          </Stack>

          {/* Function */}
          {data.function && (
            <Stack direction="row" spacing={0.5} alignItems="center" mb={1}>
              <Functions sx={{ fontSize: 14, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {data.function}
              </Typography>
            </Stack>
          )}

          <Divider sx={{ my: 1 }} />

          {/* Leader Information */}
          {data.leader?.name && (
            <Box sx={{ mb: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Avatar
                  sx={{
                    width: 28,
                    height: 28,
                    fontSize: 12,
                    backgroundColor: colors.border,
                  }}
                >
                  {data.leader.name[0]}
                </Avatar>
                <Box>
                  <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                    {data.leader.title} · {data.leader.rank}
                  </Typography>
                  <Typography variant="body2">
                    {data.leader.name}
                    {data.leader.age && (
                      <Typography
                        component="span"
                        variant="caption"
                        color="text.secondary"
                        sx={{ ml: 0.5 }}
                      >
                        ({data.leader.age}세)
                      </Typography>
                    )}
                  </Typography>
                </Box>
              </Stack>
            </Box>
          )}

          {/* Members Composition */}
          {data.members && data.members.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                {data.members.map((member, index) => (
                  <Chip
                    key={index}
                    label={`${member.grade} ${member.count}`}
                    size="small"
                    variant="outlined"
                    sx={{
                      fontSize: 10,
                      height: 20,
                      '& .MuiChip-label': { px: 1 },
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {/* Total Headcount */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mt: 1,
              pt: 1,
              borderTop: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Stack direction="row" spacing={0.5} alignItems="center">
              <Group sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                총원
              </Typography>
            </Stack>
            <Tooltip title="총 인원수">
              <Chip
                label={`${data.headcount}명`}
                size="small"
                sx={{
                  backgroundColor: colors.border,
                  color: 'white',
                  fontWeight: 'bold',
                }}
              />
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: colors.border,
          width: 12,
          height: 12,
          border: '2px solid white',
        }}
      />
    </>
  );
};

export default memo(OrgNodeCard);