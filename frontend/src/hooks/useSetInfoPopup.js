import { useEffect } from 'react'
import { useInfoPopup } from '../context/ThemeContext'

export function useSetInfoPopup(title, description) {
    const { setInfoProps } = useInfoPopup()

    useEffect(() => {
        setInfoProps({ title, description })
        return () => setInfoProps(null)
    }, [title, description])
}