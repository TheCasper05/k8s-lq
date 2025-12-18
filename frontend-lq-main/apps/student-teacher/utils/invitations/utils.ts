/**
 * Downloads the invitation template CSV file with headers
 */
export function downloadInvitationTemplate(): void {
  const headers = "Email, Workspace Slug, Role, Classroom Names, Welcome Message";
  const blob = new Blob([headers], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", "invitation_template.csv");
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

/**
 * Converts a file to base64 string
 * @param file - The file to convert
 * @returns Promise that resolves to the base64 string
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      if (typeof reader.result === "string") {
        // Remove the data URL prefix (e.g., "data:text/csv;base64,")
        const base64 = reader.result.split(",")[1];
        resolve(base64);
      } else {
        reject(new Error("Failed to read file as base64"));
      }
    };
    reader.onerror = (error) => reject(error);
  });
}
