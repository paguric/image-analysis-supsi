export const handleExport = async () => {
    try {
        const result = await exportToCSV();
        if (result.success) {
            alert(`File salvato in: ${result.path}`);
        }
    } catch (err) {
        console.error("Export failed:", err);
    }
};

