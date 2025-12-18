export interface Country {
  label: string;
  value: string;
}

export const useCountries = () => {
  const countries = useState<Country[]>("countries", () => []);
  const loading = useState<boolean>("countries-loading", () => false);
  const error = useState<string | null>("countries-error", () => null);

  /**
   * Fetch countries from API if not already loaded
   */
  const fetchCountries = async () => {
    // If we already have data, don't fetch again
    if (countries.value.length > 0) return;

    loading.value = true;
    error.value = null;

    try {
      const response = await fetch("https://restcountries.com/v3.1/all?fields=name,cca2");
      if (!response.ok) throw new Error("Failed to fetch countries");

      const data = await response.json();

      countries.value = data
        .map((country: { name: { common: string }; cca2: string }) => ({
          label: country.name.common,
          value: country.cca2.toLowerCase(),
        }))
        .sort((a: Country, b: Country) => a.label.localeCompare(b.label));
    } catch (err: unknown) {
      console.error("Failed to fetch countries:", err);
      error.value = err instanceof Error ? err.message : "Unknown error";

      // Fallback to basic list if API fails
      countries.value = [
        { value: "co", label: "Colombia" },
        { value: "us", label: "United States" },
        { value: "es", label: "Spain" },
        { value: "mx", label: "Mexico" },
      ];
    } finally {
      loading.value = false;
    }
  };

  return {
    countries,
    loading,
    error,
    fetchCountries,
  };
};
