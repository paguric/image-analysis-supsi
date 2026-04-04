import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import { useThemeMode } from '../context/ThemeContext'

export default function DarkModeToggle() {
    const { dark, toggle } = useThemeMode()

    return (
        <Tooltip title={dark ? 'Light mode' : 'Dark mode'}>
            <IconButton
                onClick={toggle}
                sx={{ 
                    position: 'fixed', 
                    top: 7, 
                    left: 12, 
                    zIndex: 9999,
                    color: 'text.primary',
                }}
            >
                {dark ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
        </Tooltip>
    )
}