import { createContext, useContext, useState } from 'react'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const ThemeContext = createContext(null)

export function useThemeMode() {
    return useContext(ThemeContext)
}

export function AppThemeProvider({ children }) {
    const [dark, setDark] = useState(false)

    const toggle = () => {
        setDark(prev => !prev)
        document.documentElement.classList.toggle('dark')
    }

    const muiTheme = createTheme({
        palette: { mode: dark ? 'dark' : 'light' }
    })

    return (
        <ThemeContext.Provider value={{ dark, toggle }}>
            <ThemeProvider theme={muiTheme}>
                <CssBaseline />
                {children}
            </ThemeProvider>
        </ThemeContext.Provider>
    )
}