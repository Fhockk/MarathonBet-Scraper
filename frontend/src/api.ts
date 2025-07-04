import { EventData  } from "./types"

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8080"

export const fetchEvents = async ({
      sport,
      keyword,
      hours,
  }: {
    sport?: string;
    keyword?: string;
    hours?: number;
}): Promise<EventData[]> => {
    const params = new URLSearchParams();
    if (sport) params.append("sport", sport);
    if (keyword) params.append("keyword", keyword);
    if (hours) params.append("hours", hours.toString());

    const response = await fetch(`${API_BASE}/v1/get_results?${params}`);
    if (!response.ok) throw new Error("Failed to fetch events");
    return response.json();
};
