import { createContext, useContext, useState } from 'react'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const ThemeContext = createContext(null)
const InfoContext = createContext(null)

export function useThemeMode() {
    return useContext(ThemeContext)
}

export function useInfoPopup() {
    return useContext(InfoContext)
}

export function AppThemeProvider({ children }) {
    const [dark, setDark] = useState(false)
    const [infoProps, setInfoProps] = useState(null) // { title, description }

    const toggle = () => {
        setDark(prev => !prev)
        document.documentElement.classList.toggle('dark')
    }

    const muiTheme = createTheme({
        palette: { mode: dark ? 'dark' : 'light' }
    })

    return (
        <ThemeContext.Provider value={{ dark, toggle }}>
            <InfoContext.Provider value={{ infoProps, setInfoProps }}>
                <ThemeProvider theme={muiTheme}>
                    <CssBaseline />
                    {children}
                </ThemeProvider>
            </InfoContext.Provider>
        </ThemeContext.Provider>
    )
}