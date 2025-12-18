export const useStudentColors = () => {
  const getLevelSeverity = (level: string): "danger" | "warn" | "info" | "success" | "secondary" => {
    const severityMap: Record<string, "danger" | "warn" | "info" | "success" | "secondary"> = {
      A1: "danger",
      A2: "warn",
      B1: "info",
      B2: "info",
      C1: "success",
      C2: "success",
    };
    return severityMap[level] || "secondary";
  };

  const getProgressSeverity = (progress: number): "danger" | "warn" | "success" => {
    if (progress < 30) return "danger";
    if (progress < 60) return "warn";
    return "success";
  };

  return {
    getLevelSeverity,
    getProgressSeverity,
  };
};
