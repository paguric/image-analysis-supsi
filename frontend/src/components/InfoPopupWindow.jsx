import * as React from 'react';
import Modal from '@mui/material/Modal';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import InfoIcon from '@mui/icons-material/Info';
import CloseIcon from '@mui/icons-material/Close';
import TextRetriever from '../components/TextRetriever';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

export default function InfoPopupWindow({ title, description }) {
    const [open, setOpen] = React.useState(false);

    return (
        <>
            <Tooltip title="Info">
                <IconButton
                    onClick={() => setOpen(true)}
                    size="small"
                    sx={{ color: 'text.secondary', '&:hover': { color: 'info.main' } }}
                >
                    <InfoIcon fontSize="small" />
                </IconButton>
            </Tooltip>

            <Modal open={open} onClose={() => setOpen(false)}>
                <Box sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: { xs: '90vw', sm: 480 },
                    bgcolor: 'background.paper',
                    border: '0.5px solid',
                    borderColor: 'divider',
                    borderRadius: 3,
                    overflow: 'hidden',
                    outline: 'none',
                }}>
                    {/* Header */}
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        px: 2,
                        py: 1.5,
                        borderBottom: '0.5px solid',
                        borderColor: 'divider',
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Box sx={{
                                width: 32, height: 32,
                                borderRadius: '50%',
                                bgcolor: 'info.50',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                <InfoIcon sx={{ fontSize: 16, color: 'info.main' }} />
                            </Box>
                            <Typography variant="body1" fontWeight={500}>
                                <TextRetriever label={title} />
                            </Typography>
                        </Box>
                        <IconButton size="small" onClick={() => setOpen(false)}>
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </Box>

                    {/* Body */}
                    <Box sx={{ px: 2.5, py: 2, fontSize: 14, color: 'text.secondary', lineHeight: 1.7,
                        '& p': { mt: 0, mb: 0.75 },
                        '& ul, & ol': { mt: 0.25, mb: 0.75, pl: 2.5 },
                        '& li': { mb: 0.25 },
                        '& strong': { color: 'text.primary', fontWeight: 500 },
                    }}>
                        <TextRetriever label={description} />
                    </Box>
                </Box>
            </Modal>
        </>
    );
}