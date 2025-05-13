export const getApiUrl = () => {
    const url = import.meta.env.VITE_API_URL || 'http://localhost:7860'
    console.log("📦 VITE_API_URL (runtime, in env.js):", import.meta.env.VITE_API_URL, "| Used URL:", url)
    return url
}