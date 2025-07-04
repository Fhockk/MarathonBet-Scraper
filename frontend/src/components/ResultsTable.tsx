import React from "react";
import { EventData } from "../types";

interface Props {
    events: EventData[];
}

const formatTimeUTC = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
    });
};


const ResultsTable: React.FC<Props> = ({ events }) => {
    const groupedData: Record<string, Record<string, EventData[]>> = {};

    events.forEach((event) => {
        const { sport, metadata } = event;
        const { competition_name } = metadata;
        if (!groupedData[sport]) groupedData[sport] = {};
        if (!groupedData[sport][competition_name]) groupedData[sport][competition_name] = [];
        groupedData[sport][competition_name].push(event);
    });

    return (
        <div style={{ padding: "1rem" }}>
            {Object.entries(groupedData).map(([sport, competitions]) => (
                <div key={sport} style={{ marginBottom: "2rem" }}>
                    <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#003366" }}>{sport}</h2>
                    {Object.entries(competitions).map(([competition, events]) => (
                        <div key={competition} style={{ marginBottom: "1rem" }}>
                            <div
                                style={{
                                    backgroundColor: "#e0eaff",
                                    fontWeight: "bold",
                                    padding: "8px 12px",
                                    marginTop: "1rem",
                                }}
                            >
                                {competition}
                            </div>
                            <table style={{ width: "100%", borderCollapse: "collapse" }}>
                                <tbody>
                                {events.map((event) => (
                                    <tr key={event.event_id} style={{ borderBottom: "1px solid #ddd" }}>
                                        <td style={{ padding: "6px 12px", width: "50%" }}>
                                            {event.metadata.home_team} vs {event.metadata.away_team}
                                        </td>
                                        <td style={{ padding: "6px 12px", width: "25%", color: "#900" }}>
                                            {event.state?.scores?.map((s, idx) => (
                                                <div key={idx}>
                                                    {s.label && <b>{s.label}: </b>}
                                                    {s.value}
                                                </div>
                                            )) || "-"}
                                        </td>
                                        <td
                                            style={{
                                                padding: "6px 12px",
                                                width: "15%",
                                                textAlign: "right",
                                                color: "#555",
                                            }}
                                        >
                                            {formatTimeUTC(event.metadata.start_time)}
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
};

export default ResultsTable;
