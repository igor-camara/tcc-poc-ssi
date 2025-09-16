import { ref, onMounted, watch } from 'vue'

const isDarkMode = ref(false)

export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    updateTheme()
  }

  const setTheme = (theme) => {
    isDarkMode.value = theme === 'dark'
    updateTheme()
  }

  const updateTheme = () => {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const initTheme = () => {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem('theme')
    
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // Use system preference as fallback
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    
    updateTheme()
  }

  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleSystemThemeChange = (e) => {
    if (!localStorage.getItem('theme')) {
      isDarkMode.value = e.matches
      updateTheme()
    }
  }

  onMounted(() => {
    initTheme()
    mediaQuery.addEventListener('change', handleSystemThemeChange)
  })

  // Watch for changes to update the theme
  watch(isDarkMode, () => {
    updateTheme()
  })

  return {
    isDarkMode,
    toggleTheme,
    setTheme,
    initTheme
  }
}