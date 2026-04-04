import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'
import { useThemeMode } from '../context/ThemeContext'

export default function DarkModeToggle() {
    const { dark, toggle } = useThemeMode()

    return (
        <Tooltip title={dark ? 'Light mode' : 'Dark mode'}>
            <IconButton
                onClick={toggle}
                sx={{ position: 'fixed', top: 0, left: 6, zIndex: 9999 }}
            >
                {dark ? '☀️' : '🌙'}
            </IconButton>
        </Tooltip>
    )
}