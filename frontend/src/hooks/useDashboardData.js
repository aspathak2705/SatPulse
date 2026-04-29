import { startTransition, useEffect, useState } from "react";

import { fetchDashboardData } from "../services/api";

export function useDashboardData() {
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const payload = await fetchDashboardData();
        startTransition(() => setDataset(payload));
      } catch (fetchError) {
        setError(fetchError.message);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return { dataset, loading, error };
}
